"""
Tests for portfolio models and services.
"""
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.brokers.models import Broker
from apps.portfolios.models import Portfolio, PortfolioItem
from apps.portfolios.services import add_to_portfolio, exit_position, get_portfolio_summary
from apps.research_calls.models import ResearchCall

User = get_user_model()


class PortfolioModelTest(TestCase):
    """Test Portfolio and PortfolioItem models."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='customer@example.com',
            first_name='Test',
            last_name='Customer',
            password='TestPass123!',
            role='CUSTOMER',
        )
        self.analyst_user = User.objects.create_user(
            email='analyst@example.com',
            first_name='Analyst',
            last_name='User',
            password='TestPass123!',
            role='ANALYST',
        )
        self.broker = Broker.objects.create(
            name='Test Broker',
            slug='test-broker',
            sebi_registration_no='INZ000000000',
        )
        self.call = ResearchCall.objects.create(
            symbol='RELIANCE',
            created_by=self.analyst_user,
            broker=self.broker,
            action='BUY',
            call_type='SHORT_TERM',
            instrument_type='EQUITY',
            entry_price=Decimal('2500.00'),
            target_1=Decimal('2700.00'),
            stop_loss=Decimal('2400.00'),
            timeframe_days=30,
            status='ACTIVE',
        )

    def test_create_portfolio(self):
        portfolio = Portfolio.objects.create(user=self.user)
        self.assertEqual(portfolio.user, self.user)
        self.assertIsNotNone(portfolio.created_at)

    def test_add_portfolio_item(self):
        portfolio = Portfolio.objects.create(user=self.user)
        item = PortfolioItem.objects.create(
            portfolio=portfolio,
            research_call=self.call,
            entry_price=Decimal('2510.00'),
            quantity=10,
            entry_date=date.today(),
        )
        self.assertEqual(item.portfolio, portfolio)
        self.assertEqual(item.research_call, self.call)
        self.assertEqual(item.quantity, 10)
        self.assertEqual(item.status, 'ACTIVE')

    def test_invested_amount_calculation(self):
        portfolio = Portfolio.objects.create(user=self.user)
        item = PortfolioItem.objects.create(
            portfolio=portfolio,
            research_call=self.call,
            entry_price=Decimal('2500.00'),
            quantity=10,
            entry_date=date.today(),
        )
        expected = Decimal('2500.00') * 10
        self.assertEqual(item.invested_amount, expected)

    def test_realized_pnl_calculation(self):
        portfolio = Portfolio.objects.create(user=self.user)
        item = PortfolioItem.objects.create(
            portfolio=portfolio,
            research_call=self.call,
            entry_price=Decimal('2500.00'),
            quantity=10,
            entry_date=date.today(),
        )
        item.exit_price = Decimal('2700.00')
        item.exit_date = date.today()
        item.status = 'CLOSED'
        item.calculate_pnl()
        item.save()

        expected_pnl = (Decimal('2700.00') - Decimal('2500.00')) * 10
        self.assertEqual(item.pnl_amount, expected_pnl)

        expected_pnl_pct = ((Decimal('2700.00') - Decimal('2500.00')) / Decimal('2500.00')) * 100
        self.assertEqual(item.pnl_percentage, expected_pnl_pct)


class PortfolioServiceTest(TestCase):
    """Test portfolio services."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='customer@example.com',
            first_name='Test',
            last_name='Customer',
            password='TestPass123!',
            role='CUSTOMER',
        )
        self.analyst_user = User.objects.create_user(
            email='analyst@example.com',
            first_name='Analyst',
            last_name='User',
            password='TestPass123!',
            role='ANALYST',
        )
        self.broker = Broker.objects.create(
            name='Test Broker',
            slug='test-broker-service',
            sebi_registration_no='INZ000000001',
        )
        self.call = ResearchCall.objects.create(
            symbol='TCS',
            created_by=self.analyst_user,
            broker=self.broker,
            action='BUY',
            call_type='SHORT_TERM',
            instrument_type='EQUITY',
            entry_price=Decimal('3500.00'),
            target_1=Decimal('3700.00'),
            stop_loss=Decimal('3400.00'),
            timeframe_days=30,
            status='ACTIVE',
        )

    def test_add_to_portfolio_service(self):
        item = add_to_portfolio(
            user=self.user,
            research_call=self.call,
            entry_price=Decimal('3510.00'),
            quantity=5,
        )
        self.assertEqual(item.research_call, self.call)
        self.assertEqual(item.quantity, 5)
        self.assertEqual(item.status, 'ACTIVE')
        self.assertTrue(Portfolio.objects.filter(user=self.user).exists())

    def test_exit_position_service(self):
        item = add_to_portfolio(
            user=self.user,
            research_call=self.call,
            entry_price=Decimal('3500.00'),
            quantity=10,
        )
        exited_item = exit_position(
            portfolio_item=item,
            exit_price=Decimal('3700.00'),
            exit_date=date.today(),
        )
        self.assertEqual(exited_item.status, 'CLOSED')
        self.assertEqual(exited_item.exit_price, Decimal('3700.00'))
        self.assertIsNotNone(exited_item.exit_date)

        expected_pnl = (Decimal('3700.00') - Decimal('3500.00')) * 10
        self.assertEqual(exited_item.pnl_amount, expected_pnl)

    def test_portfolio_summary_service(self):
        add_to_portfolio(self.user, self.call, Decimal('3500.00'), 10)

        call2 = ResearchCall.objects.create(
            symbol='INFY',
            created_by=self.analyst_user,
            broker=self.broker,
            action='BUY',
            call_type='SHORT_TERM',
            instrument_type='EQUITY',
            entry_price=Decimal('1500.00'),
            target_1=Decimal('1600.00'),
            stop_loss=Decimal('1450.00'),
            timeframe_days=20,
            status='ACTIVE',
        )
        item2 = add_to_portfolio(self.user, call2, Decimal('1500.00'), 20)
        exit_position(item2, Decimal('1600.00'), date.today())

        summary = get_portfolio_summary(self.user)
        self.assertEqual(summary['active_positions'], 1)
        self.assertEqual(summary['closed_positions'], 1)
        self.assertGreater(summary['total_invested'], 0)
        self.assertGreater(summary['realized_pnl'], 0)
