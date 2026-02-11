# Quick Setup Guide - Installing Dependencies

## Issue: yfinance Module Not Found

The platform requires `yfinance` and other packages to be installed in your virtual environment.

## Solution 1: Install Using python -m pip (RECOMMENDED)

```bash
# Make sure you're in the virtual environment
cd "c:\Users\karti\OneDrive\Desktop\Stock Prediction System"

# Install packages using python -m pip
python -m pip install yfinance pandas numpy plotly

# Or install without specific versions (latest)
python -m pip install yfinance pandas numpy plotly
```

## Solution 2: Install from requirements.txt

```bash
python -m pip install -r requirements.txt
```

## Solution 3: Recreate Virtual Environment (If above fails)

```bash
# Deactivate current venv
deactivate

# Delete old venv folder
Remove-Item -Recurse -Force venv

# Create new venv
python -m venv venv

# Activate new venv
.\venv\Scripts\activate

# Install all requirements
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## After Installation

Once packages are installed, run:

```bash
# Create market data tables
python manage.py makemigrations market_data
python manage.py migrate

# Populate initial data (20 popular stocks + indices)
python manage.py setup_market_data

# Start server
python manage.py runserver
```

## Access Your Platform

- **Live Trades (Cards):** http://127.0.0.1:8000/calls/
- **Closed Trades:** http://127.0.0.1:8000/calls/closed/
- **Market Indices:** http://127.0.0.1:8000/market/indices/
- **Admin Panel:** http://127.0.0.1:8000/admin/

## Verify Installation

```python
# Test yfinance
python -c "import yfinance; print('yfinance installed successfully!')"

# Test pandas
python -c "import pandas; print('pandas installed successfully!')"
```

## Common Issues

### 1. Permission Denied
- Run PowerShell as Administrator
- Or use: `python -m pip install --user yfinance pandas numpy plotly`

### 2. Pip Corrupted
```bash
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### 3. Virtual Environment Issues
- Make sure `(venv)` appears in your terminal prompt
- If not, run: `.\venv\Scripts\activate`

## What's Installed

- **yfinance** - Free Yahoo Finance API for stock prices
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **plotly** - Interactive charts

**All FREE - No API keys needed!**
