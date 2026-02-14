from django.core.management.base import BaseCommand
from django.utils import timezone
from services.market_hero_service import (
    get_today_top10_gainers,
    get_today_top10_losers,
    get_weekly_top_gainers,
    get_weekly_top_losers,
    get_market_indices
)
from services.sip_mf_etf_service import get_top_etfs
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetches live market data and populates the cache to speed up website load times.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS(f'[{timezone.now()}] Starting market data update...'))

        try:
            # 1. Market Indices
            self.stdout.write('Fetching Market Indices...')
            get_market_indices(force_refresh=True)
            self.stdout.write(self.style.SUCCESS('OK'))

            # 2. Top Gainers/Losers (Today)
            self.stdout.write('Fetching Today Top 10 Gainers...')
            get_today_top10_gainers(force_refresh=True)
            self.stdout.write(self.style.SUCCESS('OK'))

            self.stdout.write('Fetching Today Top 10 Losers...')
            get_today_top10_losers(force_refresh=True)
            self.stdout.write(self.style.SUCCESS('OK'))

            # 3. Top Gainers/Losers (Weekly)
            self.stdout.write('Fetching Weekly Top Gainers...')
            get_weekly_top_gainers(force_refresh=True)
            self.stdout.write(self.style.SUCCESS('OK'))

            self.stdout.write('Fetching Weekly Top Losers...')
            get_weekly_top_losers(force_refresh=True)
            self.stdout.write(self.style.SUCCESS('OK'))
            
            # 4. ETFs
            self.stdout.write('Fetching ETF Data...')
            get_top_etfs(force_refresh=True)
            self.stdout.write(self.style.SUCCESS('OK'))

            self.stdout.write(self.style.SUCCESS(f'[{timezone.now()}] Market data updated successfully. Cache is warm.'))

        except Exception as e:
            logger.error(f"Error updating market data: {e}")
            self.stdout.write(self.style.ERROR(f'Error updating market data: {e}'))
