#!/usr/bin/env python3
"""
Production IP Detection and Configuration
Use this to detect and configure the correct IP for production
"""

import sys
import os
import json
sys.path.append('.')

def detect_production_ip():
    """Detect the production IP address"""
    print("🌐 Production IP Detection")
    print("=" * 50)
    
    detected_ips = {}
    
    # Method 1: External IP via HTTP service
    try:
        import requests
        print("1. Checking external IP via httpbin.org...")
        response = requests.get('https://httpbin.org/ip', timeout=10)
        if response.status_code == 200:
            external_ip = response.json().get('origin', '').split(',')[0].strip()
            detected_ips['external_httpbin'] = external_ip
            print(f"   External IP: {external_ip}")
        else:
            print("   Failed to get external IP")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 2: Alternative external IP service
    try:
        import requests
        print("2. Checking external IP via ipify.org...")
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        if response.status_code == 200:
            external_ip = response.json().get('ip', '').strip()
            detected_ips['external_ipify'] = external_ip
            print(f"   External IP: {external_ip}")
        else:
            print("   Failed to get external IP")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 3: Local network IP
    try:
        import socket
        print("3. Checking local network IP...")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        detected_ips['local_network'] = local_ip
        print(f"   Local network IP: {local_ip}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 4: Hostname resolution
    try:
        import socket
        print("4. Checking hostname resolution...")
        hostname = socket.gethostname()
        host_ip = socket.gethostbyname(hostname)
        detected_ips['hostname'] = host_ip
        print(f"   Hostname: {hostname}")
        print(f"   Hostname IP: {host_ip}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 5: Environment variables
    print("5. Checking environment variables...")
    env_vars = ['HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR', 'SERVER_ADDR', 'HTTP_X_REAL_IP']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            detected_ips[f'env_{var.lower()}'] = value
            print(f"   {var}: {value}")
    
    if not any(os.environ.get(var) for var in env_vars):
        print("   No relevant environment variables found")
    
    # Summary
    print("\n" + "=" * 50)
    print("DETECTED IP ADDRESSES:")
    print("=" * 50)
    
    if detected_ips:
        for source, ip in detected_ips.items():
            print(f"{source:20}: {ip}")
        
        # Recommend the best IP
        print("\n" + "=" * 50)
        print("RECOMMENDATION:")
        print("=" * 50)
        
        # Prefer external IPs for production
        if 'external_httpbin' in detected_ips and detected_ips['external_httpbin'] != '127.0.0.1':
            recommended_ip = detected_ips['external_httpbin']
            print(f"✅ Recommended IP: {recommended_ip} (External IP)")
        elif 'external_ipify' in detected_ips and detected_ips['external_ipify'] != '127.0.0.1':
            recommended_ip = detected_ips['external_ipify']
            print(f"✅ Recommended IP: {recommended_ip} (External IP)")
        elif 'local_network' in detected_ips and not detected_ips['local_network'].startswith('127.'):
            recommended_ip = detected_ips['local_network']
            print(f"✅ Recommended IP: {recommended_ip} (Local Network IP)")
        else:
            recommended_ip = list(detected_ips.values())[0] if detected_ips else '127.0.0.1'
            print(f"⚠️  Using: {recommended_ip} (Best available)")
        
        # Save configuration
        config = {
            'production_ip': recommended_ip,
            'detected_ips': detected_ips,
            'detection_timestamp': str(datetime.now())
        }
        
        try:
            os.makedirs('data/config', exist_ok=True)
            with open('data/config/ip_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            print(f"💾 Configuration saved to data/config/ip_config.json")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
        
    else:
        print("❌ No IP addresses detected!")
    
    return detected_ips

def set_production_ip():
    """Interactive IP configuration"""
    detected_ips = detect_production_ip()
    
    if not detected_ips:
        print("\n❌ No IPs detected. Using manual input.")
        manual_ip = input("Enter your production IP address: ").strip()
        if manual_ip:
            detected_ips['manual'] = manual_ip
    
    if detected_ips:
        print("\n" + "=" * 50)
        print("IP CONFIGURATION")
        print("=" * 50)
        
        # Show options
        ip_list = list(detected_ips.items())
        for i, (source, ip) in enumerate(ip_list, 1):
            print(f"{i}. {ip} ({source})")
        
        # Get user choice
        while True:
            try:
                choice = input(f"\nSelect IP to use (1-{len(ip_list)}) or press Enter for auto: ").strip()
                if not choice:
                    # Auto-select best IP
                    if any(not ip.startswith('127.') for _, ip in ip_list):
                        selected_ip = next(ip for _, ip in ip_list if not ip.startswith('127.'))
                    else:
                        selected_ip = ip_list[0][1]
                    break
                else:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(ip_list):
                        selected_ip = ip_list[choice_idx][1]
                        break
                    else:
                        print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        print(f"\n✅ Selected IP: {selected_ip}")
        
        # Update the get_client_ip function to use this IP
        print("💡 To use this IP in production, you can:")
        print("1. Set environment variable: export PRODUCTION_IP=" + selected_ip)
        print("2. Or modify the get_client_ip() function to return this IP")
        
        return selected_ip
    
    return None

if __name__ == "__main__":
    from datetime import datetime
    set_production_ip()