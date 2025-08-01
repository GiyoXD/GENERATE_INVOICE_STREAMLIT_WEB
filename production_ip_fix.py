#!/usr/bin/env python3
"""
Production IP Fix - Simple solution for real IP detection
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import os

def inject_ip_detector():
    """Inject JavaScript to detect real IP and return it"""
    
    js_code = f"""
    <div id="ip-detector" style="display: none;">
        <script>
        async function detectRealIP() {{
            try {{
                // Method 1: Try ipify service
                const response = await fetch('https://api.ipify.org?format=json');
                const data = await response.json();
                const realIP = data.ip;
                
                if (realIP && realIP !== '127.0.0.1') {{
                    // Send back to Streamlit
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: realIP
                    }}, '*');
                    
                    console.log('Real IP detected:', realIP);
                    return realIP;
                }}
            }} catch (error) {{
                console.log('IP detection failed:', error);
                
                // Fallback method
                try {{
                    const response2 = await fetch('https://httpbin.org/ip');
                    const data2 = await response2.json();
                    const fallbackIP = data2.origin.split(',')[0].trim();
                    
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: fallbackIP
                    }}, '*');
                    
                    return fallbackIP;
                }} catch (error2) {{
                    console.log('Fallback IP detection failed:', error2);
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: 'detection_failed'
                    }}, '*');
                }}
            }}
        }}
        
        // Auto-run detection
        detectRealIP();
        </script>
    </div>
    """
    
    # This will return the detected IP
    detected_ip = components.html(js_code, height=0)
    return detected_ip

def get_production_ip():
    """Get real IP for production use"""
    
    # Check if we already have a detected IP in session
    if 'real_client_ip' in st.session_state and st.session_state['real_client_ip'] != '127.0.0.1':
        return st.session_state['real_client_ip']
    
    # Try to detect IP using JavaScript injection
    detected_ip = inject_ip_detector()
    
    if detected_ip and detected_ip != 'detection_failed' and not detected_ip.startswith('127.'):
        st.session_state['real_client_ip'] = detected_ip
        return detected_ip
    
    # Fallback: Try server-side detection
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        if response.status_code == 200:
            server_ip = response.json().get('ip', '127.0.0.1')
            if server_ip != '127.0.0.1':
                st.session_state['real_client_ip'] = server_ip
                return server_ip
    except:
        pass
    
    # Final fallback
    return '127.0.0.1'

# Simple integration function
def update_login_with_real_ip():
    """Update the login.py get_client_ip function to use real IP detection"""
    
    # This is what you should add to your login.py
    integration_code = '''
# Add this to the top of login.py
import streamlit.components.v1 as components

def get_real_ip_via_js():
    """Get real IP using JavaScript injection"""
    if 'real_client_ip' in st.session_state:
        return st.session_state['real_client_ip']
    
    js_code = """
    <script>
    fetch('https://api.ipify.org?format=json')
        .then(response => response.json())
        .then(data => {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: data.ip
            }, '*');
        })
        .catch(() => {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: 'detection_failed'
            }, '*');
        });
    </script>
    """
    
    detected_ip = components.html(js_code, height=0)
    if detected_ip and detected_ip != 'detection_failed':
        st.session_state['real_client_ip'] = detected_ip
        return detected_ip
    
    return '127.0.0.1'

# Then modify your get_client_ip function to use this:
def get_client_ip():
    """Get client IP address - production ready"""
    
    # Try to get real IP first
    real_ip = get_real_ip_via_js()
    if real_ip != '127.0.0.1':
        return real_ip
    
    # Your existing fallback methods here...
    return "127.0.0.1"
'''
    
    return integration_code

if __name__ == "__main__":
    st.title("🌐 Production IP Detection Fix")
    
    st.write("This will detect your real IP address in production.")
    
    # Show current IP
    current_ip = get_production_ip()
    
    if current_ip != '127.0.0.1':
        st.success(f"✅ Real IP detected: **{current_ip}**")
    else:
        st.warning("⚠️ Still showing localhost IP")
    
    # Show integration code
    st.divider()
    st.subheader("Integration Code")
    st.write("Add this code to your `login.py` file:")
    
    integration_code = update_login_with_real_ip()
    st.code(integration_code, language='python')
    
    # Manual override
    st.divider()
    st.subheader("Manual Override")
    manual_ip = st.text_input("Enter your real IP manually:")
    if st.button("Set Manual IP") and manual_ip:
        st.session_state['real_client_ip'] = manual_ip
        st.success(f"✅ IP set to: {manual_ip}")
        st.rerun()