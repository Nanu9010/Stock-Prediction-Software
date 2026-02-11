"""
Tests for research call models and services
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.brokers.models import Broker
from apps.research_calls.models import ResearchCall, ResearchCallEvent
from apps.research_calls.forms import ResearchCallForm
from apps.research_calls.services import create_research_call, approve_research_call, publish_research_call
from decimal import Decimal
from datetime import date, timedelta

User = get_user_model()


class ResearchCallModelTest(TestCase):
    """Test ResearchCall model"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='analyst@example.com',
            first_name='Test',
            last_name='Analyst',
            password='TestPass123!',
            role='ANALYST'
        )
        
        self.broker = Broker.objects.create(
            name='Test Broker',
            slug='test-broker'
        )
        
        self.call_data = {
            'symbol': 'RELIANCE',
            'created_by': self.user,
            'broker': self.broker,
            'action': 'BUY',
            'call_type': 'SHORT_TERM',
            'instrument_type': 'EQUITY',
            'entry_price': Decimal('2500.00'),
            'target_1': Decimal('2700.00'),
            'stop_loss': Decimal('2400.00'),
            'timeframe_days': 30,
            'rationale': 'Strong fundamentals'
        }
    
    def test_create_research_call(self):
        """Test creating a research call"""
        call = ResearchCall.objects.create(**self.call_data)
        
        self.assertEqual(call.symbol, 'RELIANCE')
        self.assertEqual(call.action, 'BUY')
        self.assertEqual(call.status, 'DRAFT')
        self.assertIsNotNone(call.created_at)
    
    def test_price_validation_buy_call(self):
        """Test price validation for BUY calls"""
        # Target should be > entry
        invalid_data = self.call_data.copy()
        invalid_data['target_1'] = Decimal('2400.00')  # Less than entry
        
        call = ResearchCall(**invalid_data)
        with self.assertRaises(Exception):
            call.full_clean()


class ResearchCallServiceTest(TestCase):
    """Test research call services"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='analyst@example.com',
            first_name='Test',
            last_name='Analyst',
            password='TestPass123!',
            role='ANALYST'
        )
        
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='AdminPass123!'
        )
        
        self.broker = Broker.objects.create(
            name='Test Broker',
            slug='test-broker-service'
        )
    
    def test_create_research_call_service(self):
        """Test create_research_call service"""
        call_data = {
            'symbol': 'TCS',
            'broker': self.broker,
            'action': 'BUY',
            'call_type': 'SHORT_TERM',
            'instrument_type': 'EQUITY',
            'entry_price': Decimal('3500.00'),
            'target_1': Decimal('3700.00'),
            'stop_loss': Decimal('3400.00'),
            'timeframe_days': 20,
            'rationale': 'Good earnings'
        }
        
        call = create_research_call(
            created_by=self.user,
            data=call_data
        )
        
        self.assertEqual(call.symbol, 'TCS')
        self.assertEqual(call.status, 'DRAFT')
        self.assertEqual(call.created_by, self.user)
        
        # Check event was created
        events = ResearchCallEvent.objects.filter(research_call=call)
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().event_type, 'CREATED')
    
    def test_approve_call_service(self):
        """Test approve_call service"""
        call = ResearchCall.objects.create(
            symbol='INFY',
            created_by=self.user,
            broker=self.broker,
            action='BUY',
            call_type='SHORT_TERM',
            entry_price=Decimal('1500.00'),
            target_1=Decimal('1600.00'),
            stop_loss=Decimal('1450.00'),
            timeframe_days=15,
            status='PENDING_APPROVAL'
        )
        
        approved_call = approve_research_call(call, self.admin)
        
        self.assertEqual(approved_call.status, 'APPROVED')
        self.assertIsNotNone(approved_call.approved_by)
        self.assertEqual(approved_call.approved_by, self.admin)


class ResearchCallFormTest(TestCase):
    def setUp(self):
        self.broker = Broker.objects.create(name='Test Broker', slug='test-broker-form')

    def test_valid_form(self):
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
            'broker': self.broker.id,
            'rationale': 'Strong buy signal',
        }
        form = ResearchCallForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_price_logic(self):
        data = {
            'symbol': 'RELIANCE',
            'exchange': 'NSE',
            'action': 'BUY',
            'call_type': 'INTRADAY',
            'instrument_type': 'EQUITY',
            'entry_price': 2500,
            'target_1': 2400, # Invalid
            'stop_loss': 2450,
            'timeframe_days': 1,
            'broker': self.broker.id,
        }
        form = ResearchCallForm(data=data)
        # Note: ModelForm might not catch model logic unless we explicitly validate or save
        # But our manual verification script showed it passed is_valid if we didn't add clean methods
        # Wait, I didn't add custom clean to form, only model has clean.
        # ModelForm validation calls model.clean().
        self.assertFalse(form.is_valid())
