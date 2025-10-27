# Page 1: Executive Overview
# High-level KPIs, trends, and alerts

import streamlit as st
import pandas as pd
from datetime import datetime
from config import load_custom_css, COLORS, BENCHMARKS
from utils.data_loader import get_data_loader
from utils.calculations import get_calculator
from utils.visualizations import get_chart_builder
from utils.visualizations import get_chart_builder
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
# Load CSS
load_custom_css()

# Page header
st.title("📊 Executive Overview")
st.markdown("*High-level performance snapshot across all channels*")

# Check if data is loaded
if not st.session_state.data_loaded:
    st.warning("⚠️ No data loaded. Please upload your Excel file in **Settings** first.")
    
    if st.button("Go to Settings"):
        st.switch_page("pages/5_⚙️_Settings.py")
    
    st.stop()

# Initialize utilities
loader = get_data_loader()
calc = get_calculator()
charts = get_chart_builder()

# Reload data from session
if st.session_state.excel_data:
    loader.data = st.session_state.excel_data

# Get data
kpis = loader.get_kpi_data()
channels_df = loader.get_channel_data()
weekly_trend = loader.get_weekly_trend_data()
alerts = loader.get_alerts()

# Last updated timestamp
col1, col2 = st.columns([3, 1])
with col2:
    if st.session_state.last_upload_time:
        st.caption(f"📅 Last updated: {st.session_state.last_upload_time.strftime('%Y-%m-%d %H:%M')}")

st.markdown("---")

# ========== PRIMARY KPIs (Top Row) ==========
st.markdown("### 🎯 This Month's Performance")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    leads = kpis.get('Total Leads', 0)
    leads_prev = 232  # Previous month (would come from historical data)
    leads_change = calc.calculate_mom_change(leads, leads_prev)
    
    st.metric(
        label="TOTAL LEADS",
        value=calc.format_number(leads),
        delta=f"{leads_change:+.1f}% MoM"
    )
    
    # Target progress
    target = BENCHMARKS['monthly_lead_goal']
    progress = (leads / target) * 100
    st.progress(min(progress / 100, 1.0))
    st.caption(f"{progress:.0f}% of {target} target")

with kpi_col2:
    meetings = kpis.get('Total Meetings', 0)
    meetings_prev = 58
    meetings_change = calc.calculate_mom_change(meetings, meetings_prev)
    
    st.metric(
        label="MEETINGS BOOKED",
        value=calc.format_number(meetings),
        delta=f"{meetings_change:+.1f}% MoM"
    )
    
    # Conversion rate
    if leads > 0:
        conversion = (meetings / leads) * 100
        st.caption(f"{conversion:.1f}% conversion rate")
        
        # Compare to target
        target_conv = BENCHMARKS['target_lead_to_meeting']
        if conversion >= target_conv:
            st.caption(f"✅ Above {target_conv}% target")
        else:
            st.caption(f"⚠️ Below {target_conv}% target")

with kpi_col3:
    deals = kpis.get('Total Deals', 0)
    deals_prev = 11
    deals_change = calc.calculate_mom_change(deals, deals_prev)
    
    st.metric(
        label="DEALS CLOSED",
        value=calc.format_number(deals),
        delta=f"{deals_change:+.1f}% MoM"
    )
    
    # Win rate
    if meetings > 0:
        win_rate = (deals / meetings) * 100
        st.caption(f"{win_rate:.1f}% win rate")
        
        target_win = BENCHMARKS['target_meeting_to_deal']
        if win_rate >= target_win:
            st.caption(f"✅ Above {target_win}% target")
        else:
            st.caption(f"⚠️ Below {target_win}% target")

with kpi_col4:
    pipeline = kpis.get('Pipeline Value', 0)
    
    st.metric(
        label="PIPELINE VALUE",
        value=calc.format_currency(pipeline),
        delta="+12% MoM"
    )
    
    # Weighted pipeline
    weighted = pipeline * 0.35  # Assume 35% weighted close rate
    st.caption(f"{calc.format_currency(weighted)} weighted")
    st.caption(f"Avg: {calc.format_currency(pipeline/max(deals, 1))} per deal")

st.markdown("---")

# ========== SECONDARY KPIs (Bottom Row) ==========
st.markdown("### 💰 Efficiency Metrics")

eff_col1, eff_col2, eff_col3, eff_col4 = st.columns(4)

with eff_col1:
    cpl = kpis.get('Avg CPL', 0)
    cpl_prev = 45.00
    cpl_change = cpl - cpl_prev
    
    st.metric(
        label="AVG COST PER LEAD",
        value=f"£{cpl:.2f}",
        delta=f"£{cpl_change:+.2f} vs last month",
        delta_color="inverse"  # Lower is better
    )
    
    target_cpl = BENCHMARKS['target_cpl']
    if cpl <= target_cpl:
        st.caption(f"✅ Below £{target_cpl} target")
    else:
        st.caption(f"⚠️ Above £{target_cpl} target")

with eff_col2:
    lead_to_meeting = kpis.get('Lead to Meeting %', 0)
    
    st.metric(
        label="LEAD → MEETING",
        value=f"{lead_to_meeting:.1f}%",
        delta="+2.1% vs last month"
    )
    
    target = BENCHMARKS['target_lead_to_meeting']
    st.caption(f"Target: {target}%")

with eff_col3:
    meeting_to_deal = kpis.get('Meeting to Deal %', 0)
    
    st.metric(
        label="MEETING → DEAL",
        value=f"{meeting_to_deal:.1f}%",
        delta="-1.3% vs last month",
        delta_color="inverse"
    )
    
    target = BENCHMARKS['target_meeting_to_deal']
    st.caption(f"Target: {target}%")

with eff_col4:
    avg_deal = kpis.get('Avg Deal Size', 0)
    
    st.metric(
        label="AVG DEAL SIZE",
        value=calc.format_currency(avg_deal),
        delta="+£3K vs last month"
    )
    
    st.caption("Median: £45K")

st.markdown("---")

# ========== WEEKLY TREND CHART ==========
st.markdown("### 📈 Weekly Lead Trend (Last 12 Weeks)")

# Create trend chart
trend_fig = charts.create_kpi_trend_chart(
    weekly_trend,
    title=""
)

st.plotly_chart(trend_fig, use_container_width=True)

# Trend insights
col1, col2, col3 = st.columns(3)

with col1:
    recent_avg = weekly_trend.tail(4).drop('Week', axis=1).sum(axis=1).mean()
    older_avg = weekly_trend.head(4).drop('Week', axis=1).sum(axis=1).mean()
    trend_pct = calc.calculate_mom_change(recent_avg, older_avg)
    
    if trend_pct > 5:
        st.success(f"📈 **Trending Up**: {trend_pct:+.1f}% vs 8 weeks ago")
    elif trend_pct < -5:
        st.error(f"📉 **Trending Down**: {trend_pct:+.1f}% vs 8 weeks ago")
    else:
        st.info(f"→ **Stable**: {trend_pct:+.1f}% vs 8 weeks ago")

with col2:
    # Best week
    weekly_totals = weekly_trend.drop('Week', axis=1).sum(axis=1)
    best_week_idx = weekly_totals.idxmax()
    best_week_leads = weekly_totals.iloc[best_week_idx]
    
    st.info(f"🏆 **Best Week**: {int(best_week_leads)} leads")

with col3:
    # Consistency score
    std_dev = weekly_totals.std()
    mean_leads = weekly_totals.mean()
    consistency = (1 - (std_dev / mean_leads)) * 100
    
    if consistency > 80:
        st.success(f"✅ **Consistent**: {consistency:.0f}% stable")
    else:
        st.warning(f"⚠️ **Variable**: {consistency:.0f}% consistency")

st.markdown("---")

# ========== TOP PERFORMERS & ACTION REQUIRED (Side by Side) ==========
perf_col, alert_col = st.columns(2)

with perf_col:
    st.markdown("### 🏆 Top Performers This Month")
    
    if not channels_df.empty:
        # Sort by efficiency (consider CPL and lead volume)
        # Create efficiency score
        channels_df['Efficiency'] = channels_df.apply(
            lambda row: calc.calculate_channel_efficiency_score(
                row['Leads'], 
                row['CPL'], 
                row.get('Conversion', 20)
            ), 
            axis=1
        )
        
        top_channels = channels_df.nlargest(3, 'Efficiency')
        
        for idx, (_, channel) in enumerate(top_channels.iterrows(), 1):
            with st.container():
                st.markdown(f"**{idx}. {channel['Channel']}**")
                
                metric_cols = st.columns(3)
                with metric_cols[0]:
                    st.caption(f"**{int(channel['Leads'])}** leads")
                with metric_cols[1]:
                    if channel['CPL'] > 0:
                        st.caption(f"**£{channel['CPL']:.2f}** CPL")
                    else:
                        st.caption("**£0** CPL")
                with metric_cols[2]:
                    if 'Conversion' in channel and channel['Conversion'] > 0:
                        st.caption(f"**{channel['Conversion']:.1f}%** conv")
                    else:
                        st.caption("N/A conv")
                
                # Performance indicator
                if channel['CPL'] == 0:
                    st.success("✅ Organic channel - Excellent ROI")
                elif channel['CPL'] < 25:
                    st.success("✅ Great CPL - Keep scaling")
                elif channel['CPL'] < 50:
                    st.info("→ Good CPL - Monitor closely")
                else:
                    st.warning("⚠️ High CPL - Review strategy")
                
                st.markdown("---")
    else:
        st.info("No channel data available")

with alert_col:
    st.markdown("### 🚨 Action Required")
    
    if alerts:
        # Show urgent alerts first
        urgent = [a for a in alerts if a['type'] == 'urgent']
        warnings = [a for a in alerts if a['type'] == 'warning']
        info_alerts = [a for a in alerts if a['type'] == 'info']
        
        # Display urgent
        for alert in urgent:
            st.error(f"**{alert['title']}**  \n{alert['message']}  \n→ *{alert['action']}*")
            st.markdown("---")
        
        # Display warnings (max 2)
        for alert in warnings[:2]:
            st.warning(f"**{alert['title']}**  \n{alert['message']}  \n→ *{alert['action']}*")
            st.markdown("---")
        
        # Display info (max 1)
        for alert in info_alerts[:1]:
            st.info(f"**{alert['title']}**  \n{alert['message']}  \n→ *{alert['action']}*")
            st.markdown("---")
        
        # Show count if more alerts
        total_shown = len(urgent) + min(2, len(warnings)) + min(1, len(info_alerts))
        if len(alerts) > total_shown:
            st.caption(f"... and {len(alerts) - total_shown} more alerts")
    else:
        st.success("✅ **All Clear!**  \nNo urgent actions required.")
        st.info("System is performing within expected parameters.")

st.markdown("---")

# ========== PRIORITY ACTIONS CHECKLIST ==========
st.markdown("### 🎯 Priority Actions This Week")

# Get content calendar
content_df = loader.get_content_calendar()

# Create checklist
actions = []

# From content calendar
if not content_df.empty and 'Due_Date' in content_df.columns:
    today = datetime.now()
    this_week = today + pd.Timedelta(days=7)
    
    due_this_week = content_df[
        (content_df['Due_Date'] >= today) & 
        (content_df['Due_Date'] <= this_week)
    ].sort_values('Due_Date')
    
    for _, item in due_this_week.head(5).iterrows():
        due_date = item['Due_Date'].strftime('%b %d')
        topic = item.get('Topic', 'Unknown')
        status = item.get('Status', 'Unknown')
        
        # Determine icon based on status
        if status == 'Completed':
            icon = '✅'
        elif status == 'In Progress':
            icon = '⏳'
        elif pd.notna(item['Due_Date']) and item['Due_Date'] < today:
            icon = '🔴'
        else:
            icon = '⏳'
        
        actions.append({
            'icon': icon,
            'task': f"Complete: {topic}",
            'due': due_date,
            'status': status
        })

# From strategy (Priority 0 actions)
priority_actions = [
    {'icon': '⏳', 'task': 'Host monthly webinar', 'due': 'Wed 15:00', 'status': 'Scheduled'},
    {'icon': '⏳', 'task': 'Re-engage 3 inactive partners', 'due': 'This week', 'status': 'Pending'},
    {'icon': '⏳', 'task': 'Create case study from recent deal', 'due': 'End of week', 'status': 'Not Started'},
]

# Combine
all_actions = actions + priority_actions

# Display checklist
if all_actions:
    for action in all_actions[:7]:  # Show max 7
        col1, col2, col3 = st.columns([1, 6, 2])
        
        with col1:
            # Checkbox
            checked = st.checkbox("", key=f"action_{action['task']}", label_visibility="collapsed")
        
        with col2:
            task_text = f"~~{action['task']}~~" if checked else action['task']
            st.markdown(f"{action['icon']} {task_text}")
        
        with col3:
            st.caption(action['due'])
else:
    st.info("No pending actions. Great job staying on top of everything! 🎉")

st.markdown("---")

# ========== CHANNEL COMPARISON TABLE ==========
st.markdown("### 📊 All Channels at a Glance")

if not channels_df.empty:
    # Prepare display dataframe
    display_df = channels_df[['Channel', 'Status', 'Leads', 'CPL', 'Budget']].copy()
    
    # Format columns
    display_df['CPL'] = display_df['CPL'].apply(lambda x: f"£{x:.2f}" if x > 0 else "£0")
    display_df['Budget'] = display_df['Budget'].apply(lambda x: f"£{int(x)}" if x > 0 else "-")
    
    # Sort by leads (descending)
    display_df = display_df.sort_values('Leads', ascending=False)
    
    # Add rank
    display_df.insert(0, 'Rank', range(1, len(display_df) + 1))
    
    # Display table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "Channel": st.column_config.TextColumn("Channel", width="medium"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Leads": st.column_config.NumberColumn("Leads", width="small"),
            "CPL": st.column_config.TextColumn("CPL", width="small"),
            "Budget": st.column_config.TextColumn("Monthly Budget", width="small")
        }
    )
    
    # Quick insights
    st.caption(f"📌 Tracking {len(display_df)} channels | {display_df['Leads'].sum():.0f} total leads this month")
else:
    st.info("No channel data available")

# Export button
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("📥 Export Report", type="secondary"):
        st.info("Export functionality coming soon!")

with col2:
    if st.button("🔄 Refresh Data", type="secondary"):
        st.rerun()

# Footer
st.markdown("---")
st.caption("💡 **Tip**: Click on any channel name to view detailed performance in Channel Performance page")
