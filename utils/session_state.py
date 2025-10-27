import streamlit as st

DEFAULT_THRESHOLDS = {
    'max_cpl': 50.0,
    'min_conversion_rate': 2.0,
    'max_response_time': 24.0,
    'min_leads_per_week': 10.0,
    'partner_inactive_days': 60.0,     # newly added
    'content_overdue_days': 7.0        # newly added
}

def initialize_session_state():
    """Initialize all session state variables used across the dashboard"""

    # Data variables
    st.session_state.setdefault('data_loaded', False)
    st.session_state.setdefault('excel_data', None)

    # Threshold settings
    if 'thresholds' not in st.session_state:
        st.session_state.thresholds = DEFAULT_THRESHOLDS.copy()
    else:
        # Fill in missing keys without overwriting existing values
        for key, value in DEFAULT_THRESHOLDS.items():
            st.session_state.thresholds.setdefault(key, value)
