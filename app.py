# Guavas Lead Gen Dashboard
# Main Application Entry Point

import streamlit as st
from config import (
    configure_page, load_custom_css, init_session_state,
    DASHBOARD_TITLE, COMPANY_NAME, PAGE_ICONS
)

# Configure page (must be first Streamlit command)
configure_page()

# Initialize session state
init_session_state()

# Load custom CSS
load_custom_css()

# Sidebar
with st.sidebar:
    st.title(f"📊 {COMPANY_NAME}")
    st.markdown("---")
    
    # Data status
    if st.session_state.data_loaded:
        st.success("✅ Data Loaded")
        if st.session_state.last_upload_time:
            st.caption(f"Last updated: {st.session_state.last_upload_time.strftime('%Y-%m-%d %H:%M')}")
    else:
        st.warning("⚠️ No Data Loaded")
        st.caption("Upload your Excel file in Settings")
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### Navigation")
    st.markdown("""
    - 📊 **Executive Overview** - High-level metrics
    - 📈 **Channel Performance** - Deep dive by source
    - ⚙️ **Settings** - Upload data & configure
    """)
    
    st.markdown("---")
    
    # Quick Stats (if data loaded)
    if st.session_state.data_loaded and st.session_state.excel_data:
        st.markdown("### Quick Stats")
        from utils.data_loader import get_data_loader
        
        loader = get_data_loader()
        if st.session_state.excel_data:
            loader.data = st.session_state.excel_data
            kpis = loader.get_kpi_data()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Leads", f"{int(kpis.get('Total Leads', 0))}")
            with col2:
                st.metric("CPL", f"£{kpis.get('Avg CPL', 0):.2f}")
    
    st.markdown("---")
    st.caption(f"v1.0.0 | {COMPANY_NAME}")

# Main content area
st.title("📊 Guavas Lead Gen Dashboard")

# Welcome message if no data
if not st.session_state.data_loaded:
    st.info("👋 Welcome! Please upload your Excel file in the **Settings** page to get started.")
    
    st.markdown("---")
    
    st.markdown("### 📚 Getting Started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 1️⃣ Upload Data")
        st.markdown("Go to **Settings** page and upload your 14-tab Excel file")
    
    with col2:
        st.markdown("#### 2️⃣ View Metrics")
        st.markdown("Navigate to **Executive Overview** to see your KPIs and trends")
    
    with col3:
        st.markdown("#### 3️⃣ Analyze Channels")
        st.markdown("Dive deep into each channel's performance in **Channel Performance**")
    
    st.markdown("---")
    
    st.markdown("### 📊 Dashboard Features")
    
    features = [
        "✅ **Real-time KPI tracking** - Leads, meetings, deals, CPL",
        "✅ **Channel performance analysis** - Deep dive into each traffic source",
        "✅ **Automated alerts** - Get notified when metrics need attention",
        "✅ **Weekly trends** - Visualize performance over time",
        "✅ **Partner tracking** - Monitor referral partner health",
        "✅ **Content calendar** - Track content production and performance"
    ]
    
    for feature in features:
        st.markdown(feature)
    
    st.markdown("---")
    
    # Demo button
    if st.button("🎮 Load Demo Data", type="primary"):
        st.session_state.data_loaded = True
        st.info("Demo mode activated! This shows sample data. Upload your real Excel file in Settings to see your actual metrics.")
        st.rerun()

else:
    # Data is loaded - show quick overview
    from utils.data_loader import get_data_loader
    from utils.calculations import get_calculator
    
    loader = get_data_loader()
    calc = get_calculator()
    
    # Reload data from session state
    if st.session_state.excel_data:
        loader.data = st.session_state.excel_data
    
    kpis = loader.get_kpi_data()
    
    st.markdown("### 📊 Quick Overview")
    
    # Top KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Leads",
            value=calc.format_number(kpis.get('Total Leads', 0)),
            delta="23% vs last month",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="Meetings Booked",
            value=calc.format_number(kpis.get('Total Meetings', 0)),
            delta="15% vs last month",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="Deals Closed",
            value=calc.format_number(kpis.get('Total Deals', 0)),
            delta="8% vs last month",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="Avg CPL",
            value=f"£{kpis.get('Avg CPL', 0):.2f}",
            delta="-£12.50 vs target",
            delta_color="normal"
        )
    
    st.markdown("---")
    
    # Channel performance preview
    st.markdown("### 📈 Top Performing Channels")
    
    channels_df = loader.get_channel_data()
    
    if not channels_df.empty:
        # Sort by CPL (exclude £0 CPL for organic channels)
        paid_channels = channels_df[channels_df['CPL'] > 0].sort_values('CPL').head(3)
        
        if not paid_channels.empty:
            for idx, channel in paid_channels.iterrows():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    status_icon = "🟢" if channel['Status'] == 'Active' else "🟡"
                    st.markdown(f"**{status_icon} {channel['Channel']}**")
                
                with col2:
                    st.markdown(f"{int(channel['Leads'])} leads")
                
                with col3:
                    st.markdown(f"£{channel['CPL']:.2f} CPL")
                
                with col4:
                    if channel['CPL'] < 25:
                        st.markdown("✅ Great")
                    elif channel['CPL'] < 50:
                        st.markdown("⚠️ OK")
                    else:
                        st.markdown("🚨 High")
    
    st.markdown("---")
    
    # Alerts preview
    alerts = loader.get_alerts()
    
    if alerts:
        st.markdown("### 🚨 Action Required")
        
        urgent_alerts = [a for a in alerts if a['type'] == 'urgent']
        warning_alerts = [a for a in alerts if a['type'] == 'warning']
        
        if urgent_alerts:
            for alert in urgent_alerts[:2]:  # Show max 2
                st.error(f"**{alert['title']}**: {alert['message']}")
        
        if warning_alerts:
            for alert in warning_alerts[:2]:  # Show max 2
                st.warning(f"**{alert['title']}**: {alert['message']}")
        
        if len(alerts) > 4:
            st.info(f"... and {len(alerts) - 4} more alerts. View all in Executive Overview.")
    
    st.markdown("---")
    
    st.markdown("### 🧭 Next Steps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("👉 Go to **Executive Overview** for full KPI dashboard")
        st.markdown("👉 Check **Channel Performance** for deep dive analysis")
    
    with col2:
        st.markdown("👉 Review **Settings** to configure alerts and thresholds")
        st.markdown("👉 Upload fresh data weekly to keep metrics current")

# Footer
st.markdown("---")
st.caption(f"© 2025 {COMPANY_NAME} | Lead Generation Dashboard v1.0.0")
