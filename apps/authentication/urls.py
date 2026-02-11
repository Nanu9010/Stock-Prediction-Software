from django.urls import path
from apps.authentication import views
from apps.authentication.password_reset import password_reset_request, password_reset_confirm

app_name = 'authentication'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
]
