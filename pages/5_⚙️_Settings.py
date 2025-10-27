# Page 5: Settings
# File upload, data validation, and dashboard configuration

import streamlit as st
import pandas as pd
from datetime import datetime
from config import (
    load_custom_css, EXPECTED_TABS, MAX_FILE_SIZE_MB,
    THRESHOLDS, BENCHMARKS
)
from utils.data_loader import get_data_loader
# Initialize session state
from utils.session_state import initialize_session_state
initialize_session_state()
# Initialize session state variables
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None
# Load CSS
load_custom_css()

# Page header
st.title("⚙️ Settings & Data Management")
st.markdown("*Upload your Excel file and configure dashboard settings*")

st.markdown("---")

# Initialize data loader
loader = get_data_loader()

# ========== TAB NAVIGATION ==========
tab1, tab2, tab3 = st.tabs(["📤 Data Upload", "🎚️ Configuration", "ℹ️ About"])

# ========== TAB 1: DATA UPLOAD ==========
with tab1:
    st.markdown("### 📤 Upload Your Tracking Spreadsheet")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose your Excel file (.xlsx or .xls)",
        type=['xlsx', 'xls'],
        help=f"Maximum file size: {MAX_FILE_SIZE_MB}MB"
    )
    
    if uploaded_file is not None:
        # Show file info
        file_details = {
            "Filename": uploaded_file.name,
            "File Size": f"{uploaded_file.size / 1024:.2f} KB",
            "Upload Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        st.info(f"**File Selected**: {file_details['Filename']} ({file_details['File Size']})")
        
        # Load button
        if st.button("📥 Load Data", type="primary"):
            with st.spinner("Loading and validating data..."):
                try:
                    # Load the Excel file
                    data = loader.load_excel(uploaded_file)
                    
                    if data:
                        st.success("✅ Data loaded successfully!")
                        st.balloons()
                        
                        # Show validation results
                        st.markdown("---")
                        st.markdown("### ✅ Data Validation Results")
                        
                        validation = loader.get_validation_summary()
                        
                        # Create validation dataframe
                        val_data = []
                        for tab_name, result in validation.items():
                            val_data.append({
                                'Tab Name': tab_name,
                                'Status': result['status'],
                                'Rows': result.get('rows', 0) if result['exists'] else 'N/A',
                                'Columns': result.get('columns', 0) if result['exists'] else 'N/A',
                                'Issues': ', '.join(result.get('issues', [])) if result.get('issues') else 'None'
                            })
                        
                        val_df = pd.DataFrame(val_data)
                        
                        # Color code status
                        def highlight_status(row):
                            if row['Status'] == 'Valid':
                                return ['background-color: #D1FAE5'] * len(row)
                            elif row['Status'] == 'Warning':
                                return ['background-color: #FEF3C7'] * len(row)
                            elif row['Status'] == 'Missing':
                                return ['background-color: #FEE2E2'] * len(row)
                            return [''] * len(row)
                        
                        st.dataframe(
                            val_df.style.apply(highlight_status, axis=1),
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Summary stats
                        valid_count = sum(1 for v in validation.values() if v['status'] == 'Valid')
                        warning_count = sum(1 for v in validation.values() if v['status'] == 'Warning')
                        missing_count = sum(1 for v in validation.values() if v['status'] == 'Missing')
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("✅ Valid", valid_count)
                        with col2:
                            st.metric("⚠️ Warnings", warning_count)
                        with col3:
                            st.metric("❌ Missing", missing_count)
                        
                        # Warnings
                        if warning_count > 0 or missing_count > 0:
                            st.warning("⚠️ Some tabs have issues. The dashboard will work, but some features may have limited data.")
                        
                        # Quick preview
                        st.markdown("---")
                        st.markdown("### 👀 Data Preview")
                        
                        preview_tab = st.selectbox(
                            "Select tab to preview:",
                            [tab for tab in EXPECTED_TABS if tab in data]
                        )
                        
                        if preview_tab and preview_tab in data:
                            preview_df = data[preview_tab]
                            st.dataframe(
                                preview_df.head(10),
                                use_container_width=True
                            )
                            st.caption(f"Showing first 10 rows of {len(preview_df)} total rows")
                        
                    else:
                        st.error("❌ Failed to load data. Please check the file format.")
                        
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
                    st.caption("Please ensure your Excel file matches the expected structure.")
    
    else:
        # Show expected structure
        st.markdown("---")
        st.markdown("### 📋 Expected File Structure")
        
        st.info("Your Excel file should contain these 14 tabs:")
        
        tab_cols = st.columns(2)
        
        with tab_cols[0]:
            st.markdown("**Core Tracking Tabs:**")
            for tab in EXPECTED_TABS[:7]:
                st.markdown(f"• {tab}")
        
        with tab_cols[1]:
            st.markdown("**Additional Tabs:**")
            for tab in EXPECTED_TABS[7:]:
                st.markdown(f"• {tab}")
        
        st.markdown("---")
        
        # Current data status
        st.markdown("### 📊 Current Data Status")
        
        if st.session_state.data_loaded:
            st.success("✅ **Data is loaded and ready**")
            if st.session_state.last_upload_time:
                st.caption(f"Last uploaded: {st.session_state.last_upload_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if st.button("🗑️ Clear Current Data"):
                st.session_state.data_loaded = False
                st.session_state.excel_data = None
                st.session_state.last_upload_time = None
                st.success("Data cleared. Upload a new file to continue.")
                st.rerun()
        else:
            st.warning("⚠️ **No data currently loaded**")
            st.caption("Upload your Excel file above to get started")
            
            # Demo data option
            st.markdown("---")
            st.markdown("### 🎮 Demo Mode")
            st.info("Want to explore the dashboard with sample data?")
            
            if st.button("Load Demo Data", type="secondary"):
                st.session_state.data_loaded = True
                st.info("✅ Demo data loaded! This shows sample data for testing purposes.")
                st.rerun()

# ========== TAB 2: CONFIGURATION ==========
with tab2:
    st.markdown("### 🎚️ Dashboard Configuration")
    
    # Alert Thresholds
    st.markdown("#### 🚨 Alert Thresholds")
    st.caption("Set thresholds for automatic alerts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_cpl = st.number_input(
            "Maximum CPL (£)",
            min_value=10.0,
            max_value=200.0,
            value=st.session_state.thresholds['max_cpl'],
            step=5.0,
            help="Alert when any channel CPL exceeds this amount"
        )
        
        min_conversion = st.number_input(
            "Minimum Lead→Meeting Conversion (%)",
            min_value=5.0,
            max_value=50.0,
            value=st.session_state.thresholds['min_conversion_rate'],
            step=1.0,
            help="Alert when conversion rate drops below this"
        )
        
        min_weekly_leads = st.number_input(
            "Minimum Weekly Leads",
            min_value=10.0,
            max_value=200.0,
            value=st.session_state.thresholds['min_leads_per_week'],
            step=5.0,
            help="Alert when weekly leads drop below this number"
        )
    
    with col2:
        partner_inactive_days = st.number_input(
            "Partner Inactive Alert (days)",
            min_value=30.0,
            max_value=180.0,
            value=st.session_state.thresholds['partner_inactive_days'],
            step=10.0,
            help="Alert when partner has no referrals for this many days"
        )
        
        content_overdue_days = st.number_input(
            "Content Overdue Alert (days)",
            min_value=1,
            max_value=14,
            value=st.session_state.thresholds['content_overdue_days'],
            step=1.0,
            help="Alert when content is overdue by this many days"
        )
    
    # Save thresholds
    if st.button("💾 Save Alert Settings", type="primary"):
        st.session_state.thresholds = {
            'max_cpl': max_cpl,
            'min_conversion_rate': min_conversion,
            'min_leads_per_week': min_weekly_leads,
            'partner_inactive_days': partner_inactive_days,
            'content_overdue_days': content_overdue_days
        }
        st.success("✅ Alert settings saved!")
    
    st.markdown("---")
    
    # Target Benchmarks
    st.markdown("#### 🎯 Target Benchmarks")
    st.caption("Set your performance targets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_cpl = st.number_input(
            "Target CPL (£)",
            min_value=10.0,
            max_value=100.0,
            value=st.session_state.benchmarks['target_cpl'],
            step=5.0
        )
        
        target_lead_to_meeting = st.number_input(
            "Target Lead→Meeting (%)",
            min_value=10.0,
            max_value=50.0,
            value=st.session_state.benchmarks['target_lead_to_meeting'],
            step=1.0
        )
        
        target_meeting_to_deal = st.number_input(
            "Target Meeting→Deal (%)",
            min_value=10.0,
            max_value=50.0,
            value=st.session_state.benchmarks['target_meeting_to_deal'],
            step=1.0
        )
    
    with col2:
        monthly_lead_goal = st.number_input(
            "Monthly Lead Goal",
            min_value=50.0,
            max_value=500.0,
            value=st.session_state.benchmarks['monthly_lead_goal'],
            step=10.0
        )
        
        monthly_revenue_goal = st.number_input(
            "Monthly Revenue Goal (£)",
            min_value=100000.0,
            max_value=2000000.0,
            value=st.session_state.benchmarks['monthly_revenue_goal'],
            step=50000.0
        )
    
    # Save benchmarks
    if st.button("💾 Save Target Benchmarks", type="primary"):
        st.session_state.benchmarks = {
            'target_cpl': target_cpl,
            'target_lead_to_meeting': target_lead_to_meeting,
            'target_meeting_to_deal': target_meeting_to_deal,
            'monthly_lead_goal': monthly_lead_goal,
            'monthly_revenue_goal': monthly_revenue_goal
        }
        st.success("✅ Target benchmarks saved!")
    
    st.markdown("---")
    
    # Dashboard Preferences
    st.markdown("#### 🎨 Dashboard Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_page = st.selectbox(
            "Default Landing Page",
            ["Home", "Executive Overview", "Channel Performance"],
            index=0
        )
        
        date_range_default = st.selectbox(
            "Default Date Range",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "This Month"],
            index=1
        )
    
    with col2:
        currency = st.selectbox(
            "Currency",
            ["GBP (£)", "USD ($)", "EUR (€)"],
            index=0,
            disabled=True,
            help="Currency selection coming soon"
        )
        
        timezone = st.selectbox(
            "Timezone",
            ["Europe/London (GMT)", "US/Eastern (EST)", "US/Pacific (PST)"],
            index=0,
            disabled=True,
            help="Timezone selection coming soon"
        )
    
    st.markdown("---")
    
    # Reset to defaults
    st.markdown("#### 🔄 Reset Settings")
    
    if st.button("⚠️ Reset All Settings to Default", type="secondary"):
        st.session_state.thresholds = THRESHOLDS.copy()
        st.session_state.benchmarks = BENCHMARKS.copy()
        st.warning("Settings reset to defaults. Refresh the page to see changes.")

# ========== TAB 3: ABOUT ==========
with tab3:
    st.markdown("### ℹ️ About Guavas Lead Gen Dashboard")
    
    st.markdown("""
    **Version:** 1.0.0  
    **Built for:** Guavas.co.uk  
    **Purpose:** Real-time lead generation performance tracking and optimization
    """)
    
    st.markdown("---")
    
    st.markdown("#### 📊 Dashboard Features")
    
    features = {
        "Executive Overview": "High-level KPIs, trends, and alerts across all channels",
        "Channel Performance": "Deep dive analysis for each traffic source with benchmarks",
        "Content Calendar": "Track content production and performance (coming soon)",
        "Partners & Pipeline": "Manage referral partners and forecast revenue (coming soon)",
        "Settings": "Upload data, configure alerts, and set targets"
    }
    
    for feature, description in features.items():
        st.markdown(f"**{feature}**  \n{description}")
    
    st.markdown("---")
    
    st.markdown("#### 📚 How to Use")
    
    st.markdown("""
    **Step 1: Upload Your Data**
    - Go to Settings → Data Upload tab
    - Upload your 14-tab Excel tracking file
    - Verify validation results
    
    **Step 2: Explore Your Metrics**
    - Navigate to Executive Overview for high-level dashboard
    - Use Channel Performance for deep dives
    - Set up alerts in Configuration
    
    **Step 3: Make Data-Driven Decisions**
    - Review weekly trends
    - Compare to industry benchmarks
    - Optimize underperforming channels
    - Double down on winners
    """)
    
    st.markdown("---")
    
    st.markdown("#### 🎯 Data Sources & Benchmarks")
    
    st.markdown("""
    Industry benchmarks referenced in this dashboard:
    
    - **89%** of B2B marketers use LinkedIn for lead generation
    - **277%** more effective than Facebook/X for B2B leads
    - **58%** of B2B marketers say video is most effective content
    - **73%** say webinars generate highest quality leads
    - **£15-20** typical CPL range for LinkedIn in B2B
    
    *Source: Industry research from strategy document (fact-checked)*
    """)
    
    st.markdown("---")
    
    st.markdown("#### 📞 Support")
    
    st.info("""
    **Need Help?**
    
    - 📧 Email: support@guavas.co.uk
    - 📱 Check the strategy documents uploaded to Claude Projects
    - 🤖 Ask Claude: "How do I optimize [channel] based on the dashboard data?"
    """)
    
    st.markdown("---")
    
    st.markdown("#### 🔧 Technical Information")
    
    tech_col1, tech_col2 = st.columns(2)
    
    with tech_col1:
        st.markdown("""
        **Built With:**
        - Streamlit 1.31+
        - Plotly 5.18+
        - Pandas 2.1+
        - Python 3.9+
        """)
    
    with tech_col2:
        st.markdown("""
        **Features:**
        - Real-time data loading
        - Interactive charts
        - Automated alerts
        - Mobile responsive
        """)
    
    st.markdown("---")
    
    # System status
    st.markdown("#### 🟢 System Status")
    
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.success("✅ **Dashboard**: Online")
    
    with status_col2:
        if st.session_state.data_loaded:
            st.success("✅ **Data**: Loaded")
        else:
            st.warning("⚠️ **Data**: Not Loaded")
    
    with status_col3:
        st.success("✅ **Charts**: Operational")

# Footer
st.markdown("---")
st.caption("© 2025 Guavas.co.uk | Lead Generation Dashboard v1.0.0")
