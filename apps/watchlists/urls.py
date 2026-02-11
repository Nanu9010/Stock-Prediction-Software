from django.urls import path
from apps.watchlists import views

app_name = 'watchlists'

urlpatterns = [
    path('', views.watchlist_view, name='watchlist'),
    path('add/', views.add_to_watchlist_view, name='add'),
    path('<int:pk>/remove/', views.remove_from_watchlist_view, name='remove'),
]
