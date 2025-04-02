import streamlit as st
from .auth import check_auth
from .pages import dashboard, metrics, ratings

def main():
    st.set_page_config(
        page_title="Cruise Analytics",
        page_icon="🚢",
        layout="wide"
    )
    
    if not check_auth():
        return
    
    # Navigation
    pages = {
        "Dashboard": dashboard.show,
        "Ratings Summary": ratings.show,
        "Metric Comparison": metrics.show
    }
    
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(pages.keys()))
    pages[selection]()
    
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({'authenticated': False}))

if __name__ == "__main__":
    main()