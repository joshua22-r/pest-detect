#!/usr/bin/env python
"""Test social login endpoint with mock tokens"""
import os
import sys
import django
import json
import requests
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def test_social_login():
    """Test social login with mock tokens"""
    
    base_url = 'http://localhost:8000/api'
    
    # Test 1: Google mock token
    print("\n" + "="*60)
    print("Testing Google Social Login with Mock Token")
    print("="*60)
    
    google_mock_token = f'mock_google_token_{int(datetime.now().timestamp())}'
    payload = {
        'provider': 'google',
        'access_token': google_mock_token
    }
    
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f'{base_url}/auth/social-login/',
            json=payload,
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Google mock login SUCCESS")
            data = response.json()
            print(f"   - User email: {data['user']['email']}")
            print(f"   - Access token received: {'access' in data}")
        else:
            print(f"❌ Google mock login FAILED")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Facebook mock token
    print("\n" + "="*60)
    print("Testing Facebook Social Login with Mock Token")
    print("="*60)
    
    facebook_mock_token = f'mock_facebook_token_{int(datetime.now().timestamp())}'
    payload = {
        'provider': 'facebook',
        'access_token': facebook_mock_token
    }
    
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f'{base_url}/auth/social-login/',
            json=payload,
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Facebook mock login SUCCESS")
            data = response.json()
            print(f"   - User email: {data['user']['email']}")
            print(f"   - Access token received: {'access' in data}")
        else:
            print(f"❌ Facebook mock login FAILED")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)

if __name__ == '__main__':
    test_social_login()
