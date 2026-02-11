
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.research_calls.forms import ResearchCallForm
from apps.brokers.models import Broker

class Command(BaseCommand):
    help = 'Verify Research Call creation logic'

    def handle(self, *args, **options):
        self.stdout.write("Verifying Call Creation Logic...")
        User = get_user_model()
        
        # Create or get a test user
        user, _ = User.objects.get_or_create(
            email='test_analyst@example.com', 
            defaults={'role': 'ANALYST', 'first_name': 'Test', 'mobile': '1234567890'}
        )
        if not user.password:
            user.set_password('pass')
            user.save()
            
        # Create or get a test broker
        broker, _ = Broker.objects.get_or_create(name='Test Broker', defaults={'slug': 'test-broker'})

        # Test Case 1: Valid Buy Call
        self.stdout.write("\n--- Test Case 1: Valid Buy Call ---")
        data = {
            'symbol': 'RELIANCE',
            'exchange': 'NSE',
            'action': 'BUY',
            'call_type': 'INTRADAY',
            'instrument_type': 'EQUITY',
            'entry_price': 2500,
            'target_1': 2550,
            'stop_loss': 2450,
            'timeframe_days': 1,
            'broker': broker.id,
            'rationale': 'Strong buy signal',
        }
        form = ResearchCallForm(data=data)
        if form.is_valid():
            self.stdout.write("PASS: Form is valid")
            # Save without commit to set user
            call = form.save(commit=False)
            call.created_by = user
            call.save()
            self.stdout.write(f"PASS: Saved call: {call}")
        else:
            self.stdout.write(f"FAIL: Form errors: {form.errors}")

        # Test Case 2: Invalid Logic
        self.stdout.write("\n--- Test Case 2: Invalid Buy Call (Target < Entry) ---")
        data_invalid = data.copy()
        data_invalid['target_1'] = 2400 # Invalid for BUY
        form = ResearchCallForm(data=data_invalid)
        if not form.is_valid():
            self.stdout.write(f"PASS: Form correctly found errors: {form.errors}")
        else:
            self.stdout.write("FAIL: Form did not catch logic error!")

        self.stdout.write("\nVerification Complete.")
