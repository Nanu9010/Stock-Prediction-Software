# Real-Time Stock Market Data Architecture for StockPro

This document outlines the architecture, data flow, and operational procedures for building the real-time stock market data system for StockPro, strictly following a multi-tiered fallback approach to guarantee continuous data availability without incurring excessive API costs.

---

## 1. Service Architecture Overview

The system abstracts market data fetching from the business logic layer. Frontend components do not call third-party APIs directly, nor do they block waiting for slow downstream HTTP requests.

### Core Components:
1. **Market Data Service (`apps/market_data/services.py`)**: The business-facing API. Serves formatted data to the Django views/serializers.
2. **Provider Abstraction Layer (`infrastructure/market_data_client.py`)**: A unified interface that wraps multiple downstream data providers.
3. **Redis Caching Layer**: Ultra-fast storage for intraday quotes, market movers, and temporary failures.
4. **PostgreSQL Database Cache**: Persistent fallback (Last-Known-Good) and historical EOD data storage.
5. **Celery Workers**: Background schedulers responsible for refreshing the cache proactively.
6. **Websocket Server (Django Channels)**: Pushes real-time ticks to connected clients.

---

## 2. Provider Wrappers & Abstraction

The `MarketDataClient` must implement a unified interface (`fetch_price`, `get_history`, `get_movers`). It queries providers in a strict cascading order.

### Provider Hierarchy (Free Tier Optimization):
1. **Primary**: Unofficial NSE JSON APIs (Ultra-low latency for Indian markets).
2. **Secondary**: Yahoo Finance (`yfinance`) (Reliable fallback for global/Indian stocks, indices, commodities).
3. **Tertiary**: TwelveData Free Tier (Fallback for exact intraday limits).
4. **Quaternary**: AlphaVantage Free Tier (Fallback for historical OHLCV).

### Abstraction Rules:
- **No Provider Leakage**: The rest of the app must never know *which* provider served the data. Responses must be standardized to a canonical StockPro JSON schema.
- **Freshness Metadata**: Every response must include a `provider_used` and `timestamp` field so the frontend can display an "As of [Time]" indicator.

---

## 3. Symbol Normalization Rules

Providers use different symbol formats (e.g., `RELIANCE` vs `RELIANCE.NS` vs `^NSEI`). The system enforces strict normalization rules:

- **Canonical Format**: The system standardizes on pure NSE symbols for equities (`RELIANCE`, `TCS`).
- **Translation Matrix**: The `MarketDataClient` contains a mapping dictionary:
  - *NSE to yfinance*: Append `.NS` (e.g., `RELIANCE` → `RELIANCE.NS`).
  - *Indices to yfinance*: Map custom strings (e.g., `NIFTY50` → `^NSEI`, `SENSEX` → `^BSESN`).
  - *Global/Commodities*: Explicit mapping (e.g., `GOLD` → `GC=F`).

---

## 4. Redis Strategy & Cache Invalidation

Frontend requests hit the Redis cache **first**. If a cache miss occurs, the system fetches the data, caches it, and returns it. To prevent blocking the user, if the fetch takes too long, the system returns DB Last-Known-Good data and queues a background refresh.

### Redis Keys & TTLs:
- **Live Ticker Strip**: `market_ticker_data` (TTL: 60 seconds)
- **Individual Stock Quote**: `quote:NSE:{symbol}` (TTL: 30 seconds)
- **Top Gainers/Losers**: `market_movers:{limit}` (TTL: 120 seconds)
- **Market Breadth/Sectors**: `sector_perf:{sector}` (TTL: 300 seconds)

### Invalidation Strategy:
- **Time-Based Expiration**: Most keys expire naturally based on TTL.
- **Pre-emptive Warming**: Celery jobs overwrite keys *before* they expire during market hours, effectively making cache misses near zero for popular symbols.

---

## 5. Database Caching Strategy (Last-Known-Good)

The PostgreSQL database acts as a durable fallback and historical record.

- **Models**: `StockPrice`, `MarketIndex`, `GainersLosers` act as persistent snapshots.
- **EOD Snapshotting**: At the end of the trading day, current prices are committed to historical OHLCV tables.
- **Fallback Rule**: If Redis is empty AND all providers fail/timeout, the `services.py` layer reads the last updated row from `StockPrice` or `MarketIndex`.

---

## 6. Scheduled Refresh Jobs (Celery)

Background jobs prevent the user from experiencing the latency of external API calls.

### Scheduled Tasks (During Market Hours: 9:15 AM - 3:30 PM IST):
1. **`task_update_indices`**: Runs every 1 minute. Fetches top 5 indices, writes to Redis and DB.
2. **`task_update_gainers_active`**: Runs every 3 minutes. Fetches top 20 gainers, losers, and active stocks.
3. **`task_update_popular_stocks`**: Runs every 5 minutes. Updates the top 50 most viewed stocks on the platform.
4. **`task_daily_historical_sync`**: Runs at 6:00 PM IST. Downloads daily OHLCV candles for all active symbols and persists to DB.

---

## 7. Websocket Architecture (Django Channels)

For sub-second updates on the trading dashboard:
- **Channel Groups**: Clients subscribe to specific groups (e.g., `quote_RELIANCE`, `live_ticker`).
- **Publisher**: When Celery updates Redis with a new price, it triggers a `channel_layer.group_send()` event.
- **Payload**: Minimal JSON containing `{"symbol": "RELIANCE", "ltp": 2500.50, "change": 12.5, "change_pct": 0.5, "ts": 1700000000}`.
- **Throttling**: The server throttles outbound WS messages to a maximum of 1 per second per symbol to prevent frontend rendering lag.

---

## 8. Failover, Circuit Breakers & Outage Behavior

### Circuit Breakers:
- If a provider (e.g., NSE JSON) returns 5 consecutive errors or timeouts (HTTP 429/403/500), the Circuit Breaker "opens" for that provider for 5 minutes.
- Traffic is automatically routed to the next provider (Yahoo Finance).

### Rate Limit Handling:
- TwelveData and AlphaVantage have strict API limits (e.g., 5 requests/min).
- The client wraps these in a Token Bucket rate limiter. If limits are hit, it immediately falls back to Database Last-Known-Good data rather than waiting.

### Partial Outage Behavior (Graceful Degradation):
- **Provider Down**: System seamlessly degrades to secondary providers.
- **All Providers Down**: System returns Database Last-Known-Good data. The UI displays an amber indicator: *"Live feed delayed. Showing last known prices."*
- **Redis Down**: System bypasses Redis and queries the PostgreSQL DB directly, disabling live websocket pushes until Redis recovers.
- **Never Hardcode**: The system will never hardcode a default price; if absolutely no data exists for a new symbol, it returns an explicit `{"error": "Data unavailable"}` to be handled gracefully by the UI.

---

## 9. Market Freshness Policy

- **Market Open (9:15 AM - 3:30 PM IST)**: Cache TTLs are strictly enforced (30s - 120s). Celery jobs run continuously. UI shows green "LIVE" indicator.
- **Market Closed (Post 3:30 PM IST / Weekends)**: 
  - Celery jobs suspend execution.
  - Redis TTLs are set to "infinite" (or bypassed).
  - API provider calls are suspended to save quota.
  - UI shows a gray "MARKET CLOSED" indicator. Data is served from DB.
