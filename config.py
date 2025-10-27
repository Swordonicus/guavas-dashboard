# Guavas Lead Gen Dashboard - Configuration
# This file contains all dashboard settings and constants

import streamlit as st

# Dashboard Settings
DASHBOARD_TITLE = "Guavas Lead Gen Dashboard"
COMPANY_NAME = "Guavas.co.uk"
DASHBOARD_VERSION = "1.0.0"

# Color Scheme (Guavas Brand Colors)
COLORS = {
    'primary': '#FF9786',      # Guavas coral pink - primary brand color
    'success': '#8FC93A',      # Guavas lime green - positive metrics
    'warning': '#FF9786',      # Coral for warnings (same as primary)
    'danger': '#E94B3C',       # Slightly darker red (complements coral)
    'info': '#FF9786',         # Use coral for info too
    'grey_900': '#342E37',     # Guavas dark charcoal - text/headers
    'grey_600': '#5C5560',     # Lighter version of charcoal
    'grey_300': '#D1D5DB',     # Keep existing for borders
    'grey_100': '#FBFBFB',     # Guavas off-white - backgrounds
    'white': '#FBFBFB'         # Use off-white instead of pure white
}

# Status Colors
STATUS_COLORS = {
    'Active': '#10B981',       # Green
    'Paused': '#F59E0B',       # Amber
    'In Development': '#6366F1', # Indigo
    'Inactive': '#6B7280',     # Grey
    'Live': '#10B981',
    'Planning': '#F59E0B',
    'Completed': '#10B981',
    'Overdue': '#EF4444'
}

# Alert Thresholds (Default - User can modify in Settings)
THRESHOLDS = {
    'max_cpl': 50,                    # Alert if CPL exceeds £50
    'min_conversion_rate': 15,        # Alert if lead→meeting drops below 15%
    'min_leads_per_week': 40,         # Alert if weekly leads drop below 40
    'partner_inactive_days': 60,      # Alert if partner no referrals in 60 days
    'content_overdue_days': 2         # Alert if content overdue by 2+ days
}

# Target Benchmarks (From Strategy Document)
BENCHMARKS = {
    'target_cpl': 25,                 # Target CPL: £25
    'target_lead_to_meeting': 20,     # Target: 20% lead→meeting conversion
    'target_meeting_to_deal': 18,     # Target: 18% meeting→deal conversion
    'monthly_lead_goal': 100,         # Target: 100 leads/month
    'monthly_revenue_goal': 500000    # Target: £500K/month
}

# Industry Benchmarks (From Strategy Document - Fact Checked)
INDUSTRY_BENCHMARKS = {
    'linkedin_usage': 89,              # 89% of B2B marketers use LinkedIn
    'linkedin_effectiveness': 277,     # 277% more effective than Facebook/X
    'video_effectiveness': 58,         # 58% say video most effective
    'webinar_quality': 73,            # 73% say webinars = best quality leads
    'trust_requirement': 75,          # 75% refuse to buy without trust
    'linkedin_cpl_range': (15, 20),   # Industry CPL range: £15-20
    'email_open_rate': 23,            # Industry avg: 23% open rate
    'email_click_rate': 3.5           # Industry avg: 3.5% click rate
}

# Data File Settings
UPLOAD_FOLDER = 'data/uploads/'
MAX_FILE_SIZE_MB = 10

# Expected Excel Tabs (Your 14-tab structure)
EXPECTED_TABS = [
    '1_Funnel Master Map',
    '2_Content Elements',
    '3_Content Calendar',
    '4_Lead Magnets',
    '5_Email Sequences',
    '6_Customer Journey',
    '7_Retargeting',
    '8_Website Elements',
    '9_Attribution Tracking',
    '10_Testing Log',
    '11_Lead Scoring',
    '12_KPI Dashboard',
    '13_Partner Performance',
    '13_Gaps & Opportunities'
]

# Chart Settings
CHART_HEIGHT = 400
CHART_TEMPLATE = 'plotly_white'
TREND_WEEKS = 12  # Show last 12 weeks in trend charts

# Date Format
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# Currency
CURRENCY = 'GBP'
CURRENCY_SYMBOL = '£'

# Page Icons (Emoji for sidebar)
PAGE_ICONS = {
    'Executive Overview': '📊',
    'Channel Performance': '📈',
    'Content Calendar': '📝',
    'Partners & Pipeline': '🤝',
    'Settings': '⚙️'
}

# Priority 0 Channels (From Strategy Document)
PRIORITY_0_CHANNELS = [
    'LinkedIn Organic',
    'Webinar Program',
    'Case Studies',
    'Partner Referrals'
]

# Streamlit Page Config
def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title=DASHBOARD_TITLE,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Custom CSS for styling
def load_custom_css():
    """Load custom CSS for dashboard styling"""
    st.markdown(f"""
    <style>
        /* Main Dashboard Styling */
        .main {{
            background-color: {COLORS['grey_100']};
        }}
        
        /* KPI Card Styling */
        .kpi-card {{
            background: {COLORS['white']};
            padding: 20px;
            border-radius: 12px;
            border: 1px solid {COLORS['grey_300']};
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .kpi-value {{
            font-size: 36px;
            font-weight: 700;
            color: {COLORS['grey_900']};
            line-height: 1;
            margin: 10px 0;
        }}
        
        .kpi-label {{
            font-size: 14px;
            color: {COLORS['grey_600']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }}
        
        .kpi-trend {{
            font-size: 14px;
            font-weight: 600;
            margin-top: 8px;
        }}
        
        .trend-up {{
            color: {COLORS['success']};
        }}
        
        .trend-down {{
            color: {COLORS['danger']};
        }}
        
        .trend-neutral {{
            color: {COLORS['grey_600']};
        }}
        
        /* Alert Styling */
        .alert-warning {{
            background: {COLORS['warning']};
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        
        .alert-danger {{
            background: {COLORS['danger']};
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        
        .alert-info {{
            background: {COLORS['info']};
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        
        /* Button Styling */
        .stButton > button {{
            background-color: {COLORS['primary']};
            color: white;
            border-radius: 8px;
            padding: 12px 24px;
            border: none;
            font-weight: 600;
        }}
        
        .stButton > button:hover {{
            background-color: #0052A3;
        }}
        
        /* Metric Cards (Streamlit native) */
        [data-testid="stMetricValue"] {{
            font-size: 36px;
            font-weight: 700;
        }}
        
        /* Hide Streamlit Branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* Table Styling */
        .dataframe {{
            border: 1px solid {COLORS['grey_300']} !important;
        }}
        
        .dataframe thead th {{
            background-color: {COLORS['grey_100']} !important;
            font-weight: 600 !important;
        }}
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: {COLORS['white']};
        }}
        
        /* Header Styling */
        h1 {{
            color: {COLORS['grey_900']};
            font-weight: 700;
        }}
        
        h2 {{
            color: {COLORS['grey_900']};
            font-weight: 600;
        }}
        
        h3 {{
            color: {COLORS['grey_900']};
            font-weight: 600;
        }}
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
def init_session_state():
    """Initialize session state variables"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    if 'excel_data' not in st.session_state:
        st.session_state.excel_data = None
    
    if 'last_upload_time' not in st.session_state:
        st.session_state.last_upload_time = None
    
    if 'thresholds' not in st.session_state:
        st.session_state.thresholds = THRESHOLDS.copy()
    
    if 'benchmarks' not in st.session_state:
        st.session_state.benchmarks = BENCHMARKS.copy()
