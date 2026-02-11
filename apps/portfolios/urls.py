from django.urls import path
from apps.portfolios import views

app_name = 'portfolios'

urlpatterns = [
    path('', views.portfolio_view, name='portfolio'),
    path('add/', views.add_to_portfolio_view, name='add'),
    path('<int:pk>/exit/', views.exit_position_view, name='exit'),
]
