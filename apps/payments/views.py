"""
Payment views for subscription and transaction management
"""
import json
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from infrastructure.razorpay_client import RazorpayClient

from .models import Payment, Subscription, SubscriptionPlan


def _subscription_end_date(billing_cycle):
    if billing_cycle == 'MONTHLY':
        return timezone.now() + timedelta(days=30)
    return timezone.now() + timedelta(days=365)


@transaction.atomic
def activate_subscription_for_payment(payment):
    """
    Activate one subscription record per captured payment and retire older active plans.
    This keeps checkout verification and webhook recovery idempotent.
    """
    plan_type = payment.metadata.get('plan_type')
    billing_cycle = payment.metadata.get('billing_cycle')

    if plan_type not in dict(Subscription.PLAN_TYPES):
        raise ValueError('Payment metadata is missing a valid plan type')
    if billing_cycle not in dict(Subscription.BILLING_CYCLE):
        raise ValueError('Payment metadata is missing a valid billing cycle')

    now = timezone.now()
    end_date = _subscription_end_date(billing_cycle)

    Subscription.objects.filter(
        user=payment.user,
        status='ACTIVE',
    ).exclude(payment=payment).update(
        status='CANCELLED',
        auto_renew=False,
        end_date=now,
    )

    existing_subscriptions = list(
        Subscription.objects.select_for_update().filter(payment=payment).order_by('-created_at')
    )
    subscription = existing_subscriptions[0] if existing_subscriptions else None

    if subscription is None:
        subscription = Subscription.objects.create(
            user=payment.user,
            plan_type=plan_type,
            billing_cycle=billing_cycle,
            amount=payment.amount,
            start_date=now,
            end_date=end_date,
            status='ACTIVE',
            payment=payment,
        )
    else:
        subscription.user = payment.user
        subscription.plan_type = plan_type
        subscription.billing_cycle = billing_cycle
        subscription.amount = payment.amount
        subscription.start_date = now
        subscription.end_date = end_date
        subscription.status = 'ACTIVE'
        subscription.payment = payment
        subscription.save()

        duplicate_ids = [item.pk for item in existing_subscriptions[1:]]
        if duplicate_ids:
            Subscription.objects.filter(pk__in=duplicate_ids).update(
                status='CANCELLED',
                auto_renew=False,
                end_date=now,
            )

    return subscription


@login_required
def membership_view(request):
    """Display membership plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('display_order')
    context = {
        'plans': plans,
        'current_subscription': request.user.subscription,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'payments/membership.html', context)


@login_required
def create_subscription_order(request):
    """Create Razorpay order for subscription"""
    if request.method == 'POST':
        plan_type = request.POST.get('plan_type')
        billing_cycle = request.POST.get('billing_cycle')

        if billing_cycle not in dict(Subscription.BILLING_CYCLE):
            return JsonResponse({'error': 'Invalid billing cycle'}, status=400)

        try:
            plan = SubscriptionPlan.objects.get(plan_type=plan_type, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return JsonResponse({'error': 'Invalid plan'}, status=400)

        amount = plan.price_monthly if billing_cycle == 'MONTHLY' else plan.price_yearly

        receipt = f'sub_{request.user.id}_{int(timezone.now().timestamp())}'
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            description=f'{plan.name} - {billing_cycle}',
            receipt=receipt,
            metadata={
                'plan_type': plan_type,
                'billing_cycle': billing_cycle,
                'plan_name': plan.name,
            }
        )

        razorpay_service = RazorpayClient()
        try:
            order = razorpay_service.create_order(
                amount=amount,
                receipt=receipt,
                notes={
                    'user_id': request.user.id,
                    'plan_type': plan_type,
                    'billing_cycle': billing_cycle,
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
                    'contact': request.user.mobile or '',
                }
            })
        except Exception as exc:
            payment.status = 'FAILED'
            payment.save()
            return JsonResponse({'error': str(exc)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def verify_payment(request):
    """Verify payment and activate subscription"""
    if request.method == 'POST':
        data = json.loads(request.body)

        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)

        if payment.user_id != request.user.id:
            return JsonResponse({'error': 'Payment does not belong to the current user'}, status=403)

        existing_subscription = Subscription.objects.filter(payment=payment).order_by('-created_at').first()
        if payment.status == 'CAPTURED' and existing_subscription and existing_subscription.is_active():
            return JsonResponse({
                'success': True,
                'message': 'Payment already verified.',
                'subscription_id': existing_subscription.id,
            })

        razorpay_service = RazorpayClient()
        if razorpay_service.verify_payment_signature(
            razorpay_order_id, razorpay_payment_id, razorpay_signature
        ):
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'CAPTURED'
            payment.paid_at = timezone.now()
            payment.save()

            try:
                payment_details = razorpay_service.fetch_payment(razorpay_payment_id)
                payment.payment_method = payment_details.get('method', '').upper() or None
                payment.save()
            except Exception:
                pass

            try:
                subscription = activate_subscription_for_payment(payment)
            except ValueError as exc:
                return JsonResponse({'error': str(exc)}, status=400)

            return JsonResponse({
                'success': True,
                'message': 'Payment successful! Your subscription is now active.',
                'subscription_id': subscription.id,
            })

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
        if not razorpay_service.verify_webhook_signature(webhook_body, webhook_signature):
            return HttpResponse('Invalid signature', status=400)

        data = json.loads(webhook_body)
        event = data.get('event')
        payload = data.get('payload', {}).get('payment', {}).get('entity', {})

        if event == 'payment.captured':
            payment_id = payload.get('id')
            order_id = payload.get('order_id')

            try:
                payment = Payment.objects.get(razorpay_order_id=order_id)
                payment.razorpay_payment_id = payment_id
                payment.status = 'CAPTURED'
                payment.paid_at = timezone.now()
                payment.save()
                activate_subscription_for_payment(payment)
            except Payment.DoesNotExist:
                pass
            except ValueError:
                return HttpResponse('Invalid payment metadata', status=400)

        elif event == 'payment.failed':
            order_id = payload.get('order_id')

            try:
                payment = Payment.objects.get(razorpay_order_id=order_id)
                payment.status = 'FAILED'
                payment.save()
            except Payment.DoesNotExist:
                pass

        return HttpResponse('OK', status=200)

    return HttpResponse('Method not allowed', status=405)
