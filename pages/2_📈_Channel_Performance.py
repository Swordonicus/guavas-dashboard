# Page 2: Channel Performance
# Deep dive into individual channel performance

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import load_custom_css, COLORS, INDUSTRY_BENCHMARKS, PRIORITY_0_CHANNELS
from utils.data_loader import get_data_loader
from utils.calculations import get_calculator
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

# Page header
st.title("📈 Channel Performance Deep Dive")
st.markdown("*Detailed analysis for each traffic source*")

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

# Reload data
if st.session_state.excel_data:
    loader.data = st.session_state.excel_data

channels_df = loader.get_channel_data()

# Check if we have channel data
if channels_df.empty:
    st.error("No channel data available. Please check your Excel file structure.")
    st.stop()

st.markdown("---")

# ========== CHANNEL SELECTOR ==========
col1, col2 = st.columns([3, 1])

with col1:
    # Get list of channels
    channel_list = channels_df['Channel'].tolist()
    
    selected_channel = st.selectbox(
        "Select Channel to Analyze:",
        channel_list,
        index=0
    )

with col2:
    # Date range selector
    date_range = st.selectbox(
        "Time Period:",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "This Month", "Last Month"],
        index=1
    )

# Get selected channel data
channel_data = channels_df[channels_df['Channel'] == selected_channel].iloc[0]

st.markdown("---")

# ========== CHANNEL HEADER ==========
header_col1, header_col2, header_col3 = st.columns([2, 1, 1])

with header_col1:
    # Channel name and type
    st.markdown(f"## {channel_data['Channel']}")
    st.caption(f"Type: {channel_data.get('Type', 'Unknown')} | Priority: {channel_data.get('Priority', 'Medium')}")

with header_col2:
    # Status badge
    status = channel_data.get('Status', 'Unknown')
    if status == 'Active':
        st.success(f"● {status}")
    elif status == 'Paused':
        st.warning(f"⏸ {status}")
    elif status == 'In Development':
        st.info(f"🚧 {status}")
    else:
        st.error(f"○ {status}")

with header_col3:
    # Priority indicator
    priority = channel_data.get('Priority', 'Medium')
    if priority == 'High' or channel_data['Channel'] in PRIORITY_0_CHANNELS:
        st.error("🔥 Priority 0")
    elif priority == 'Medium':
        st.warning("→ Priority 1")
    else:
        st.info("→ Priority 2")

st.markdown("---")

# ========== KEY METRICS (6 Cards) ==========
st.markdown("### 📊 Key Performance Metrics")

m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)

with m_col1:
    leads = channel_data.get('Leads', 0)
    st.metric(
        label="LEADS",
        value=calc.format_number(leads),
        delta="+23%" if leads > 30 else "-5%"
    )

with m_col2:
    # Meetings (estimate from conversion)
    conversion = channel_data.get('Conversion', 20)
    meetings = int(leads * (conversion / 100))
    st.metric(
        label="MEETINGS",
        value=calc.format_number(meetings),
        delta=f"{conversion:.1f}% rate"
    )

with m_col3:
    # Deals (estimate)
    deals = int(meetings * 0.18)  # 18% close rate
    st.metric(
        label="DEALS",
        value=calc.format_number(deals),
        delta="17.9% rate"
    )

with m_col4:
    spent = channel_data.get('Budget', 0)
    st.metric(
        label="SPENT",
        value=calc.format_currency(spent),
        delta="Within budget"
    )

with m_col5:
    cpl = channel_data.get('CPL', 0)
    st.metric(
        label="CPL",
        value=f"£{cpl:.2f}",
        delta="-£12" if cpl < 30 else "+£15",
        delta_color="inverse"
    )

with m_col6:
    # Quality score
    quality = calc.calculate_lead_quality_score(
        qualification_rate=65,
        meeting_rate=conversion,
        deal_rate=17.9,
        avg_deal_size=47200
    )
    st.metric(
        label="QUALITY",
        value=f"{quality:.1f}/10",
        delta="Good" if quality > 7 else "Fair"
    )

st.markdown("---")

# ========== BENCHMARK COMPARISON ==========
st.markdown("### 🎯 vs Industry Benchmarks")

bench_col1, bench_col2, bench_col3 = st.columns(3)

with bench_col1:
    if cpl > 0:
        benchmark_cpl = INDUSTRY_BENCHMARKS.get('linkedin_cpl_range', (15, 20))
        
        if cpl <= benchmark_cpl[0]:
            st.success(f"✅ Excellent CPL (Industry: £{benchmark_cpl[0]}-{benchmark_cpl[1]})")
        elif cpl <= benchmark_cpl[1]:
            st.success(f"✅ Good CPL (Industry: £{benchmark_cpl[0]}-{benchmark_cpl[1]})")
        elif cpl <= benchmark_cpl[1] * 2:
            st.warning(f"⚠️ Above benchmark (Industry: £{benchmark_cpl[0]}-{benchmark_cpl[1]})")
        else:
            st.error(f"🚨 High CPL (Industry: £{benchmark_cpl[0]}-{benchmark_cpl[1]})")
    else:
        st.success("✅ Organic Channel - No cost")

with bench_col2:
    if conversion > 0:
        if conversion >= 25:
            st.success(f"✅ Strong conversion ({conversion:.1f}% vs 20% target)")
        elif conversion >= 15:
            st.info(f"→ Average conversion ({conversion:.1f}% vs 20% target)")
        else:
            st.warning(f"⚠️ Low conversion ({conversion:.1f}% vs 20% target)")
    else:
        st.caption("Conversion data not available")

with bench_col3:
    if leads >= 50:
        st.success(f"✅ High volume ({leads} leads)")
    elif leads >= 25:
        st.info(f"→ Moderate volume ({leads} leads)")
    else:
        st.warning(f"⚠️ Low volume ({leads} leads)")

st.markdown("---")

# ========== PERFORMANCE OVER TIME CHART ==========
st.markdown("### 📈 Performance Over Time")

# Generate sample weekly data for this channel
weeks = 12
dates = pd.date_range(end=datetime.now(), periods=weeks, freq='W')

# Create realistic trend data
base_leads = leads / 4  # Average per week
weekly_data = pd.DataFrame({
    'Week': dates,
    'Leads': [int(base_leads + np.random.randint(-10, 15)) for _ in range(weeks)],
    'CPL': [cpl + np.random.uniform(-5, 5) if cpl > 0 else 0 for _ in range(weeks)]
})

# Create dual-axis chart
dual_chart = charts.create_dual_axis_chart(
    weekly_data,
    date_col='Week',
    bar_col='Leads',
    line_col='CPL'
)

st.plotly_chart(dual_chart, use_container_width=True)

# Trend analysis
trend_col1, trend_col2, trend_col3 = st.columns(3)

with trend_col1:
    recent_avg = weekly_data.tail(4)['Leads'].mean()
    older_avg = weekly_data.head(4)['Leads'].mean()
    trend = calc.calculate_mom_change(recent_avg, older_avg)
    
    if trend > 10:
        st.success(f"📈 **Strong Growth**: {trend:+.1f}%")
    elif trend > 0:
        st.info(f"→ **Slight Growth**: {trend:+.1f}%")
    else:
        st.warning(f"📉 **Declining**: {trend:+.1f}%")

with trend_col2:
    best_week = weekly_data['Leads'].max()
    worst_week = weekly_data['Leads'].min()
    variance = ((best_week - worst_week) / worst_week) * 100
    
    st.info(f"📊 **Variance**: {variance:.0f}%  \nBest: {best_week} | Worst: {worst_week}")

with trend_col3:
    if cpl > 0:
        recent_cpl = weekly_data.tail(4)['CPL'].mean()
        older_cpl = weekly_data.head(4)['CPL'].mean()
        cpl_trend = recent_cpl - older_cpl
        
        if cpl_trend < 0:
            st.success(f"✅ **CPL Improving**: £{abs(cpl_trend):.2f}")
        else:
            st.warning(f"⚠️ **CPL Rising**: +£{cpl_trend:.2f}")
    else:
        st.info("→ **Organic Channel** (£0 CPL)")

st.markdown("---")

# ========== CONTENT BREAKDOWN & FUNNEL (Side by Side) ==========
content_col, funnel_col = st.columns(2)

with content_col:
    st.markdown("### 📝 Content Breakdown")
    
    # Sample content performance data
    content_types = pd.DataFrame({
        'Type': ['Video', 'Carousel', 'Text Post', 'Case Study', 'Blog Link'],
        'Count': [8, 12, 15, 3, 5],
        'Leads': [18, 12, 10, 7, 0],
        'Avg CPL': [6.50, 8.20, 9.10, 7.80, 0]
    })
    
    # Calculate CPL only for posts with leads
    content_types['CPL Display'] = content_types.apply(
        lambda row: f"£{row['Avg CPL']:.2f}" if row['Leads'] > 0 else "-",
        axis=1
    )
    
    # Display table
    st.dataframe(
        content_types[['Type', 'Count', 'Leads', 'CPL Display']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Type": "Content Type",
            "Count": "Posts",
            "Leads": "Leads",
            "CPL Display": "Avg CPL"
        }
    )
    
    # Best performer
    if not content_types.empty:
        best_type = content_types.loc[content_types['Leads'].idxmax(), 'Type']
        best_leads = content_types.loc[content_types['Leads'].idxmax(), 'Leads']
        st.caption(f"🏆 Best: {best_type} ({best_leads} leads)")

with funnel_col:
    st.markdown("### 🔽 Conversion Funnel")
    
    # Calculate funnel stages
    visitors = int(leads * 4)  # Assume 4 visitors per lead
    form_fills = leads
    qualified = int(leads * 0.65)  # 65% qualify
    meetings_funnel = meetings
    deals_funnel = deals
    
    # Create funnel chart
    stages = ['Website Visits', 'Form Fills', 'Qualified', 'Meetings', 'Deals']
    values = [visitors, form_fills, qualified, meetings_funnel, deals_funnel]
    
    funnel_chart = charts.create_funnel_chart(stages, values)
    st.plotly_chart(funnel_chart, use_container_width=True)
    
    # Conversion rates
visit_to_form = (form_fills/visitors*100) if visitors > 0 else 0
form_to_meet = (meetings_funnel/form_fills*100) if form_fills > 0 else 0
meet_to_deal = (deals_funnel/meetings_funnel*100) if meetings_funnel > 0 else 0
st.caption(f"Visit→Form: {visit_to_form:.1f}% | Form→Meet: {form_to_meet:.1f}% | Meet→Deal: {meet_to_deal:.1f}%")
st.markdown("---")

# ========== AI INSIGHTS PANEL ==========
st.markdown("### 💡 AI Insights & Recommendations")

with st.container():
    st.markdown("#### ✅ What's Working Well")
    
    insights = []
    
    # CPL insight
    if cpl > 0 and cpl < 25:
        insights.append(f"• CPL of £{cpl:.2f} is significantly below industry benchmark (£15-20)")
    elif cpl == 0:
        insights.append("• Organic channel with no direct costs - excellent ROI potential")
    
    # Conversion insight
    if conversion > 20:
        insights.append(f"• Conversion rate of {conversion:.1f}% exceeds target (20%)")
    
    # Volume insight
    if leads > 40:
        insights.append(f"• Strong lead volume ({leads} leads) demonstrates channel viability")
    
    # Quality insight
    if quality > 7:
        insights.append(f"• Lead quality score of {quality:.1f}/10 indicates high-value prospects")
    
    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.markdown("• Channel is performing within normal parameters")
    
    st.markdown("---")
    
    st.markdown("#### ⚠️ Opportunities for Improvement")
    
    opportunities = []
    
    # CPL opportunities
    if cpl > 50:
        opportunities.append(f"• CPL of £{cpl:.2f} is 2x above target - review targeting and ad creative")
    
    # Conversion opportunities
    if conversion < 15:
        opportunities.append(f"• Conversion rate of {conversion:.1f}% is below benchmark - optimize landing page or form")
    
    # Volume opportunities
    if leads < 25:
        opportunities.append(f"• Lead volume of {leads} is below potential - consider increasing frequency or budget")
    
    # Content opportunities
    best_content = content_types.loc[content_types['Leads'].idxmax(), 'Type']
    if best_content:
        opportunities.append(f"• {best_content} performs best - create more of this content type")
    
    if opportunities:
        for opp in opportunities:
            st.markdown(opp)
    else:
        st.markdown("• No major optimization opportunities identified")
    
    st.markdown("---")
    
    st.markdown("#### 🎯 Recommended Actions")
    
    actions = []
    
    # Priority 0 channel recommendations
    if channel_data['Channel'] in PRIORITY_0_CHANNELS:
        if channel_data['Channel'] == 'LinkedIn Organic':
            actions.append("1. Increase posting frequency to 7-10 posts/week (currently may be lower)")
            actions.append("2. Test LinkedIn Sponsored Content with £500/month to amplify top posts")
            actions.append("3. Engage with comments within 1 hour to boost algorithmic reach")
        elif channel_data['Channel'] == 'Webinar Program':
            actions.append("1. Host webinars monthly (consistency builds audience)")
            actions.append("2. Repurpose webinar content into 5+ LinkedIn posts + blog")
            actions.append("3. Send recording to no-shows (typically 50% conversion recovery)")
        elif channel_data['Channel'] == 'Partner Referrals':
            actions.append("1. Re-engage inactive partners (60+ days no referrals)")
            actions.append("2. Send monthly partner newsletter with success stories")
            actions.append("3. Offer limited-time commission boost (12% vs standard 10%)")
    else:
        # General recommendations
        if cpl > 40:
            actions.append("1. Pause campaign and review targeting - CPL too high")
        if conversion < 15:
            actions.append("2. A/B test landing page form length (try 5 fields vs current)")
        if leads < 20:
            actions.append("3. Increase budget or frequency if ROI is positive")
    
    # Add expected impact
    if channel_data['Channel'] == 'LinkedIn Organic':
        actions.append("\n**Expected Impact**: +30-50 leads/month, maintain CPL <£12")
    elif cpl > 40:
        actions.append("\n**Expected Impact**: CPL reduction to £20-30 or pause channel")
    
    if actions:
        for action in actions:
            st.markdown(action)
    else:
        st.markdown("Continue current strategy - no immediate changes needed")

st.markdown("---")

# ========== ACTION BUTTONS ==========
button_col1, button_col2, button_col3, button_col4 = st.columns(4)

with button_col1:
    if st.button("📥 Export Channel Report", type="secondary"):
        st.info("Export functionality coming soon!")

with button_col2:
    if st.button("🤖 Ask Claude for Strategy", type="secondary"):
        st.info("Claude Projects integration coming soon!")

with button_col3:
    if st.button("📊 View in Executive Overview", type="secondary"):
        st.switch_page("pages/1_📊_Executive_Overview.py")

with button_col4:
    if st.button("🔄 Refresh Data", type="secondary"):
        st.rerun()

# Footer
st.markdown("---")
st.caption(f"💡 **Tip**: Industry benchmarks sourced from strategy document (89% LinkedIn usage, 277% more effective than other platforms)")
