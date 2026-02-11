from django.urls import path
from apps.research_calls import views

app_name = 'research_calls'

urlpatterns = [
    path('', views.call_list_view, name='list'),
    path('live/', views.live_calls_view, name='live_calls'),
    path('closed/', views.closed_calls_view, name='closed_calls'),
    path('baskets/', views.pro_baskets_view, name='pro_baskets'),
    path('closed-trades/', views.closed_trades_view, name='closed_trades'),  # Legacy
    path('<int:pk>/', views.call_detail_view, name='detail'),
    path('create/', views.call_create_view, name='create'),
    path('<int:pk>/edit/', views.call_edit_view, name='edit'),
    path('<int:pk>/approve/', views.call_approve_view, name='approve'),
    path('<int:pk>/publish/', views.call_publish_view, name='publish'),
]
