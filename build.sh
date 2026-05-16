#!/bin/bash

# Install dependencies (redundant but safe)
python3.12 -m pip install -r requirements.txt

# Run collectstatic
echo "Collecting static files..."
python3.12 manage.py collectstatic --noinput

echo "Build finished."
