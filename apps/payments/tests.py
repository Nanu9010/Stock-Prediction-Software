import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.authentication.models import User
from apps.payments.models import Payment, Subscription, SubscriptionPlan


class PaymentFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='paid@example.com',
            password='StrongPass123!',
            first_name='Paid',
            last_name='User',
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='StrongPass123!',
            first_name='Other',
            last_name='User',
        )
        SubscriptionPlan.objects.create(
            name='PRO',
            plan_type='PRO',
            price_monthly=999,
            price_yearly=9990,
            features=['Unlimited research calls'],
            max_calls_per_month=-1,
            display_order=1,
            is_active=True,
        )

    @patch('apps.payments.views.RazorpayClient')
    def test_verify_payment_activates_subscription_once(self, razorpay_client_cls):
        payment = Payment.objects.create(
            user=self.user,
            razorpay_order_id='order_123',
            amount=999,
            description='PRO - MONTHLY',
            receipt='sub_1',
            metadata={'plan_type': 'PRO', 'billing_cycle': 'MONTHLY'},
        )
        Subscription.objects.create(
            user=self.user,
            plan_type='BASIC',
            billing_cycle='MONTHLY',
            amount=499,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30),
            status='ACTIVE',
        )

        client_instance = razorpay_client_cls.return_value
        client_instance.verify_payment_signature.return_value = True
        client_instance.fetch_payment.return_value = {'method': 'upi'}

        self.client.login(email='paid@example.com', password='StrongPass123!')
        payload = {
            'razorpay_order_id': 'order_123',
            'razorpay_payment_id': 'pay_123',
            'razorpay_signature': 'sig_123',
        }

        response = self.client.post(
            reverse('payments:verify_payment'),
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'CAPTURED')
        self.assertEqual(payment.payment_method, 'UPI')

        subscriptions = Subscription.objects.filter(user=self.user).order_by('-created_at')
        self.assertEqual(subscriptions.count(), 2)
        self.assertEqual(subscriptions.first().payment_id, payment.id)
        self.assertEqual(subscriptions.first().status, 'ACTIVE')
        self.assertEqual(subscriptions.first().plan_type, 'PRO')
        self.assertEqual(subscriptions.last().status, 'CANCELLED')

        second_response = self.client.post(
            reverse('payments:verify_payment'),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(Subscription.objects.filter(payment=payment).count(), 1)

    @patch('apps.payments.views.RazorpayClient')
    def test_verify_payment_rejects_different_user(self, razorpay_client_cls):
        Payment.objects.create(
            user=self.user,
            razorpay_order_id='order_456',
            amount=999,
            description='PRO - MONTHLY',
            receipt='sub_2',
            metadata={'plan_type': 'PRO', 'billing_cycle': 'MONTHLY'},
        )

        client_instance = razorpay_client_cls.return_value
        client_instance.verify_payment_signature.return_value = True

        self.client.login(email='other@example.com', password='StrongPass123!')
        payload = {
            'razorpay_order_id': 'order_456',
            'razorpay_payment_id': 'pay_456',
            'razorpay_signature': 'sig_456',
        }

        response = self.client.post(
            reverse('payments:verify_payment'),
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Subscription.objects.filter(payment__razorpay_order_id='order_456').count(), 0)
