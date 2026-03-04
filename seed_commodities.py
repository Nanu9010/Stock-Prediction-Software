import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.market_data.models import Commodity

def run():
    print("Deleting old commodities...")
    Commodity.objects.all().delete()
    print("Seeding new commodities...")
    Commodity.objects.bulk_create([
        Commodity(name='Gold', symbol='GC=F', unit='$/oz', icon='🥇', is_global=True, is_active=True, display_order=1), 
        Commodity(name='Silver', symbol='SI=F', unit='$/oz', icon='🥈', is_global=True, is_active=True, display_order=2), 
        Commodity(name='Crude Oil (WTI)', symbol='CL=F', unit='$/bbl', icon='🛢️', is_global=True, is_active=True, display_order=3), 
        Commodity(name='Crude Oil (Brent)', symbol='BZ=F', unit='$/bbl', icon='🛢️', is_global=True, is_active=True, display_order=4), 
        Commodity(name='Natural Gas', symbol='NG=F', unit='$/MMBtu', icon='🔥', is_global=True, is_active=True, display_order=5), 
        Commodity(name='Copper', symbol='HG=F', unit='$/lb', icon='🟤', is_global=True, is_active=True, display_order=6), 
        Commodity(name='Gold (10g)', symbol='GC=F', unit='₹', mcx_multiplier=0.322, icon='🥇', is_global=False, is_active=True, display_order=1), 
        Commodity(name='Silver (1kg)', symbol='SI=F', unit='₹', mcx_multiplier=26.5, icon='🥈', is_global=False, is_active=True, display_order=2), 
        Commodity(name='Crude Oil', symbol='CL=F', unit='$/bbl', mcx_multiplier=1, icon='🛢️', is_global=False, is_active=True, display_order=3), 
        Commodity(name='Natural Gas', symbol='NG=F', unit='₹/MMBtu', mcx_multiplier=83, icon='🔥', is_global=False, is_active=True, display_order=4)
    ])
    print("Done!")

if __name__ == '__main__':
    run()
