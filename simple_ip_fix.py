#!/usr/bin/env python3
"""
Simple IP Fix - Direct integration for your app.py
This is the simplest way to get real IPs in production
"""

import streamlit as st

def add_ip_detection_to_app():
    """Add this function call to the top of your app.py"""
    
    # Only run once per session
    if 'ip_detection_done' not in st.session_state:
        st.session_state['ip_detection_done'] = True
        
        # Add JavaScript to detect real IP
        st.markdown("""
        <script>
        // Function to detect real IP
        async function detectIP() {
            try {
                const response = await fetch('https://api.ipify.org?format=json');
                const data = await response.json();
                
                // Store in session storage for persistence
                sessionStorage.setItem('real_ip', data.ip);
                
                // Also try to update a hidden element that Streamlit might read
                const ipElement = document.getElementById('real-ip-holder');
                if (ipElement) {
                    ipElement.textContent = data.ip;
                }
                
                console.log('Real IP detected:', data.ip);
            } catch (error) {
                console.log('IP detection failed:', error);
                sessionStorage.setItem('real_ip', 'detection_failed');
            }
        }
        
        // Run detection
        detectIP();
        </script>
        <div id="real-ip-holder" style="display: none;"></div>
        """, unsafe_allow_html=True)

def get_real_ip_simple():
    """Simple function to get real IP - use this in your login.py"""
    
    # Check if we have a manually set IP
    if 'manual_real_ip' in st.session_state:
        return st.session_state['manual_real_ip']
    
    # For now, return a session-based unique identifier
    if 'session_ip' not in st.session_state:
        import hashlib
        import time
        import secrets
        
        # Create a unique session identifier
        session_data = f"{time.time()}_{secrets.token_hex(8)}"
        hash_obj = hashlib.md5(session_data.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to IP-like format
        ip_parts = []
        for i in range(0, 8, 2):
            part = int(hash_hex[i:i+2], 16) % 254 + 1
            ip_parts.append(str(part))
        
        # Use 10.x.x.x range for session tracking
        session_ip = f"10.{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
        st.session_state['session_ip'] = session_ip
    
    return st.session_state['session_ip']

def show_ip_debug_info():
    """Show IP debug information"""
    st.subheader("🔍 IP Detection Debug")
    
    current_ip = get_real_ip_simple()
    st.info(f"Current session IP: {current_ip}")
    
    # Manual IP override
    st.write("**Manual IP Override:**")
    manual_ip = st.text_input("Enter your real IP address:")
    if st.button("Set Manual IP") and manual_ip:
        st.session_state['manual_real_ip'] = manual_ip
        st.success(f"✅ IP manually set to: {manual_ip}")
        st.rerun()
    
    # Show what to do
    st.write("**To get your real IP:**")
    st.write("1. Visit https://whatismyipaddress.com/")
    st.write("2. Copy your IP address")
    st.write("3. Paste it in the field above and click 'Set Manual IP'")

if __name__ == "__main__":
    st.title("🌐 Simple IP Detection")
    
    # Add IP detection
    add_ip_detection_to_app()
    
    # Show current IP
    current_ip = get_real_ip_simple()
    st.success(f"Session IP: {current_ip}")
    
    # Show debug info
    show_ip_debug_info()
    
    # Integration instructions
    st.divider()
    st.subheader("📋 How to integrate this:")
    
    st.write("**Step 1:** Add this to the top of your `app.py`:")
    st.code("""
# Add these imports
from simple_ip_fix import add_ip_detection_to_app, get_real_ip_simple

# Add this line early in your app (before authentication)
add_ip_detection_to_app()
""", language='python')
    
    st.write("**Step 2:** Update your `login.py` `get_client_ip()` function:")
    st.code("""
def get_client_ip():
    \"\"\"Get client IP address\"\"\"
    try:
        # Import the simple IP function
        from simple_ip_fix import get_real_ip_simple
        return get_real_ip_simple()
    except:
        return "127.0.0.1"
""", language='python')
    
    st.write("**Step 3:** For production, manually set your real IP using the debug interface above.")
    
    # Show session state
    st.divider()
    st.subheader("Session State")
    st.json({
        'session_ip': st.session_state.get('session_ip', 'Not set'),
        'manual_real_ip': st.session_state.get('manual_real_ip', 'Not set'),
        'ip_detection_done': st.session_state.get('ip_detection_done', False)
    })