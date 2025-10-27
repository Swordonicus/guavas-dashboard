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
import streamlit as st

def load_custom_css():
    st.markdown("""
    <style>
      /* --- Force theme variables (affects sidebar background in some builds) --- */
      :root,
      [data-theme="light"],
      [data-theme="dark"] {
        --background-color: #0F1116 !important;
        --secondary-background-color: #111827 !important; /* sidebar/cards */
        --text-color: #E5E7EB !important;
      }

      /* --- Sidebar containers (cover both nav + old/new testids) --- */
      [data-testid="stSidebar"],
      section[data-testid="stSidebar"],
      [data-testid="stSidebarNav"],
      nav[data-testid="stSidebarNav"] {
        background: linear-gradient(180deg, #0F1116 0%, #111827 60%, #151A22 100%) !important;
        color: #E5E7EB !important;
      }

      /* Ensure all text inside sidebar is readable */
      [data-testid="stSidebar"] *,
      [data-testid="stSidebarNav"] * {
        color: #E5E7EB !important;
      }

      /* Active/hover states for page links */
      [data-testid="stSidebarNav"] ul li a {
        color: #E5E7EB !important;
        border-radius: 10px;
        padding: 0.5rem 0.75rem;
        transition: transform .15s ease, background-color .15s ease;
      }
      [data-testid="stSidebarNav"] ul li a:hover {
        background: rgba(255,255,255,.06) !important;
        transform: translateX(2px);
      }
      [data-testid="stSidebarNav"] ul li a[aria-selected="true"] {
        background: linear-gradient(90deg, #22C55E 0%, #16A34A 100%) !important;
        color: #0B0F14 !important;
        font-weight: 600 !important;
      }

      /* Scrollbar tweaks */
      [data-testid="stSidebar"] ::-webkit-scrollbar { width: 10px; }
      [data-testid="stSidebar"] ::-webkit-scrollbar-thumb { background: rgba(255,255,255,.15); border-radius: 8px; }

      /* If OS switches to light, keep sidebar dark for contrast */
      @media (prefers-color-scheme: light) {
        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"] {
          background: linear-gradient(180deg, #0F1116 0%, #111827 60%, #151A22 100%) !important;
        }
        [data-testid="stSidebar"] *,
        [data-testid="stSidebarNav"] * {
          color: #E5E7EB !important;
        }
      }
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
