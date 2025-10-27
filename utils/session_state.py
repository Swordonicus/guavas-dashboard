import streamlit as st

def initialize_session_state():
    """Initialize all session state variables used across the dashboard"""
    
    # Data variables
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    if 'excel_data' not in st.session_state:
        st.session_state.excel_data = None
    
    # Threshold settings
    if 'thresholds' not in st.session_state:
        st.session_state.thresholds = {
            'max_cpl': 50.0,
            'min_conversion_rate': 2.0,
            'max_response_time': 24.0
        }
