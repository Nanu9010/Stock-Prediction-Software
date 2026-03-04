import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.market_data.models import ETF

def run():
    print("Deleting old ETFs...")
    ETF.objects.all().delete()
    print("Seeding new ETFs...")
    ETF.objects.bulk_create([
        ETF(name='Nippon India Nifty BeES', symbol='NIFTYBEES.NS', short_name='NIFTYBEES', category='Index', is_active=True, display_order=1),
        ETF(name='Nippon India Bank BeES', symbol='BANKBEES.NS', short_name='BANKBEES', category='Banking', is_active=True, display_order=2),
        ETF(name='Nippon India Gold BeES', symbol='GOLDBEES.NS', short_name='GOLDBEES', category='Gold', is_active=True, display_order=3),
        ETF(name='SBI ETF Nifty 50', symbol='SETFNIF50.NS', short_name='SETFNIF50', category='Index', is_active=True, display_order=4),
        ETF(name='Nippon India Junior BeES', symbol='JUNIORBEES.NS', short_name='JUNIORBEES', category='Index', is_active=True, display_order=5),
        ETF(name='Nippon India Silver ETF', symbol='SILVERBEES.NS', short_name='SILVERBEES', category='Silver', is_active=True, display_order=6),
        ETF(name='Nippon India Liquid BeES', symbol='LIQUIDBEES.NS', short_name='LIQUIDBEES', category='Liquid', is_active=True, display_order=7),
        ETF(name='ICICI Pru Bharat 22 ETF', symbol='ICICIB22.NS', short_name='ICICIB22', category='Thematic', is_active=True, display_order=8),
    ])
    print("Done!")

if __name__ == '__main__':
    run()
