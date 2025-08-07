#!/usr/bin/env python3
"""
Simple test for BFL API authentication
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_bfl_api():
    """Test BFL API authentication"""
    api_key = os.getenv('BFL_API_KEY')
    print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")
    
    if not api_key:
        print("ERROR: No BFL_API_KEY found in .env file")
        return
    
    # Test endpoints
    test_url = "https://api.bfl.ai/v1/flux-kontext-max"
    
    headers = {
        "accept": "application/json",
        "x-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Simple test payload
    payload = {
        "prompt": "a simple test image",
        "model": "flux-kontext-max"
    }
    
    print(f"Testing URL: {test_url}")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")
    
    try:
        response = requests.post(test_url, headers=headers, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API authentication successful!")
        elif response.status_code == 403:
            print("❌ Authentication failed - check your API key")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_bfl_api()