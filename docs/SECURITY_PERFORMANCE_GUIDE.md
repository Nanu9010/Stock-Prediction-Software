# SECURITY & PERFORMANCE OPTIMIZATION GUIDE

## SECURITY CONSIDERATIONS

### 1. AUTHENTICATION & AUTHORIZATION SECURITY

#### A. Password Security
```python
# Password hashing (Django default: PBKDF2 with SHA256)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Recommended
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}
    },
    {
        'NAME': 'apps.core.validators.PasswordComplexityValidator',
        # Custom: requires uppercase, lowercase, digit, special char
    },
]
```

#### B. Session Security
```python
# Session configuration
SESSION_COOKIE_AGE = 604800  # 7 days
SESSION_COOKIE_HTTPONLY = True  # Prevents JavaScript access
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection

# Invalidate session on password change
from django.contrib.auth.signals import user_logged_in

@receiver(user_logged_in)
def update_last_login(sender, user, request, **kwargs):
    user.last_login_at = timezone.now()
    user.save(update_fields=['last_login_at'])
```

#### C. Rate Limiting
```python
# Using Django-ratelimit
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/15m', method='POST', block=True)
def login_view(request):
    """Limit login attempts to 5 per 15 minutes per IP"""
    pass

@ratelimit(key='user', rate='100/h', method='GET')
def research_calls_api(request):
    """Limit API calls to 100 per hour per user"""
    pass
```

#### D. CSRF Protection
```html
<!-- In all forms -->
<form method="POST">
  {% csrf_token %}
  <!-- form fields -->
</form>

<!-- In AJAX requests -->
<script>
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

fetch('/api/portfolio/add', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
    },
    body: JSON.stringify({...})
});
</script>
```

---

### 2. SQL INJECTION PREVENTION

#### A. Use Django ORM (parameterized queries)
```python
# SAFE - Django ORM automatically parameterizes
users = User.objects.filter(email=user_input)

# UNSAFE - Raw SQL without params
cursor.execute(f"SELECT * FROM users WHERE email = '{user_input}'")

# SAFE - Raw SQL with params
cursor.execute("SELECT * FROM users WHERE email = %s", [user_input])
```

#### B. Validate user inputs
```python
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def validate_symbol(symbol):
    """Validate stock symbol (alphanumeric only)"""
    if not symbol.isalnum():
        raise ValidationError('Symbol must be alphanumeric')
    return symbol.upper()
```

---

### 3. AUTHORIZATION & ACCESS CONTROL

#### A. Role-Based Access Control (RBAC)
```python
# Custom decorator
from functools import wraps
from django.http import HttpResponseForbidden

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.role not in roles:
                return HttpResponseForbidden("You don't have permission to access this page")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Usage
@role_required('ADMIN', 'ANALYST')
def create_research_call(request):
    pass

@role_required('CUSTOMER')
def add_to_portfolio(request):
    pass
```

#### B. Object-Level Permissions
```python
def edit_portfolio_view(request, portfolio_id):
    """Ensure user can only edit their own portfolio"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    
    # Check ownership
    if portfolio.user != request.user:
        raise PermissionDenied("You can only edit your own portfolio")
    
    # Proceed with edit
    pass
```

---

### 4. DATA PROTECTION

#### A. Sensitive Data Encryption
```python
from cryptography.fernet import Fernet
from django.conf import settings

def encrypt_data(data):
    """Encrypt sensitive data before storing"""
    cipher = Fernet(settings.ENCRYPTION_KEY.encode())
    encrypted = cipher.encrypt(data.encode())
    return encrypted.decode()

def decrypt_data(encrypted_data):
    cipher = Fernet(settings.ENCRYPTION_KEY.encode())
    decrypted = cipher.decrypt(encrypted_data.encode())
    return decrypted.decode()

# Example: Encrypt broker's SEBI registration number
broker.sebi_registration_no = encrypt_data(sebi_number)
```

#### B. Audit Logging (Tamper-Proof)
```python
# Middleware to log all critical actions
class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Log state-changing actions
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            if request.user.is_authenticated:
                AuditLog.objects.create(
                    user=request.user,
                    action=f"{request.method} {request.path}",
                    entity_type='request',
                    entity_id=0,
                    new_values={'request_data': request.POST.dict()},
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                )
        
        return response
```

#### C. Soft Deletes (Never hard delete critical data)
```python
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Include deleted
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete instead of hard delete"""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])
    
    class Meta:
        abstract = True
```

---

### 5. API SECURITY

#### A. API Rate Limiting
```python
# Using Django REST Framework throttling
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'burst': '60/minute',
    }
}
```

#### B. Input Validation
```python
from rest_framework import serializers

class AddToPortfolioSerializer(serializers.Serializer):
    research_call_id = serializers.IntegerField(min_value=1)
    entry_price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    quantity = serializers.IntegerField(min_value=1, max_value=100000)
    entry_date = serializers.DateField()
    
    def validate_research_call_id(self, value):
        """Ensure call exists and is active"""
        if not ResearchCall.objects.filter(id=value, status='ACTIVE').exists():
            raise serializers.ValidationError("Research call not found or not active")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        if data['entry_date'] > timezone.now().date():
            raise serializers.ValidationError("Entry date cannot be in the future")
        return data
```

---

### 6. XSS PREVENTION

#### A. Template Auto-Escaping (Django default)
```html
<!-- Django automatically escapes HTML -->
<p>{{ user_input }}</p>
<!-- If user_input = "<script>alert('XSS')</script>" -->
<!-- Output: &lt;script&gt;alert('XSS')&lt;/script&gt; -->

<!-- To render raw HTML (use with extreme caution) -->
<p>{{ trusted_html|safe }}</p>
```

#### B. Content Security Policy (CSP)
```python
# Add CSP headers
MIDDLEWARE = [
    ...
    'csp.middleware.CSPMiddleware',
]

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "https://cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "https://fonts.googleapis.com")
CSP_IMG_SRC = ("'self'", "data:", "https:")
```

---

### 7. PRODUCTION SECURITY CHECKLIST

```python
# settings/production.py

DEBUG = False
ALLOWED_HOSTS = ['stockresearch.com', 'www.stockresearch.com']

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS (force HTTPS for 1 year)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Clickjacking protection
X_FRAME_OPTIONS = 'DENY'

# Browser XSS protection
SECURE_BROWSER_XSS_FILTER = True

# Content type sniffing protection
SECURE_CONTENT_TYPE_NOSNIFF = True
```

---

## PERFORMANCE OPTIMIZATION

### 1. DATABASE QUERY OPTIMIZATION

#### A. N+1 Query Problem (CRITICAL)
```python
# BAD - N+1 queries
calls = ResearchCall.objects.filter(status='ACTIVE')  # 1 query
for call in calls:
    print(call.broker.name)  # N queries (one per call)
    print(call.analyst.name)  # N more queries

# GOOD - Single query with joins
calls = ResearchCall.objects.filter(status='ACTIVE') \
    .select_related('broker', 'analyst')  # 1 query with JOIN

for call in calls:
    print(call.broker.name)  # No additional query
    print(call.analyst.name)  # No additional query
```

#### B. Prefetch Related (for Many-to-Many or Reverse FK)
```python
# BAD
portfolios = Portfolio.objects.all()
for portfolio in portfolios:
    for item in portfolio.items.all():  # N queries
        print(item.research_call.symbol)

# GOOD
portfolios = Portfolio.objects.prefetch_related('items__research_call')
for portfolio in portfolios:
    for item in portfolio.items.all():  # No additional queries
        print(item.research_call.symbol)
```

#### C. Selective Field Loading
```python
# BAD - Loads all fields
calls = ResearchCall.objects.all()

# GOOD - Load only needed fields
calls = ResearchCall.objects.only(
    'id', 'symbol', 'entry_price', 'target_1', 'stop_loss'
)

# Or exclude heavy fields
calls = ResearchCall.objects.defer('rationale', 'technical_levels')
```

#### D. Aggregation in Database (not Python)
```python
# BAD - Python-level aggregation
portfolio_items = PortfolioItem.objects.filter(portfolio=portfolio)
total_invested = sum(item.invested_amount for item in portfolio_items)

# GOOD - Database-level aggregation
from django.db.models import Sum

total_invested = PortfolioItem.objects.filter(portfolio=portfolio) \
    .aggregate(total=Sum('invested_amount'))['total']
```

---

### 2. INDEXING STRATEGY

#### A. Critical Indexes (already in schema)
```sql
-- Frequently filtered fields
CREATE INDEX idx_research_calls_status ON research_calls(status);
CREATE INDEX idx_research_calls_symbol ON research_calls(symbol);
CREATE INDEX idx_research_calls_published ON research_calls(published_at);

-- Composite indexes for common queries
CREATE INDEX idx_active_calls ON research_calls(status, published_at);
CREATE INDEX idx_broker_calls ON research_calls(broker_id, status);

-- Foreign key indexes
CREATE INDEX idx_portfolio_items_portfolio ON portfolio_items(portfolio_id);
CREATE INDEX idx_portfolio_items_call ON portfolio_items(research_call_id);
```

#### B. Index Usage Analysis
```sql
-- Check if indexes are being used
EXPLAIN SELECT * FROM research_calls 
WHERE status = 'ACTIVE' 
AND published_at >= '2026-02-09'
ORDER BY published_at DESC;

-- Look for "Using index" in EXPLAIN output
-- If "Using filesort" appears, add index on ORDER BY column
```

---

### 3. CACHING STRATEGY

#### A. Redis Cache for Expensive Queries
```python
from django.core.cache import cache

def get_todays_calls():
    """Cache today's calls for 5 minutes"""
    cache_key = f"todays_calls_{timezone.now().date()}"
    
    # Try cache first
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Cache miss - query database
    calls = ResearchCall.objects.filter(
        status='ACTIVE',
        published_at__date=timezone.now().date()
    ).select_related('broker', 'analyst')
    
    # Store in cache (TTL: 300 seconds)
    cache.set(cache_key, list(calls), 300)
    
    return calls

# Invalidate cache when new call published
@receiver(post_save, sender=ResearchCall)
def invalidate_calls_cache(sender, instance, **kwargs):
    if instance.status == 'PUBLISHED':
        cache_key = f"todays_calls_{timezone.now().date()}"
        cache.delete(cache_key)
```

#### B. Template Fragment Caching
```html
{% load cache %}

{% cache 600 broker_rankings %}
  <!-- This fragment cached for 10 minutes -->
  <div class="broker-rankings">
    {% for broker in top_brokers %}
      <div class="broker-card">
        {{ broker.name }} - {{ broker.overall_accuracy }}%
      </div>
    {% endfor %}
  </div>
{% endcache %}
```

#### C. Database Query Result Caching
```python
# Low-level cache API
def get_broker_accuracy(broker_id):
    cache_key = f"broker_accuracy_{broker_id}"
    
    accuracy = cache.get(cache_key)
    if accuracy is None:
        # Expensive calculation
        accuracy = calculate_broker_accuracy(broker_id)
        cache.set(cache_key, accuracy, 3600)  # 1 hour
    
    return accuracy
```

---

### 4. PAGINATION

#### A. Efficient Pagination
```python
from django.core.paginator import Paginator

def live_calls_view(request):
    calls = ResearchCall.objects.filter(status='ACTIVE') \
        .select_related('broker', 'analyst') \
        .order_by('-published_at')
    
    paginator = Paginator(calls, 50)  # 50 per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'live_calls.html', {'page_obj': page_obj})
```

#### B. Cursor-Based Pagination (for large datasets)
```python
# Instead of LIMIT/OFFSET (slow on large tables)
# Use WHERE id > last_seen_id

def get_next_page(last_id=None, limit=50):
    queryset = ResearchCall.objects.filter(status='ACTIVE')
    
    if last_id:
        queryset = queryset.filter(id__gt=last_id)
    
    return queryset.order_by('id')[:limit]
```

---

### 5. BACKGROUND JOBS (Celery)

#### A. Offload Heavy Tasks
```python
# Don't block HTTP requests with slow operations

# BAD - Slow operation in view
def publish_call_view(request, call_id):
    call = ResearchCall.objects.get(id=call_id)
    call.status = 'PUBLISHED'
    call.published_at = timezone.now()
    call.save()
    
    # Send email to 10,000 subscribers (takes 30 seconds)
    send_email_to_all_subscribers(call)
    
    return redirect('dashboard')

# GOOD - Offload to Celery
from apps.notifications.tasks import send_call_published_emails

def publish_call_view(request, call_id):
    call = ResearchCall.objects.get(id=call_id)
    call.status = 'PUBLISHED'
    call.published_at = timezone.now()
    call.save()
    
    # Async task (returns immediately)
    send_call_published_emails.delay(call.id)
    
    return redirect('dashboard')
```

#### B. Periodic Tasks (Celery Beat)
```python
# apps/analytics/tasks.py

@celery_app.task
def calculate_daily_broker_metrics():
    """
    Runs nightly to calculate broker accuracy
    """
    yesterday = timezone.now().date() - timedelta(days=1)
    
    for broker in Broker.objects.filter(is_active=True):
        closed_calls = ResearchCall.objects.filter(
            broker=broker,
            status='CLOSED',
            closed_at__date=yesterday
        )
        
        total_closed = closed_calls.count()
        if total_closed == 0:
            continue
        
        successful = closed_calls.filter(is_successful=True).count()
        accuracy = (successful / total_closed) * 100
        
        BrokerPerformanceMetrics.objects.create(
            broker=broker,
            metric_date=yesterday,
            total_closed_calls=total_closed,
            successful_calls=successful,
            accuracy_percentage=accuracy,
            avg_return_percentage=calculate_avg_return(closed_calls),
        )
```

---

### 6. STATIC FILES OPTIMIZATION

#### A. WhiteNoise for Static Files
```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # After SecurityMiddleware
    ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### B. Minify CSS/JS (Production)
```bash
# Install django-compressor
pip install django-compressor

# settings.py
INSTALLED_APPS += ['compressor']
COMPRESS_ENABLED = not DEBUG
COMPRESS_OFFLINE = True
```

```html
{% load compress %}

{% compress css %}
  <link rel="stylesheet" href="{% static 'css/base.css' %}">
  <link rel="stylesheet" href="{% static 'css/dashboard.css' %}">
{% endcompress %}

{% compress js %}
  <script src="{% static 'js/main.js' %}"></script>
  <script src="{% static 'js/portfolio.js' %}"></script>
{% endcompress %}
```

---

### 7. DATABASE CONNECTION POOLING

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'CONN_MAX_AGE': 600,  # Persist connections for 10 minutes
    }
}
```

---

### 8. MONITORING & PROFILING

#### A. Django Debug Toolbar (Development)
```python
# settings/development.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']

# Shows SQL queries, cache hits, template rendering time
```

#### B. Sentry for Error Tracking (Production)
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=env('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,  # 10% of requests
    send_default_pii=False,
)
```

---

## SCALABILITY CONSIDERATIONS

### 1. Read Replicas (MySQL)
```python
# For 100k+ users, split read/write operations

DATABASES = {
    'default': {  # Write operations
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stock_research',
        'HOST': 'primary-db.mysql.com',
    },
    'replica': {  # Read operations
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stock_research',
        'HOST': 'replica-db.mysql.com',
    }
}

DATABASE_ROUTERS = ['apps.core.routers.PrimaryReplicaRouter']

# Router
class PrimaryReplicaRouter:
    def db_for_read(self, model, **hints):
        return 'replica'
    
    def db_for_write(self, model, **hints):
        return 'default'
```

### 2. Horizontal Scaling (Load Balancing)
```
Internet
   │
   ▼
NGINX Load Balancer
   │
   ├─────┬─────┬─────┬─────┐
   ▼     ▼     ▼     ▼     ▼
Django Django Django Django Django
App    App    App    App    App
Server Server Server Server Server
   │     │     │     │     │
   └─────┴─────┴─────┴─────┘
              │
              ▼
      MySQL Database
         (Primary)
              │
              ▼
      MySQL Replica
       (Read-only)
```

### 3. CDN for Static Files
```python
# Use CloudFlare/AWS CloudFront for static assets
STATIC_URL = 'https://cdn.stockresearch.com/static/'
MEDIA_URL = 'https://cdn.stockresearch.com/media/'
```

---

# END OF SECURITY & PERFORMANCE GUIDE
