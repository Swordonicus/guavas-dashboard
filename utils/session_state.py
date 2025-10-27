import streamlit as st

# Central defaults
DEFAULT_THRESHOLDS = {
    "max_cpl": 50.0,
    "min_conversion_rate": 2.0,
    "max_response_time": 24.0,
    "min_leads_per_week": 10.0,
    "partner_inactive_days": 60.0,
    "content_overdue_days": 7.0,
}

DEFAULT_BENCHMARKS = {
    "target_cpl": 30.0,
    "target_lead_to_meeting": 20.0,
    "target_meeting_to_deal": 18.0,
    "monthly_lead_goal": 120.0,
    "monthly_revenue_goal": 250000.0,
}

def initialize_session_state() -> None:
    """Initialize all session state variables used across the dashboard."""
    st.session_state.setdefault("data_loaded", False)
    st.session_state.setdefault("excel_data", None)
    st.session_state.setdefault("last_upload_time", None)

    # thresholds
    if "thresholds" not in st.session_state:
        st.session_state.thresholds = DEFAULT_THRESHOLDS.copy()
    else:
        for k, v in DEFAULT_THRESHOLDS.items():
            st.session_state.thresholds.setdefault(k, v)

    # benchmarks
    if "benchmarks" not in st.session_state:
        st.session_state.benchmarks = DEFAULT_BENCHMARKS.copy()
    else:
        for k, v in DEFAULT_BENCHMARKS.items():
            st.session_state.benchmarks.setdefault(k, v)

# QoL helpers
def get_threshold(key: str, fallback=None):
    return st.session_state.thresholds.get(key, DEFAULT_THRESHOLDS.get(key, fallback))

def set_threshold(key: str, value) -> None:
    st.session_state.thresholds[key] = value

def get_benchmark(key: str, fallback=None):
    return st.session_state.benchmarks.get(key, DEFAULT_BENCHMARKS.get(key, fallback))

def set_benchmark(key: str, value) -> None:
    st.session_state.benchmarks[key] = value

def reset_defaults() -> None:
    st.session_state.thresholds = DEFAULT_THRESHOLDS.copy()
    st.session_state.benchmarks = DEFAULT_BENCHMARKS.copy()
