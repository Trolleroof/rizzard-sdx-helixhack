#!/usr/bin/env python3
"""Test script to verify Claude API connection."""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env file explicitly
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✓ Loaded .env file from: {env_file}")
    else:
        print(f"✗ .env file not found at: {env_file}")
except ImportError:
    print("⚠ python-dotenv not available, relying on environment variables")

# Check if API key is available
api_key = os.getenv("CLAUDE_API")
if api_key:
    print(f"✓ CLAUDE_API found: {api_key[:20]}...")
else:
    print("✗ CLAUDE_API not found in environment")
    sys.exit(1)

# Test Anthropic client
print("\n" + "=" * 60)
print("Testing Anthropic Claude API")
print("=" * 60)

try:
    from anthropic import Anthropic
    
    client = Anthropic(api_key=api_key)
    print("✓ Anthropic client initialized")
    
    # Make a test call
    print("\nMaking test API call...")
    response = client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Say 'Hello, this is a test!' and nothing else."
            }
        ]
    )
    
    print("✓ API call successful!")
    print(f"\nResponse: {response.content[0].text}")
    print("\n" + "=" * 60)
    print("✓ All tests passed! Claude API is working correctly.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

