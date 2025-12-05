import threading
import time
import sys
from pathlib import Path
import requests

# Ensure project root is on sys.path so `from app import app` works
ROOT = str(Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app

def run_server():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

thr = threading.Thread(target=run_server, daemon=True)
thr.start()

time.sleep(1)
try:
    r = requests.get('http://127.0.0.1:5000/', timeout=3)
    print('status', r.status_code)
    print('body snippet:', r.text[:200])
except Exception as e:
    print('request failed:', type(e).__name__, e)
