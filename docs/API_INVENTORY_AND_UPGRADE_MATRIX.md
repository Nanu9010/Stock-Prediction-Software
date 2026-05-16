# API Inventory and Free-to-Upgrade Matrix

This document lists the APIs present in the project, what type of API each one is, where it is called from, and which areas currently treat users as "free" and prompt them to upgrade.

## Summary

- There is no explicit `FREE` subscription plan in the backend models.
- In practice, the app treats a user with no active subscription as the free tier.
- Paid plans currently seeded by the system are `BASIC`, `PRO`, and `PREMIUM`.
- Most upgrade prompts point to `/payments/membership/`.

## Current Paid Plans

Source: [apps/payments/management/commands/create_plans.py](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/apps/payments/management/commands/create_plans.py)

| Plan | Type | Monthly | Yearly | Main Intent |
|---|---|---:|---:|---|
| Basic | Paid subscription | 499 | 4990 | Entry paid tier with limited research calls |
| PRO | Paid subscription | 999 | 9990 | Main premium tier with unlimited calls and advanced features |
| Premium | Paid subscription | 1999 | 19990 | Highest tier with dedicated support and API access |

## Free Tier Interpretation

The codebase does not define a plan called `FREE`. Instead, these states behave like a free plan:

- Guest user not logged in
- Logged-in customer with no `user.subscription`
- Logged-in customer whose subscription is inactive or expired

Relevant code:

- [apps/payments/models.py](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/apps/payments/models.py)
- [apps/authentication/models.py](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/apps/authentication/models.py)
- [apps/research_calls/views.py](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/apps/research_calls/views.py)

## Internal API Inventory

### Core APIs

| Endpoint | Methods | Type | Auth | Backend Source | Called From |
|---|---|---|---|---|---|
| `/api/core/health/` | `GET` | REST JSON utility | Public | `apps.core.views.HealthCheckView` | No frontend call found in repo |
| `/api/core/info/` | `GET` | REST JSON utility | Public | `apps.core.views.APIInfoView` | No frontend call found in repo |
| `/api/core/live-ticker/` | `GET` | JSON utility / live market feed | Public | `apps.core.ticker_views.LiveTickerView` | No frontend call found in repo, but should be used by ticker bar |

### Broker APIs

| Endpoint | Methods | Type | Auth | Backend Source | Called From |
|---|---|---|---|---|---|
| `/api/brokers/` | `GET` | REST list | Public | `apps.brokers.views.BrokerListView` | No frontend call found in repo |
| `/api/brokers/<id>/` | `GET` | REST detail | Public | `apps.brokers.views.BrokerDetailView` | No frontend call found in repo |
| `/api/brokers/<id>/metrics/` | `GET` | REST metrics history | Authenticated | `apps.brokers.views.BrokerPerformanceMetricsView` | No frontend call found in repo |
| `/api/brokers/admin/` | `GET`, `POST` | Admin REST CRUD | Admin | `apps.brokers.views.AdminBrokerListCreateView` | No frontend call found in repo |
| `/api/brokers/admin/<id>/` | `GET`, `PATCH`, `DELETE` | Admin REST CRUD | Admin | `apps.brokers.views.AdminBrokerDetailView` | No frontend call found in repo |

### Notification APIs

| Endpoint | Methods | Type | Auth | Backend Source | Called From |
|---|---|---|---|---|---|
| `/api/notifications/inbox/` | `GET` | HTML page shell | Authenticated | `apps.notifications.views.NotificationsPageView` | Direct page route |
| `/api/notifications/` | `GET` | REST list | Authenticated | `apps.notifications.views.NotificationListView` | [templates/notifications/list.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/notifications/list.html) |
| `/api/notifications/mark-read/` | `POST` | REST action | Authenticated | `apps.notifications.views.NotificationMarkReadView` | [templates/notifications/list.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/notifications/list.html) |
| `/api/notifications/mark-all-read/` | `POST` | REST action | Authenticated | `apps.notifications.views.NotificationMarkAllReadView` | [templates/notifications/list.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/notifications/list.html) |
| `/api/notifications/unread-count/` | `GET` | REST counter | Authenticated | `apps.notifications.views.UnreadNotificationCountView` | No frontend call found in repo |
| `/api/notifications/preferences/` | `GET`, `PATCH` | REST settings | Authenticated | `apps.notifications.views.NotificationPreferencesView` | No frontend call found in repo |

### Subscription APIs

| Endpoint | Methods | Type | Auth | Backend Source | Called From |
|---|---|---|---|---|---|
| `/api/subscriptions/plans/` | `GET` | REST list | Public | `apps.subscriptions.views.SubscriptionPlanListView` | No frontend call found in repo |
| `/api/subscriptions/plans/<id>/` | `GET` | REST detail | Public | `apps.subscriptions.views.SubscriptionPlanDetailView` | No frontend call found in repo |
| `/api/subscriptions/my/` | `GET` | REST list | Authenticated | `apps.subscriptions.views.MySubscriptionsView` | No frontend call found in repo |
| `/api/subscriptions/my/active/` | `GET` | REST detail | Authenticated | `apps.subscriptions.views.ActiveSubscriptionView` | No frontend call found in repo |
| `/api/subscriptions/admin/plans/` | `GET`, `POST` | Admin REST CRUD | Admin | `apps.subscriptions.views.AdminSubscriptionPlanListCreateView` | No frontend call found in repo |
| `/api/subscriptions/admin/plans/<id>/` | `GET`, `PATCH`, `DELETE` | Admin REST CRUD | Admin | `apps.subscriptions.views.AdminSubscriptionPlanDetailView` | No frontend call found in repo |
| `/api/subscriptions/admin/users/` | `GET` | Admin REST list | Admin | `apps.subscriptions.views.AdminUserSubscriptionsView` | No frontend call found in repo |

### Audit APIs

| Endpoint | Methods | Type | Auth | Backend Source | Called From |
|---|---|---|---|---|---|
| `/api/audit/logs/` | `GET` | REST list | Admin | `apps.audit.views.AuditLogListView` | No frontend call found in repo |
| `/api/audit/logs/<id>/` | `GET` | REST detail | Admin | `apps.audit.views.AuditLogDetailView` | No frontend call found in repo |
| `/api/audit/my-logs/` | `GET` | REST list | Authenticated | `apps.audit.views.MyAuditLogListView` | No frontend call found in repo |

### Market Data APIs

| Endpoint | Methods | Type | Auth | Backend Source | Called From |
|---|---|---|---|---|---|
| `/market/indices/` | `GET` | HTML page | Public | `apps.market_data.views.market_indices_view` | Direct page route |
| `/market/stocks/` | `GET` | HTML page | Public | `apps.market_data.views.popular_stocks_view` | Direct page route |
| `/market/api/` | `GET` | Unified JSON data API | Public | `apps.market_data.views.market_data_api` | [templates/markets/overview_v2.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/markets/overview_v2.html) |
| `/market/update/` | `GET` | JSON admin action | Admin | `apps.market_data.views.update_market_data_view` | No frontend call found in repo |

Supported `/market/api/?type=` values:

| `type` value | Response Kind | Data Source |
|---|---|---|
| `ticker` | JSON market ticker data | `apps.market_data.services.get_ticker_data()` |
| `indices` | JSON indices data | `apps.market_data.services.get_live_indices()` |
| `gainers` | JSON top gainers | `apps.market_data.services.get_gainers()` |
| `losers` | JSON top losers | `apps.market_data.services.get_losers()` |
| `active` | JSON most active stocks | `apps.market_data.services.get_most_active()` |
| `stocks` | JSON popular stocks | `apps.market_data.services.get_popular_stocks_data()` |
| `etfs` | JSON ETF data | `services.sip_mf_etf_service.get_top_etfs()` |
| `commodities` | JSON commodities data | `services.commodity_service` |
| `mf_navs` | JSON mutual fund data | `services.sip_mf_etf_service.get_top_mutual_funds()` |

### Payment and Membership APIs

| Endpoint | Methods | Type | Auth | Backend Source | Called From |
|---|---|---|---|---|---|
| `/payments/membership/` | `GET` | HTML page | Authenticated | `apps.payments.views.membership_view` | Upgrade CTAs across the app |
| `/payments/create-order/` | `POST` | AJAX payment bootstrap | Authenticated | `apps.payments.views.create_subscription_order` | [templates/payments/membership.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/payments/membership.html) |
| `/payments/verify/` | `POST` | AJAX payment verification | Authenticated | `apps.payments.views.verify_payment` | [templates/payments/membership.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/payments/membership.html) |
| `/payments/webhook/` | `POST` | Gateway webhook | Public gateway callback | `apps.payments.views.razorpay_webhook` | Called by Razorpay, not frontend JS |

### Portfolio and Watchlist AJAX Endpoints

These are not under `/api/`, but they are still used as front-end action APIs.

| Endpoint | Methods | Type | Auth | Backend Source | Called From |
|---|---|---|---|---|---|
| `/portfolio/add/` | `POST` | AJAX form action | Authenticated | `apps.portfolios.views.add_to_portfolio_view` | [static/js/main.js](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/static/js/main.js) |
| `/portfolio/<id>/exit/` | `POST` | AJAX form action | Authenticated | `apps.portfolios.views.exit_position_view` | [static/js/main.js](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/static/js/main.js) |
| `/watchlist/add/` | `POST` | AJAX form action | Authenticated | `apps.watchlists.views.add_to_watchlist_view` | [static/js/main.js](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/static/js/main.js) |
| `/watchlist/<id>/remove/` | `POST` | AJAX form action | Authenticated | `apps.watchlists.views.remove_from_watchlist_view` | [templates/watchlists/watchlist.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/watchlists/watchlist.html) |

### Admin Panel AJAX Endpoint

| Endpoint | Methods | Type | Auth | Backend Source | Called From |
|---|---|---|---|---|---|
| `/admin-panel/api/stats/` | `GET` | Admin dashboard JSON refresh | Admin | `apps.admin_panel.views.AdminDashboardStatsAPIView` | [templates/admin_panel/dashboard.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/admin_panel/dashboard.html) |

## External API and Widget Integrations

| External Service | Type | Used In | Purpose |
|---|---|---|---|
| Yahoo Finance via `yfinance` | Server-side external market API | [apps/core/ticker_views.py](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/apps/core/ticker_views.py) | Live ticker market data |
| Razorpay Checkout | Frontend payment SDK | [templates/payments/membership.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/payments/membership.html) | Payment modal and payment flow |
| Razorpay Orders / Payment Verification | Server-side payment gateway API | [apps/payments/views.py](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/apps/payments/views.py) and [infrastructure/razorpay_client.py](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/infrastructure/razorpay_client.py) | Create orders and verify payments |
| TradingView Widget | Frontend embedded chart widget | [templates/markets/overview_v2.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/markets/overview_v2.html) and [templates/research_calls/call_detail.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/research_calls/call_detail.html) | Market and symbol charts |

## Frontend API Call Map

| Frontend File | API Called | Notes |
|---|---|---|
| [templates/markets/overview_v2.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/markets/overview_v2.html) | `/market/api/?type=active` | Loads “Most Active” tab asynchronously |
| [templates/notifications/list.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/notifications/list.html) | `/api/notifications/`, `/api/notifications/?unread=1`, `/api/notifications/mark-read/`, `/api/notifications/mark-all-read/` | Notification inbox page |
| [templates/payments/membership.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/payments/membership.html) | `/payments/create-order/`, `/payments/verify/` | Subscription purchase flow |
| [templates/watchlists/watchlist.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/watchlists/watchlist.html) | `/watchlist/<id>/remove/` | Removes watchlist item with AJAX |
| [templates/admin_panel/dashboard.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/admin_panel/dashboard.html) | `/admin-panel/api/stats/` | Refreshes KPI tiles every 60 seconds |
| [static/js/main.js](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/static/js/main.js) | `/portfolio/add/`, `/watchlist/add/`, `/portfolio/<id>/exit/` | Shared customer action helpers |

## Free Users Who Should Upgrade

### Areas already gated for free or unsubscribed users

| Area | Condition Used | What Is Locked | Upgrade Target |
|---|---|---|---|
| Live research call cards | `call.is_pro_only and not user.subscription` | Full PRO call viewing | `/payments/membership/` |
| Research call detail page | `is_locked = call.status == 'ACTIVE' and not is_pro` | Entry, target, stop loss, rationale, chart context | `/payments/membership/` |
| Dashboard live calls widget | `not user.subscription and call.is_pro_only` | Unlock CTA shown beside premium calls | `/payments/membership/` |
| Customer sidebar | `if not user.subscription` | Upgrade card shown in sidebar | `/payments/membership/` |
| PRO Trades page | `if not is_pro` | Full PRO content replaced with sales page | `/payments/membership/` |
| PRO Baskets page | `if not is_pro` | Full baskets content replaced with locked screen | `/payments/membership/` |
| Profile page | `if not current_subscription.is_active` or no active sub | Upgrade prompts in profile | `/payments/membership/` |

### Files containing upgrade prompts

| File | Upgrade Copy / Behavior |
|---|---|
| [templates/research_calls/live_trades.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/research_calls/live_trades.html) | `Upgrade to View`, `Unlock Call` |
| [templates/research_calls/call_detail.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/research_calls/call_detail.html) | `Upgrade to Pro` overlay |
| [templates/dashboard/customer_dashboard.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/dashboard/customer_dashboard.html) | `Unlock` button for PRO calls |
| [templates/partials/customer_sidebar.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/partials/customer_sidebar.html) | `Upgrade to Pro`, `View Plans` |
| [templates/pro/pro_trades.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/pro/pro_trades.html) | Full upgrade landing screen |
| [templates/pro/baskets.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/pro/baskets.html) | Locked page with `Upgrade to PRO` CTA |
| [templates/authentication/profile.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/authentication/profile.html) | Membership upgrade prompts |
| [templates/partials/navbar.html](c:/Users/karti/OneDrive/Desktop/Stock%20Prediction%20System/templates/partials/navbar.html) | `Start Free` guest onboarding CTA |

## Important Findings

- The seeded plans are `Basic`, `PRO`, and `Premium`; there is no real backend `Free` plan object.
- Most subscription gating uses `user.subscription` as the free-vs-paid check.
- The strongest lock is on research call detail pages for active calls.
- `PRO Trades` and `PRO Baskets` are pure upgrade pages for non-paid users.
- The market ticker partial appears to call the wrong path:
  - Current frontend path: `/api/market/data/?type=ticker`
  - Actual available paths in this project: `/market/api/?type=ticker` and `/api/core/live-ticker/`
- Several REST APIs exist but currently have no frontend consumer in the repository, especially broker, subscription, audit, and some notification preference endpoints.
