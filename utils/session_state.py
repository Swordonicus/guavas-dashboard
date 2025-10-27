import streamlit as st

DEFAULT_THRESHOLDS = {
    'max_cpl': 50.0,
    'min_conversion_rate': 2.0,
    'max_response_time': 24.0,
    'min_leads_per_week': 10.0,
    'partner_inactive_days': 60.0,   # added
    'content_overdue_days': 7.0      # added
}

def initialize_session_state():
    """Initialize all session state variables used across the dashboard"""
    # Data vars
    st.session_state.setdefault('data_loaded', False)
    st.session_state.setdefault('excel_data', None)

    # Thresholds (backfill new keys without overwriting user values)
    if 'thresholds' not in st.session_state:
        st.session_state.thresholds = DEFAULT_THRESHOLDS.copy()
    else:
        for k, v in DEFAULT_THRESHOLDS.items():
            st.session_state.thresholds.setdefault(k, v)
