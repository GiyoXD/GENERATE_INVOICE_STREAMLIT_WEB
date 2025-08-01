#!/usr/bin/env python3
"""
Real IP Detection for Streamlit using JavaScript injection
This actually gets the real client IP in production
"""

import streamlit as st
import streamlit.components.v1 as components

def get_real_client_ip():
    """Get the real client IP using JavaScript injection"""
    
    # JavaScript code to get the real IP
    js_code = """
    <script>
    // Function to get real IP address
    async function getRealIP() {
        try {
            // Method 1: Try WebRTC (most reliable for real IP)
            const rtcConfig = {
                iceServers: [
                    { urls: 'stun:stun.l.google.com:19302' },
                    { urls: 'stun:stun1.l.google.com:19302' }
                ]
            };
            
            const pc = new RTCPeerConnection(rtcConfig);
            const noop = () => {};
            
            // Create a data channel
            pc.createDataChannel('');
            
            // Create offer and set local description
            const offer = await pc.createOffer();
            await pc.setLocalDescription(offer);
            
            return new Promise((resolve) => {
                pc.onicecandidate = (ice) => {
                    if (!ice || !ice.candidate || !ice.candidate.candidate) return;
                    
                    const candidate = ice.candidate.candidate;
                    const ipMatch = candidate.match(/([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/);
                    
                    if (ipMatch) {
                        const ip = ipMatch[1];
                        // Filter out local IPs
                        if (!ip.startsWith('127.') && 
                            !ip.startsWith('192.168.') && 
                            !ip.startsWith('10.') && 
                            !ip.startsWith('172.')) {
                            pc.close();
                            resolve(ip);
                            return;
                        }
                    }
                };
                
                // Fallback timeout
                setTimeout(() => {
                    pc.close();
                    resolve(null);
                }, 3000);
            });
            
        } catch (error) {
            console.log('WebRTC method failed:', error);
            return null;
        }
    }
    
    // Function to get IP from external service
    async function getIPFromService() {
        try {
            const response = await fetch('https://api.ipify.org?format=json');
            const data = await response.json();
            return data.ip;
        } catch (error) {
            console.log('External service method failed:', error);
            try {
                const response = await fetch('https://httpbin.org/ip');
                const data = await response.json();
                return data.origin.split(',')[0].trim();
            } catch (error2) {
                console.log('Backup service method failed:', error2);
                return null;
            }
        }
    }
    
    // Main function to detect IP
    async function detectIP() {
        const statusDiv = document.getElementById('ip-status');
        statusDiv.innerHTML = '🔍 Detecting your real IP address...';
        
        // Try WebRTC first (gets real IP even behind NAT)
        let realIP = await getRealIP();
        
        if (!realIP) {
            // Fallback to external service
            realIP = await getIPFromService();
        }
        
        if (realIP) {
            statusDiv.innerHTML = `✅ Your real IP: <strong>${realIP}</strong>`;
            
            // Send IP back to Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: realIP
            }, '*');
            
            // Also try to set it in session storage for persistence
            try {
                sessionStorage.setItem('detected_ip', realIP);
            } catch (e) {
                console.log('Could not save to session storage:', e);
            }
            
        } else {
            statusDiv.innerHTML = '❌ Could not detect real IP address';
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: 'detection_failed'
            }, '*');
        }
    }
    
    // Auto-detect when page loads
    window.addEventListener('load', detectIP);
    </script>
    
    <div id="ip-status" style="
        padding: 10px; 
        border: 1px solid #ddd; 
        border-radius: 5px; 
        background: #f9f9f9;
        font-family: Arial, sans-serif;
        text-align: center;
    ">
        🔍 Initializing IP detection...
    </div>
    
    <button onclick="detectIP()" style="
        margin-top: 10px;
        padding: 8px 16px;
        background: #ff4b4b;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-family: Arial, sans-serif;
    ">
        🔄 Detect IP Again
    </button>
    """
    
    # Render the JavaScript component
    detected_ip = components.html(js_code, height=120)
    
    return detected_ip

def set_detected_ip_in_session(ip):
    """Set the detected IP in Streamlit session state"""
    if ip and ip != 'detection_failed' and not ip.startswith('127.'):
        st.session_state['detected_real_ip'] = ip
        st.success(f"✅ Real IP detected and saved: {ip}")
        return True
    return False

# Enhanced get_client_ip that uses the detected real IP
def get_enhanced_client_ip():
    """Get client IP with real IP detection fallback"""
    
    # First check if we have a detected real IP
    if 'detected_real_ip' in st.session_state:
        return st.session_state['detected_real_ip']
    
    # Fall back to the original method
    from login import get_client_ip
    return get_client_ip()

if __name__ == "__main__":
    st.title("🌐 Real IP Detection Test")
    st.write("This will detect your real IP address even in production deployments.")
    
    # Show current detection
    current_ip = get_enhanced_client_ip()
    st.info(f"Current detected IP: {current_ip}")
    
    st.divider()
    st.subheader("Real-time IP Detection")
    
    # Run the real IP detection
    detected_ip = get_real_client_ip()
    
    if detected_ip:
        if set_detected_ip_in_session(detected_ip):
            st.rerun()
    
    # Show session state
    if 'detected_real_ip' in st.session_state:
        st.success(f"✅ Real IP in session: {st.session_state['detected_real_ip']}")
    
    # Manual IP override
    st.divider()
    st.subheader("Manual IP Override")
    manual_ip = st.text_input("Enter your IP manually if detection fails:")
    if st.button("Set Manual IP") and manual_ip:
        st.session_state['detected_real_ip'] = manual_ip
        st.success(f"✅ Manual IP set: {manual_ip}")
        st.rerun()