"""
Payment app URL configuration
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('membership/', views.membership_view, name='membership'),
    path('create-order/', views.create_subscription_order, name='create_order'),
    path('verify/', views.verify_payment, name='verify_payment'),
    path('webhook/', views.razorpay_webhook, name='webhook'),
]
