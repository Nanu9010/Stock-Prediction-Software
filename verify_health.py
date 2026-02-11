
import os
import sys
import django
from django.test import Client

# Setup Django
sys.path.append(r'c:\Users\karti\OneDrive\Desktop\Stock Prediction System')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

if __name__ == "__main__":
    print("Starting Health Check...")
    client = Client()
    
    urls = [
        '/',
        '/dashboard/',
        '/auth/login/',
        '/calls/', 
        '/admin/login/'
    ]

    for url in urls:
        try:
            response = client.get(url, follow=True)
            print(f"URL: {url} | Status: {response.status_code}")
            if response.status_code != 200:
                print(f"WARNING: {url} returned {response.status_code}")
        except Exception as e:
            print(f"ERROR accessing {url}: {e}")

    print("Health Check Complete.")
