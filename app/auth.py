import streamlit as st
from services.api_client import APIClient
import time

def check_auth():
    if st.session_state.get('authenticated'):
        # Check session expiration if implemented
        return True
        
    st.title("Cruise Analytics Login")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("assets/ship_logo.png", width=150)
    
    with col2:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password", autocomplete="current-password")
            
            if st.form_submit_button("Login"):
                if not username or not password:
                    st.error("Please enter both username and password")
                    return False
                
                try:
                    client = APIClient()
                    if client.authenticate(username, password):
                        st.session_state.authenticated = True
                        st.session_state.api_client = client
                        st.session_state.auth_time = time.time()  # For session timeout
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                        # Clear password field on failure
                        st.session_state.login_password = ""
                except Exception as e:
                    st.error(f"Authentication failed: {str(e)}")
    
    return False