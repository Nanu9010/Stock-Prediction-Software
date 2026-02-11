# Stock Research Platform

A comprehensive Django-based platform for managing stock research calls, broker performance tracking, portfolio management, and analytics.

## Features

- **Role-Based Access Control**: Admin, Analyst, and Customer roles
- **Research Call Management**: Create, approve, and track stock research calls with targets and stop-losses
- **Real-Time Lifecycle Tracking**: Automatic monitoring of price levels and call status updates
- **Portfolio Management**: Track investments with real-time P&L calculations
- **Broker Analytics**: Performance metrics, accuracy tracking, and leaderboards
- **Notifications**: Email and in-app alerts for call events
- **Subscription Management**: Flexible access control with subscription plans

## Tech Stack

- **Backend**: Django 5.0, Django REST Framework
- **Database**: MySQL
- **Cache/Queue**: Redis, Celery
- **Frontend**: HTML, CSS, JavaScript
- **Background Jobs**: Celery Beat for periodic tasks

## Installation

### Prerequisites

- Python 3.10+
- MySQL 8.0+
- Redis 6.0+

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock_research_platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and settings
   ```

5. **Create MySQL database**
   ```sql
   CREATE DATABASE stock_research_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

10. **Start Celery worker** (in separate terminal)
    ```bash
    celery -A celery_app worker -l info
    ```

11. **Start Celery beat** (in separate terminal)
    ```bash
    celery -A celery_app beat -l info
    ```

## Project Structure

```
stock_research_platform/
├── apps/                    # Django applications
│   ├── authentication/      # User management & auth
│   ├── brokers/            # Broker & analyst management
│   ├── research_calls/     # Research call engine
│   ├── lifecycle/          # Call lifecycle tracking
│   ├── portfolios/         # Portfolio management
│   ├── watchlists/         # Watchlist functionality
│   ├── subscriptions/      # Subscription plans
│   ├── notifications/      # Notification system
│   ├── analytics/          # Performance analytics
│   ├── dashboard/          # Dashboard views
│   ├── audit/              # Audit logging
│   └── core/               # Shared utilities
├── config/                 # Project configuration
├── templates/              # Global templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploads
└── celery_app/            # Celery configuration
```

## Usage

### Admin Panel
Access the Django admin at `http://localhost:8000/admin/` to manage brokers, analysts, and system configuration.

### Customer Dashboard
Customers can view live research calls, manage portfolios, and track performance at `http://localhost:8000/customer/dashboard/`.

### Analyst Dashboard
Analysts can create and manage research calls at `http://localhost:8000/analyst/dashboard/`.

## Testing

Run tests with pytest:
```bash
pytest
```

## License

Proprietary - All rights reserved

## Support

For support, please contact support@stockresearch.com
