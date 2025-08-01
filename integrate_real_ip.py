#!/usr/bin/env python3
"""
Integration script to add real IP detection to your app
Add this to your main app.py or login page
"""

import streamlit as st
import streamlit.components.v1 as components

def setup_real_ip_detection():
    """Set up real IP detection for the session"""
    
    # Only run once per session
    if 'ip_detection_attempted' not in st.session_state:
        st.session_state['ip_detection_attempted'] = True
        
        # Inject JavaScript to detect real IP
        js_code = """
        <div style="display: none;">
            <script>
            async function detectRealIP() {
                try {
                    // Try primary service
                    const response = await fetch('https://api.ipify.org?format=json');
                    const data = await response.json();
                    const realIP = data.ip;
                    
                    if (realIP && realIP !== '127.0.0.1') {
                        // Send back to Streamlit
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: realIP
                        }, '*');
                        return;
                    }
                } catch (error) {
                    console.log('Primary IP detection failed:', error);
                }
                
                // Fallback method
                try {
                    const response2 = await fetch('https://httpbin.org/ip');
                    const data2 = await response2.json();
                    const fallbackIP = data2.origin.split(',')[0].trim();
                    
                    if (fallbackIP && fallbackIP !== '127.0.0.1') {
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: fallbackIP
                        }, '*');
                        return;
                    }
                } catch (error2) {
                    console.log('Fallback IP detection failed:', error2);
                }
                
                // Signal detection failed
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: 'detection_failed'
                }, '*');
            }
            
            // Auto-run detection
            detectRealIP();
            </script>
        </div>
        """
        
        # Run the detection
        detected_ip = components.html(js_code, height=0)
        
        # Store the detected IP
        if detected_ip:
            try:
                if str(detected_ip) != 'detection_failed' and not str(detected_ip).startswith('127.'):
                    st.session_state['real_client_ip'] = str(detected_ip)
                    return str(detected_ip)
            except:
                pass
    
    # Return stored IP if available
    return st.session_state.get('real_client_ip', '127.0.0.1')

# Example usage in your app
if __name__ == "__main__":
    st.title("🌐 Real IP Detection Integration")
    
    # Set up IP detection
    real_ip = setup_real_ip_detection()
    
    # Show results
    if real_ip != '127.0.0.1':
        st.success(f"✅ Real IP detected: **{real_ip}**")
    else:
        st.info("🔍 Detecting your real IP address...")
        
        # Show a refresh button
        if st.button("🔄 Refresh to detect IP"):
            if 'ip_detection_attempted' in st.session_state:
                del st.session_state['ip_detection_attempted']
            st.rerun()
    
    # Show current IP from login system
    st.divider()
    st.subheader("Current IP Detection")
    
    try:
        from login import get_client_ip
        current_ip = get_client_ip()
        st.info(f"Login system IP: {current_ip}")
    except:
        st.error("Could not import get_client_ip from login.py")
    
    # Integration instructions
    st.divider()
    st.subheader("📋 Integration Instructions")
    
    st.write("**To integrate this into your app:**")
    st.write("1. Add this code to the top of your main app.py or login page:")
    
    integration_code = '''
# Add to the top of your app.py
from integrate_real_ip import setup_real_ip_detection

# Add this line early in your app (before authentication)
real_ip = setup_real_ip_detection()
'''
    
    st.code(integration_code, language='python')
    
    st.write("2. The real IP will be automatically stored in `st.session_state['real_client_ip']`")
    st.write("3. Your `get_client_ip()` function will now use the real IP when available")
    
    # Show session state
    st.divider()
    st.subheader("🔍 Debug Info")
    st.write("Session state:")
    st.json({
        'real_client_ip': st.session_state.get('real_client_ip', 'Not detected'),
        'ip_detection_attempted': st.session_state.get('ip_detection_attempted', False)
    })