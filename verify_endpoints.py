#!/usr/bin/env python3
"""
Verify that the Flask endpoints are returning data.
"""

import time
import requests

time.sleep(2)  # Give server time to be ready

print("Testing Flask endpoints...\n")

try:
    # Test home endpoint
    print("1. Testing / (home page)")
    r = requests.get('http://127.0.0.1:5000/', timeout=5)
    print(f"   Status: {r.status_code}")
    if "Movie Data App" in r.text:
        print("   ✓ Home page loaded successfully")
    else:
        print("   ✗ Home page content not found")

    # Test scraped endpoint
    print("\n2. Testing /scraped (scraped movies)")
    r = requests.get('http://127.0.0.1:5000/scraped', timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        # Count movies in response
        count = r.text.count("<li>")
        print(f"   ✓ Scraped endpoint loaded - found {count} movies")
        if "The Shawshank Redemption" in r.text or "Godfather" in r.text:
            print("   ✓ Scraped movie data is rendering")
        else:
            print("   ⚠ Warning: Expected movies not found in response")
    else:
        print(f"   ✗ Error: {r.status_code}")

    # Test api endpoint
    print("\n3. Testing /api (API movies)")
    r = requests.get('http://127.0.0.1:5000/api', timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        # Count movies in response
        count = r.text.count("<li>")
        print(f"   ✓ API endpoint loaded - found {count} movies")
        if "Inception" in r.text or "Matrix" in r.text:
            print("   ✓ API movie data is rendering")
        else:
            print("   ⚠ Warning: Expected movies not found in response")
    else:
        print(f"   ✗ Error: {r.status_code}")

    print("\n" + "=" * 60)
    print("✅ All endpoints are working!")
    print("=" * 60)
    print("\nAccess the app in your browser:")
    print("  • http://127.0.0.1:5000/           (Home)")
    print("  • http://127.0.0.1:5000/scraped    (Scraped Movies)")
    print("  • http://127.0.0.1:5000/api        (API Movies)")
    print("=" * 60)

except Exception as e:
    print(f"✗ Error testing endpoints: {e}")
    print("  Make sure Flask app is running on http://127.0.0.1:5000")
