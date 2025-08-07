#!/usr/bin/env python3
"""Debug environment variables loading"""
import os
from dotenv import load_dotenv

print("=== Environment Debug ===")

# Check before loading .env
print(f"BFL_API_KEY before load_dotenv: {os.getenv('BFL_API_KEY', 'NOT FOUND')}")

# Load .env file
load_dotenv()

# Check after loading .env
api_key = os.getenv('BFL_API_KEY')
print(f"BFL_API_KEY after load_dotenv: {api_key[:10] + '...' if api_key else 'NOT FOUND'}")

# Check .env file directly
print("\n=== .env file contents ===")
try:
    with open('.env', 'r') as f:
        content = f.read()
        print(content)
except Exception as e:
    print(f"Error reading .env: {e}")

# Check current working directory
print(f"\nCurrent directory: {os.getcwd()}")

# Test the flux processor
print("\n=== Testing flux processor ===")
try:
    from flux_processor import get_processor
    processor = get_processor(api_key)
    print(f"Processor API key: {processor.api_key[:10] + '...' if processor.api_key else 'NOT FOUND'}")
except Exception as e:
    print(f"Error creating processor: {e}")