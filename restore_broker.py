
import os
import sys
import django

# Setup Django
sys.path.append(r'c:\Users\karti\OneDrive\Desktop\Stock Prediction System')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.brokers.models import Broker

def check_and_create_broker():
    count = Broker.objects.count()
    print(f"Broker count: {count}")
    
    if count == 0:
        print("Creating default broker...")
        try:
            Broker.objects.create(
                name='Zerodha',
                slug='zerodha',
                description='Leading discount broker in India',
                overall_accuracy=85.5,
                is_active=True
            )
            print("Broker created: Zerodha")
        except Exception as e:
            print(f"Error creating broker: {e}")

if __name__ == "__main__":
    check_and_create_broker()
