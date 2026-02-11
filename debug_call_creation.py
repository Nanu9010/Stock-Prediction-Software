
import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.append(r'c:\Users\karti\OneDrive\Desktop\Stock Prediction System')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.research_calls.models import ResearchCall
from apps.brokers.models import Broker
from django.contrib.auth import get_user_model

User = get_user_model()

def debug_create_call():
    print("Attempting to create a ResearchCall...")
    
    try:
        # Get dependencies
        broker = Broker.objects.first()
        user = User.objects.first()
        
        if not broker:
            print("No broker found!")
            return
        if not user:
            print("No user found!")
            return
            
        print(f"Using Broker: {broker.name}")
        print(f"Using User: {user.email}")
        
        # Create Call
        call = ResearchCall(
            symbol="RELIANCE",
            exchange="NSE",
            call_type="INTRADAY",
            action="BUY",
            entry_price=Decimal("2500"),
            target_1=Decimal("2550"),
            stop_loss=Decimal("2450"),
            broker=broker,
            created_by=user,
            status="DRAFT"
        )
        
        # explicit cleaning to test validation
        call.full_clean()
        call.save()
        
        print(f"Successfully created Call ID: {call.id}")
        
    except Exception as e:
        print(f"FAILED to create call: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_create_call()
