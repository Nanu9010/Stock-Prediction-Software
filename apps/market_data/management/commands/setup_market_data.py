"""
Django management command to populate initial market data
"""
from django.core.management.base import BaseCommand
from apps.market_data.models import PopularStock
from apps.market_data.services import update_index_prices, update_popular_stocks


class Command(BaseCommand):
    help = 'Populate initial market data (indices and popular stocks)'

    def handle(self, *args, **options):
        self.stdout.write('Setting up popular stocks...')
        
        # Popular Indian stocks
        popular_stocks = [
            ('RELIANCE', 'Reliance Industries Ltd'),
            ('TCS', 'Tata Consultancy Services'),
            ('HDFCBANK', 'HDFC Bank Ltd'),
            ('INFY', 'Infosys Ltd'),
            ('ICICIBANK', 'ICICI Bank Ltd'),
            ('HINDUNILVR', 'Hindustan Unilever Ltd'),
            ('SBIN', 'State Bank of India'),
            ('BHARTIARTL', 'Bharti Airtel Ltd'),
            ('ITC', 'ITC Ltd'),
            ('KOTAKBANK', 'Kotak Mahindra Bank'),
            ('LT', 'Larsen & Toubro Ltd'),
            ('AXISBANK', 'Axis Bank Ltd'),
            ('ASIANPAINT', 'Asian Paints Ltd'),
            ('MARUTI', 'Maruti Suzuki India Ltd'),
            ('TITAN', 'Titan Company Ltd'),
            ('BAJFINANCE', 'Bajaj Finance Ltd'),
            ('WIPRO', 'Wipro Ltd'),
            ('ULTRACEMCO', 'UltraTech Cement Ltd'),
            ('NESTLEIND', 'Nestle India Ltd'),
            ('HCLTECH', 'HCL Technologies Ltd'),
        ]
        
        created_count = 0
        for i, (symbol, name) in enumerate(popular_stocks):
            stock, created = PopularStock.objects.get_or_create(
                symbol=symbol,
                defaults={
                    'company_name': name,
                    'display_order': i,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created: {symbol} - {name}')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_count} popular stocks'))
        
        # Update market indices
        self.stdout.write('\nUpdating market indices...')
        indices_updated = update_index_prices()
        self.stdout.write(self.style.SUCCESS(f'✓ Updated {indices_updated} market indices'))
        
        # Update popular stock prices
        self.stdout.write('\nUpdating popular stock prices...')
        stocks_updated = update_popular_stocks()
        self.stdout.write(self.style.SUCCESS(f'✓ Updated {stocks_updated} stock prices'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Market data setup complete!'))
        self.stdout.write('\nYou can now:')
        self.stdout.write('  - View indices at: /market/indices/')
        self.stdout.write('  - View stocks at: /market/stocks/')
        self.stdout.write('  - Access API at: /market/api/?type=indices')
