"""
WSGI config for expense_tracker project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import threading
import time
import requests

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')

application = get_wsgi_application()

def keep_alive():
    url = os.environ.get('RENDER_EXTERNAL_URL')
    if not url:
        return
        
    while True:
        time.sleep(480)  # Wait 8 minutes
        try:
            requests.get(url, timeout=10)
            print("Successfully pinged keep-alive url")
        except Exception as e:
            print(f"Keep-alive ping failed: {e}")

# Start the keep-alive thread as a daemon so it doesn't block shutdown
if os.environ.get('RENDER_EXTERNAL_URL'):
    thread = threading.Thread(target=keep_alive, daemon=True)
    thread.start()
