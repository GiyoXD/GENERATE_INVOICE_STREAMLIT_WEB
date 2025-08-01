#!/usr/bin/env python3
"""
Test IP detection functionality
"""

import sys
sys.path.append('.')
from login import get_client_ip, get_user_agent

def test_ip_detection():
    """Test the IP detection functionality"""
    print("🌐 Testing IP Detection")
    print("=" * 40)
    
    # Test IP detection
    print("Testing IP detection...")
    client_ip = get_client_ip()
    print(f"Detected IP: {client_ip}")
    
    if client_ip == "127.0.0.1":
        print("⚠️  Using localhost IP (normal for local development)")
    else:
        print("✅ Detected non-localhost IP (good for production)")
    
    # Test user agent detection
    print("\nTesting User Agent detection...")
    user_agent = get_user_agent()
    print(f"Detected User Agent: {user_agent}")
    
    # Additional network info
    print("\nAdditional Network Information:")
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Hostname: {hostname}")
        print(f"Local IP: {local_ip}")
        
        # Try to get external IP
        try:
            import requests
            response = requests.get('https://httpbin.org/ip', timeout=5)
            if response.status_code == 200:
                external_ip = response.json().get('origin', 'Unknown')
                print(f"External IP: {external_ip}")
            else:
                print("External IP: Could not determine")
        except Exception as e:
            print(f"External IP: Error - {e}")
            
    except Exception as e:
        print(f"Network info error: {e}")
    
    print("\n" + "=" * 40)
    print("IP Detection Test Complete")

if __name__ == "__main__":
    test_ip_detection()