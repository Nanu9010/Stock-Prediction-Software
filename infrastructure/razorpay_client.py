"""
Razorpay service wrapper for payment processing
"""
import razorpay
import hmac
import hashlib
from django.conf import settings
from django.utils import timezone


class RazorpayClient:
    """Service for Razorpay payment integration"""
    
    def __init__(self):
        self.client = razorpay.Client(auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        ))
    
    def create_order(self, amount, currency='INR', receipt=None, notes=None):
        """Create a Razorpay order"""
        data = {
            'amount': int(amount * 100),  # Amount in paise
            'currency': currency,
            'receipt': receipt or f'order_{int(timezone.now().timestamp())}',
            'notes': notes or {}
        }
        
        try:
            order = self.client.order.create(data=data)
            return order
        except Exception as e:
            raise Exception(f"Failed to create order: {str(e)}")
    
    def verify_payment_signature(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """Verify payment signature for security"""
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except:
            return False
    
    def capture_payment(self, payment_id, amount):
        """Capture an authorized payment"""
        try:
            payment = self.client.payment.capture(payment_id, int(amount * 100))
            return payment
        except Exception as e:
            raise Exception(f"Failed to capture payment: {str(e)}")
    
    def refund_payment(self, payment_id, amount=None):
        """Refund a payment"""
        try:
            data = {}
            if amount:
                data['amount'] = int(amount * 100)
            
            refund = self.client.payment.refund(payment_id, data)
            return refund
        except Exception as e:
            raise Exception(f"Failed to refund payment: {str(e)}")
    
    def fetch_payment(self, payment_id):
        """Fetch payment details"""
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            raise Exception(f"Failed to fetch payment: {str(e)}")
    
    def verify_webhook_signature(self, webhook_body, webhook_signature):
        """Verify webhook signature"""
        try:
            expected_signature = hmac.new(
                settings.RAZORPAY_WEBHOOK_SECRET.encode('utf-8'),
                webhook_body,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, webhook_signature)
        except:
            return False
