"""
Payment views for subscription and transaction management
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import json

from .models import Payment, Subscription, SubscriptionPlan
from infrastructure.razorpay_client import RazorpayClient


@login_required
def membership_view(request):
    """Display membership plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('display_order')
    
    # Get user's current subscription if any
    current_subscription = None
    if request.user.is_authenticated:
        current_subscription = Subscription.objects.filter(
            user=request.user,
            status='ACTIVE'
        ).first()
    
    context = {
        'plans': plans,
        'current_subscription': current_subscription,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'payments/membership.html', context)


@login_required
def create_subscription_order(request):
    """Create Razorpay order for subscription"""
    if request.method == 'POST':
        plan_type = request.POST.get('plan_type')
        billing_cycle = request.POST.get('billing_cycle')
        
        # Get plan
        try:
            plan = SubscriptionPlan.objects.get(plan_type=plan_type)
        except SubscriptionPlan.DoesNotExist:
            return JsonResponse({'error': 'Invalid plan'}, status=400)
        
        # Calculate amount
        amount = plan.price_monthly if billing_cycle == 'MONTHLY' else plan.price_yearly
        
        # Create payment record
        receipt = f'sub_{request.user.id}_{int(timezone.now().timestamp())}'
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            description=f'{plan.name} - {billing_cycle}',
            receipt=receipt,
            metadata={
                'plan_type': plan_type,
                'billing_cycle': billing_cycle
            }
        )
        
        # Create Razorpay order
        razorpay_service = RazorpayClient()
        try:
            order = razorpay_service.create_order(
                amount=amount,
                receipt=receipt,
                notes={
                    'user_id': request.user.id,
                    'plan_type': plan_type,
                    'billing_cycle': billing_cycle
                }
            )
            
            payment.razorpay_order_id = order['id']
            payment.save()
            
            return JsonResponse({
                'order_id': order['id'],
                'amount': amount,
                'currency': 'INR',
                'key': settings.RAZORPAY_KEY_ID,
                'name': 'StockPro',
                'description': payment.description,
                'prefill': {
                    'name': request.user.get_full_name(),
                    'email': request.user.email,
                    'contact': request.user.mobile or ''
                }
            })
        except Exception as e:
            payment.status = 'FAILED'
            payment.save()
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def verify_payment(request):
    """Verify payment and activate subscription"""
    if request.method == 'POST':
        data = json.loads(request.body)
        
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        
        # Get payment record
        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)
        
        # Verify signature
        razorpay_service = RazorpayClient()
        if razorpay_service.verify_payment_signature(
            razorpay_order_id, razorpay_payment_id, razorpay_signature
        ):
            # Update payment
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'CAPTURED'
            payment.paid_at = timezone.now()
            payment.save()
            
            # Fetch payment details
            try:
                payment_details = razorpay_service.fetch_payment(razorpay_payment_id)
                payment.payment_method = payment_details.get('method', '').upper()
                payment.save()
            except:
                pass
            
            # Create subscription
            plan_type = payment.metadata['plan_type']
            billing_cycle = payment.metadata['billing_cycle']
            
            # Calculate end date
            if billing_cycle == 'MONTHLY':
                end_date = timezone.now() + timedelta(days=30)
            else:
                end_date = timezone.now() + timedelta(days=365)
            
            subscription = Subscription.objects.create(
                user=request.user,
                plan_type=plan_type,
                billing_cycle=billing_cycle,
                amount=payment.amount,
                start_date=timezone.now(),
                end_date=end_date,
                status='ACTIVE',
                payment=payment
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Payment successful! Your subscription is now active.',
                'subscription_id': subscription.id
            })
        else:
            payment.status = 'FAILED'
            payment.save()
            return JsonResponse({'error': 'Payment verification failed'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def razorpay_webhook(request):
    """Handle Razorpay webhooks"""
    if request.method == 'POST':
        webhook_body = request.body
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        
        razorpay_service = RazorpayClient()
        
        # Verify webhook signature
        if not razorpay_service.verify_webhook_signature(webhook_body, webhook_signature):
            return HttpResponse('Invalid signature', status=400)
        
        # Parse webhook data
        data = json.loads(webhook_body)
        event = data.get('event')
        payload = data.get('payload', {}).get('payment', {}).get('entity', {})
        
        # Handle different events
        if event == 'payment.captured':
            # Payment captured successfully
            payment_id = payload.get('id')
            order_id = payload.get('order_id')
            
            try:
                payment = Payment.objects.get(razorpay_order_id=order_id)
                payment.razorpay_payment_id = payment_id
                payment.status = 'CAPTURED'
                payment.paid_at = timezone.now()
                payment.save()
            except Payment.DoesNotExist:
                pass
        
        elif event == 'payment.failed':
            # Payment failed
            order_id = payload.get('order_id')
            
            try:
                payment = Payment.objects.get(razorpay_order_id=order_id)
                payment.status = 'FAILED'
                payment.save()
            except Payment.DoesNotExist:
                pass
        
        return HttpResponse('OK', status=200)
    
    return HttpResponse('Method not allowed', status=405)
