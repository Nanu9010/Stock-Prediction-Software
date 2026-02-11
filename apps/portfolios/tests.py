"""
Tests for portfolio models and services
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.brokers.models import Broker
from apps.research_calls.models import ResearchCall
from apps.portfolios.models import Portfolio, PortfolioItem
from apps.portfolios.services import add_to_portfolio, exit_position, get_portfolio_summary
from decimal import Decimal
from datetime import date

User = get_user_model()


class PortfolioModelTest(TestCase):
    """Test Portfolio and PortfolioItem models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='customer@example.com',
            first_name='Test',
            last_name='Customer',
            password='TestPass123!',
            role='CUSTOMER'
        )
        
        analyst_user = User.objects.create_user(
            email='analyst@example.com',
            first_name='Analyst',
            last_name='User',
            password='TestPass123!',
            role='ANALYST'
        )
        
        broker = Broker.objects.create(
            name='Test Broker',
            sebi_registration='INZ000000000'
        )
        
        analyst = Analyst.objects.create(
            user=analyst_user,
            broker=broker,
            sebi_registration='INH000000000'
        )
        
        self.call = ResearchCall.objects.create(
            symbol='RELIANCE',
            analyst=analyst,
            broker=broker,
            action='BUY',
            call_type='SHORT_TERM',
            entry_price=Decimal('2500.00'),
            target_1=Decimal('2700.00'),
            stop_loss=Decimal('2400.00'),
            duration_days=30,
            status='ACTIVE'
        )
    
    def test_create_portfolio(self):
        """Test creating a portfolio"""
        portfolio = Portfolio.objects.create(user=self.user)
        
        self.assertEqual(portfolio.user, self.user)
        self.assertIsNotNone(portfolio.created_at)
    
    def test_add_portfolio_item(self):
        """Test adding item to portfolio"""
        portfolio = Portfolio.objects.create(user=self.user)
        
        item = PortfolioItem.objects.create(
            portfolio=portfolio,
            research_call=self.call,
            entry_price=Decimal('2510.00'),
            quantity=10,
            entry_date=date.today()
        )
        
        self.assertEqual(item.portfolio, portfolio)
        self.assertEqual(item.research_call, self.call)
        self.assertEqual(item.quantity, 10)
        self.assertEqual(item.status, 'ACTIVE')
    
    def test_invested_amount_calculation(self):
        """Test invested amount calculation"""
        portfolio = Portfolio.objects.create(user=self.user)
        
        item = PortfolioItem.objects.create(
            portfolio=portfolio,
            research_call=self.call,
            entry_price=Decimal('2500.00'),
            quantity=10,
            entry_date=date.today()
        )
        
        expected = Decimal('2500.00') * 10
        self.assertEqual(item.invested_amount, expected)
    
    def test_realized_pnl_calculation(self):
        """Test realized P&L calculation"""
        portfolio = Portfolio.objects.create(user=self.user)
        
        item = PortfolioItem.objects.create(
            portfolio=portfolio,
            research_call=self.call,
            entry_price=Decimal('2500.00'),
            quantity=10,
            entry_date=date.today(),
            exit_price=Decimal('2700.00'),
            exit_date=date.today(),
            status='CLOSED'
        )
        
        # P&L = (exit - entry) * quantity
        expected_pnl = (Decimal('2700.00') - Decimal('2500.00')) * 10
        self.assertEqual(item.pnl_amount, expected_pnl)
        
        # P&L % = ((exit - entry) / entry) * 100
        expected_pnl_pct = ((Decimal('2700.00') - Decimal('2500.00')) / Decimal('2500.00')) * 100
        self.assertEqual(item.pnl_percentage, expected_pnl_pct)


class PortfolioServiceTest(TestCase):
    """Test portfolio services"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='customer@example.com',
            first_name='Test',
            last_name='Customer',
            password='TestPass123!',
            role='CUSTOMER'
        )
        
        analyst_user = User.objects.create_user(
            email='analyst@example.com',
            first_name='Analyst',
            last_name='User',
            password='TestPass123!',
            role='ANALYST'
        )
        
        broker = Broker.objects.create(
            name='Test Broker',
            sebi_registration='INZ000000000'
        )
        
        analyst = Analyst.objects.create(
            user=analyst_user,
            broker=broker,
            sebi_registration='INH000000000'
        )
        
        self.call = ResearchCall.objects.create(
            symbol='TCS',
            analyst=analyst,
            broker=broker,
            action='BUY',
            call_type='SHORT_TERM',
            entry_price=Decimal('3500.00'),
            target_1=Decimal('3700.00'),
            stop_loss=Decimal('3400.00'),
            duration_days=30,
            status='ACTIVE'
        )
    
    def test_add_to_portfolio_service(self):
        """Test add_to_portfolio service"""
        item = add_to_portfolio(
            user=self.user,
            research_call=self.call,
            entry_price=Decimal('3510.00'),
            quantity=5
        )
        
        self.assertEqual(item.research_call, self.call)
        self.assertEqual(item.quantity, 5)
        self.assertEqual(item.status, 'ACTIVE')
        
        # Check portfolio was created
        portfolio = Portfolio.objects.get(user=self.user)
        self.assertIsNotNone(portfolio)
    
    def test_exit_position_service(self):
        """Test exit_position service"""
        # First add to portfolio
        item = add_to_portfolio(
            user=self.user,
            research_call=self.call,
            entry_price=Decimal('3500.00'),
            quantity=10
        )
        
        # Then exit
        exited_item = exit_position(
            portfolio_item=item,
            exit_price=Decimal('3700.00'),
            exit_date=date.today()
        )
        
        self.assertEqual(exited_item.status, 'CLOSED')
        self.assertEqual(exited_item.exit_price, Decimal('3700.00'))
        self.assertIsNotNone(exited_item.exit_date)
        
        # Check P&L
        expected_pnl = (Decimal('3700.00') - Decimal('3500.00')) * 10
        self.assertEqual(exited_item.pnl_amount, expected_pnl)
    
    def test_portfolio_summary_service(self):
        """Test get_portfolio_summary service"""
        # Add multiple positions
        add_to_portfolio(self.user, self.call, Decimal('3500.00'), 10)
        
        # Create another call and add
        call2 = ResearchCall.objects.create(
            symbol='INFY',
            analyst=self.call.analyst,
            broker=self.call.broker,
            action='BUY',
            call_type='SHORT_TERM',
            entry_price=Decimal('1500.00'),
            target_1=Decimal('1600.00'),
            stop_loss=Decimal('1450.00'),
            duration_days=20,
            status='ACTIVE'
        )
        
        item2 = add_to_portfolio(self.user, call2, Decimal('1500.00'), 20)
        
        # Exit one position
        exit_position(item2, Decimal('1600.00'), date.today())
        
        # Get summary
        summary = get_portfolio_summary(self.user)
        
        self.assertEqual(summary['active_positions'], 1)
        self.assertEqual(summary['closed_positions'], 1)
        self.assertGreater(summary['total_invested'], 0)
        self.assertGreater(summary['realized_pnl'], 0)
