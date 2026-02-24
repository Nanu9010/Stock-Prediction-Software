from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # App URLs — Template/HTML views
    path('auth/', include('apps.authentication.urls')),
    path('', include('apps.dashboard.urls')),        # Dashboard as home
    path('calls/', include('apps.research_calls.urls')),
    path('portfolio/', include('apps.portfolios.urls')),
    path('watchlist/', include('apps.watchlists.urls')),
    path('market/', include('apps.market_data.urls')),
    path('trades/', include('apps.trades.urls')),
    path('admin-panel/', include('apps.admin_panel.urls')),
    path('payments/', include('apps.payments.urls')),

    # REST API endpoints
    path('api/core/', include('apps.core.urls', namespace='core')),
    path('api/brokers/', include('apps.brokers.urls', namespace='brokers')),
    # notifications: HTML inbox at /api/notifications/inbox/ + REST at /api/notifications/
    path('api/notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('api/subscriptions/', include('apps.subscriptions.urls', namespace='subscriptions')),
    path('api/audit/', include('apps.audit.urls', namespace='audit')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Customize admin site
admin.site.site_header = "Stock Research Platform Admin"
admin.site.site_title = "Stock Research Admin"
admin.site.index_title = "Welcome to Stock Research Platform Administration"
