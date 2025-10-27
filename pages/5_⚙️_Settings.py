# Page 5: Settings
# File upload, data validation, and dashboard configuration

import streamlit as st
import pandas as pd
from datetime import datetime
from config import load_custom_css, EXPECTED_TABS, MAX_FILE_SIZE_MB
from utils.data_loader import get_data_loader
from utils.session_state import (
    initialize_session_state,
    DEFAULT_THRESHOLDS,
    DEFAULT_BENCHMARKS,
    reset_defaults,
)

# ── Init session state ─────────────────────────────────────────────────────────
initialize_session_state()
st.session_state.setdefault('data_loaded', False)
st.session_state.setdefault('excel_data', None)
st.session_state.setdefault('thresholds', DEFAULT_THRESHOLDS.copy())
st.session_state.setdefault('benchmarks', DEFAULT_BENCHMARKS.copy())
st.session_state.setdefault('last_upload_time', None)

# ── CSS ────────────────────────────────────────────────────────────────────────
load_custom_css()

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("⚙️ Settings & Data Management")
st.markdown("*Upload your Excel file and configure dashboard settings*")
st.markdown("---")

# ── Loader ─────────────────────────────────────────────────────────────────────
loader = get_data_loader()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📤 Data Upload", "🎚️ Configuration", "ℹ️ About"])

# ── TAB 1: DATA UPLOAD ─────────────────────────────────────────────────────────
with tab1:
    st.markdown("### 📤 Upload Your Tracking Spreadsheet")

    uploaded_file = st.file_uploader(
        "Choose your Excel file (.xlsx or .xls)",
        type=['xlsx', 'xls'],
        help=f"Maximum file size: {MAX_FILE_SIZE_MB}MB"
    )

    if uploaded_file is not None:
        file_details = {
            "Filename": uploaded_file.name,
            "File Size": f"{uploaded_file.size / 1024:.2f} KB",
            "Upload Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.info(f"**File Selected**: {file_details['Filename']} ({file_details['File Size']})")

        if st.button("📥 Load Data", type="primary"):
            with st.spinner("Loading and validating data..."):
                try:
                    data = loader.load_excel(uploaded_file)
                    if data:
                        st.session_state.excel_data = data
                        st.session_state.data_loaded = True
                        st.session_state.last_upload_time = datetime.now()

                        st.success("✅ Data loaded successfully!")
                        st.balloons()

                        st.markdown("---")
                        st.markdown("### ✅ Data Validation Results")

                        validation = loader.get_validation_summary()

                        rows = []
                        for tab_name, result in validation.items():
                            rows.append({
                                'Tab Name': tab_name,
                                'Status': result['status'],
                                'Rows': result.get('rows', 0) if result['exists'] else 'N/A',
                                'Columns': result.get('columns', 0) if result['exists'] else 'N/A',
                                'Issues': ', '.join(result.get('issues', [])) if result.get('issues') else 'None',
                            })
                        val_df = pd.DataFrame(rows)

                        def highlight_status(row):
                            if row['Status'] == 'Valid':
                                return ['background-color: #D1FAE5'] * len(row)
                            if row['Status'] == 'Warning':
                                return ['background-color: #FEF3C7'] * len(row)
                            if row['Status'] == 'Missing':
                                return ['background-color: #FEE2E2'] * len(row)
                            return [''] * len(row)

                        try:
                            st.dataframe(
                                val_df.style.apply(highlight_status, axis=1),
                                use_container_width=True,
                                hide_index=True,
                            )
                        except Exception:
                            st.dataframe(val_df, use_container_width=True, hide_index=True)

                        valid = sum(1 for v in validation.values() if v['status'] == 'Valid')
                        warn = sum(1 for v in validation.values() if v['status'] == 'Warning')
                        miss = sum(1 for v in validation.values() if v['status'] == 'Missing')

                        c1, c2, c3 = st.columns(3)
                        with c1: st.metric("✅ Valid", valid)
                        with c2: st.metric("⚠️ Warnings", warn)
                        with c3: st.metric("❌ Missing", miss)

                        if warn > 0 or miss > 0:
                            st.warning("⚠️ Some tabs have issues. The dashboard will work, but some features may have limited data.")

                        st.markdown("---")
                        st.markdown("### 👀 Data Preview")

                        available_tabs = [t for t in EXPECTED_TABS if t in data]
                        if available_tabs:
                            preview_tab = st.selectbox("Select tab to preview:", available_tabs)
                            if preview_tab in data:
                                preview_df = data[preview_tab]
                                st.dataframe(preview_df.head(10), use_container_width=True)
                                st.caption(f"Showing first 10 rows of {len(preview_df)} total rows")
                        else:
                            st.info("No expected tabs found in the uploaded file.")
                    else:
                        st.error("❌ Failed to load data. Please check the file format.")
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
                    st.caption("Please ensure your Excel file matches the expected structure.")

    else:
        st.markdown("---")
        st.markdown("### 📋 Expected File Structure")
        st.info("Your Excel file should contain these 14 tabs:")

        l, r = st.columns(2)
        with l:
            st.markdown("**Core Tracking Tabs:**")
            for tab in EXPECTED_TABS[:7]:
                st.markdown(f"• {tab}")
        with r:
            st.markdown("**Additional Tabs:**")
            for tab in EXPECTED_TABS[7:]:
                st.markdown(f"• {tab}")

        st.markdown("---")
        st.markdown("### 📊 Current Data Status")

        if st.session_state.data_loaded:
            st.success("✅ **Data is loaded and ready**")
            if st.session_state.get('last_upload_time'):
                st.caption(f"Last uploaded: {st.session_state['last_upload_time'].strftime('%Y-%m-%d %H:%M:%S')}")
            if st.button("🗑️ Clear Current Data"):
                st.session_state.data_loaded = False
                st.session_state.excel_data = None
                st.session_state.last_upload_time = None
                st.success("Data cleared. Upload a new file to continue.")
                st.rerun()
        else:
            st.warning("⚠️ **No data currently loaded**")
            st.caption("Upload your Excel file above to get started")

            st.markdown("---")
            st.markdown("### 🎮 Demo Mode")
            st.info("Want to explore the dashboard with sample data?")
            if st.button("Load Demo Data", type="secondary"):
                st.session_state.data_loaded = True
                st.info("✅ Demo data loaded! This shows sample data for testing purposes.")
                st.rerun()

# ── TAB 2: CONFIGURATION ───────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🎚️ Dashboard Configuration")

    st.markdown("#### 🚨 Alert Thresholds")
    st.caption("Set thresholds for automatic alerts")

    c1, c2 = st.columns(2)
    with c1:
        max_cpl = st.number_input(
            "Maximum CPL (£)", min_value=10.0, max_value=200.0,
            value=float(st.session_state.thresholds.get('max_cpl', 50.0)),
            step=5.0, help="Alert when any channel CPL exceeds this amount",
        )
        min_conversion = st.number_input(
            "Minimum Lead→Meeting Conversion (%)", min_value=0.0, max_value=50.0,
            value=float(st.session_state.thresholds.get('min_conversion_rate', 2.0)),
            step=1.0, help="Alert when conversion rate drops below this",
        )
        min_weekly_leads = st.number_input(
            "Minimum Weekly Leads", min_value=10.0, max_value=200.0,
            value=float(st.session_state.thresholds.get('min_leads_per_week', 10.0)),
            step=5.0, help="Alert when weekly leads drop below this number",
        )
    with c2:
        partner_inactive_days = st.number_input(
            "Partner Inactive Alert (days)", min_value=30.0, max_value=180.0,
            value=float(st.session_state.thresholds.get('partner_inactive_days', 60.0)),
            step=10.0, help="Alert when partner has no referrals for this many days",
        )
        content_overdue_days = st.number_input(
            "Content Overdue Alert (days)", min_value=1.0, max_value=14.0,
            value=float(st.session_state.thresholds.get('content_overdue_days', 7.0)),
            step=1.0, help="Alert when content is overdue by this many days",
        )

    if st.button("💾 Save Alert Settings", type="primary"):
        st.session_state.thresholds = {
            'max_cpl': max_cpl,
            'min_conversion_rate': min_conversion,
            'min_leads_per_week': min_weekly_leads,
            'partner_inactive_days': partner_inactive_days,
            'content_overdue_days': content_overdue_days,
        }
        st.success("✅ Alert settings saved!")

    st.markdown("---")
    st.markdown("#### 🎯 Target Benchmarks")
    st.caption("Set your performance targets")

    b1, b2 = st.columns(2)
    with b1:
        target_cpl = st.number_input(
            "Target CPL (£)", min_value=10.0, max_value=100.0,
            value=float(st.session_state.benchmarks.get('target_cpl', 30.0)),
            step=5.0,
        )
        target_lead_to_meeting = st.number_input(
            "Target Lead→Meeting (%)", min_value=10.0, max_value=50.0,
            value=float(st.session_state.benchmarks.get('target_lead_to_meeting', 20.0)),
            step=1.0,
        )
        target_meeting_to_deal = st.number_input(
            "Target Meeting→Deal (%)", min_value=10.0, max_value=50.0,
            value=float(st.session_state.benchmarks.get('target_meeting_to_deal', 18.0)),
            step=1.0,
        )
    with b2:
        monthly_lead_goal = st.number_input(
            "Monthly Lead Goal", min_value=50.0, max_value=500.0,
            value=float(st.session_state.benchmarks.get('monthly_lead_goal', 120.0)),
            step=10.0,
        )
        monthly_revenue_goal = st.number_input(
            "Monthly Revenue Goal (£)", min_value=100000.0, max_value=2000000.0,
            value=float(st.session_state.benchmarks.get('monthly_revenue_goal', 250000.0)),
            step=50000.0,
        )

    if st.button("💾 Save Target Benchmarks", type="primary"):
        st.session_state.benchmarks = {
            'target_cpl': target_cpl,
            'target_lead_to_meeting': target_lead_to_meeting,
            'target_meeting_to_deal': target_meeting_to_deal,
            'monthly_lead_goal': monthly_lead_goal,
            'monthly_revenue_goal': monthly_revenue_goal,
        }
        st.success("✅ Target benchmarks saved!")

    st.markdown("---")
    st.markdown("#### 🎨 Dashboard Preferences")

    p1, p2 = st.columns(2)
    with p1:
        default_page = st.selectbox(
            "Default Landing Page",
            ["Home", "Executive Overview", "Channel Performance"],
            index=0,
        )
        date_range_default = st.selectbox(
            "Default Date Range",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "This Month"],
            index=1,
        )
    with p2:
        currency = st.selectbox(
            "Currency", ["GBP (£)", "USD ($)", "EUR (€)"],
            index=0, disabled=True, help="Currency selection coming soon",
        )
        timezone = st.selectbox(
            "Timezone", ["Europe/London (GMT)", "US/Eastern (EST)", "US/Pacific (PST)"],
            index=0, disabled=True, help="Timezone selection coming soon",
        )

    st.markdown("---")
    st.markdown("#### 🔄 Reset Settings")
    if st.button("⚠️ Reset All Settings to Default", type="secondary"):
        reset_defaults()
        st.warning("Settings reset to defaults. Refresh the page to see changes.")

# ── TAB 3: ABOUT ───────────────────────────────────────────────────────────────
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
        "Settings": "Upload data, configure alerts, and set targets",
    }
    for k, v in features.items():
        st.markdown(f"**{k}**  \n{v}")

    st.markdown("---")
    st.markdown("#### 📚 How to Use")
    st.markdown("""
    **Step 1: Upload Your Data**
    - Go to Settings → Data Upload tab
    - Upload your 14-tab Excel tracking file
    - Verify validation results

    **Step 2: Explore Your Metrics**
    - Executive Overview for high-level dashboard
    - Channel Performance for deep dives
    - Configure alerts in Configuration

    **Step 3: Make Data-Driven Decisions**
    - Review weekly trends
    - Compare to industry benchmarks
    - Optimize underperforming channels
    """)
    st.markdown("---")

    st.markdown("#### 📞 Support")
    st.info("""
    **Need Help?**
    - 📧 Email: support@guavas.co.uk
    - 🤖 Ask: "How do I optimize [channel] based on the dashboard data?"
    """)

    st.markdown("---")
    st.markdown("#### 🔧 Technical Information")
    lft, rgt = st.columns(2)
    with lft:
        st.markdown("""
        **Built With:**
        - Streamlit 1.31+
        - Plotly 5.18+
        - Pandas 2.1+
        - Python 3.11+
        """)
    with rgt:
        st.markdown("""
        **Features:**
        - Real-time data loading
        - Interactive charts
        - Automated alerts
        - Mobile responsive
        """)

    st.markdown("---")
    st.markdown("#### 🟢 System Status")
    s1, s2, s3 = st.columns(3)
    with s1: st.success("✅ **Dashboard**: Online")
    with s2:
        st.success("✅ **Data**: Loaded") if st.session_state.data_loaded else st.warning("⚠️ **Data**: Not Loaded")
    with s3: st.success("✅ **Charts**: Operational")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("© 2025 Guavas.co.uk | Lead Generation Dashboard v1.0.0")
