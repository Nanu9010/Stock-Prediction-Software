"""
Tests for authentication models and services
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.authentication.models import UserSession
from apps.authentication.utils import generate_verification_token
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'TestPassword123!',
            'role': 'CUSTOMER'
        }
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.role, 'CUSTOMER')
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='AdminPass123!'
        )
        
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, 'ADMIN')
    
    def test_user_str_method(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'Test User')
    
    def test_get_full_name(self):
        """Test get_full_name method"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_full_name(), 'Test User')
    
    def test_email_unique(self):
        """Test email uniqueness constraint"""
        User.objects.create_user(**self.user_data)
        
        with self.assertRaises(Exception):
            User.objects.create_user(**self.user_data)


class UserSessionTest(TestCase):
    """Test UserSession model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='TestPass123!',
            role='CUSTOMER'
        )
    
    def test_create_session(self):
        """Test creating a user session"""
        session = UserSession.objects.create(
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test Browser'
        )
        
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.ip_address, '127.0.0.1')
        self.assertIsNotNone(session.created_at)
    
    def test_session_str_method(self):
        """Test session string representation"""
        session = UserSession.objects.create(
            user=self.user,
            session_key='test_key',
            ip_address='127.0.0.1'
        )
        
        self.assertIn(self.user.email, str(session))


class AuthenticationUtilsTest(TestCase):
    """Test authentication utilities"""
    
    def test_generate_verification_token(self):
        """Test token generation"""
        token = generate_verification_token()
        
        self.assertIsInstance(token, str)
        self.assertEqual(len(token), 64)  # 32 bytes hex = 64 chars
