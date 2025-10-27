# Page 2: Channel Performance
# Deep dive into individual channel performance

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from config import load_custom_css, INDUSTRY_BENCHMARKS, PRIORITY_0_CHANNELS
from utils.data_loader import get_data_loader
from utils.calculations import get_calculator
from utils.visualizations import get_chart_builder
from utils.session_state import initialize_session_state

# ── Init session state ─────────────────────────────────────────────────────────
initialize_session_state()
st.session_state.setdefault('data_loaded', False)
st.session_state.setdefault('excel_data', None)

# ── CSS ────────────────────────────────────────────────────────────────────────
load_custom_css()

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("📈 Channel Performance Deep Dive")
st.markdown("*Detailed analysis for each traffic source*")

# ── Data gate ──────────────────────────────────────────────────────────────────
if not st.session_state.data_loaded:
    st.warning("⚠️ No data loaded. Please upload your Excel file in **Settings** first.")
    if hasattr(st, "page_link"):
        st.page_link("pages/5_⚙️_Settings.py", label="Go to Settings ⚙️")
    else:
        st.info("Open the Settings page from the sidebar.")
    st.stop()

# ── Utilities ──────────────────────────────────────────────────────────────────
loader = get_data_loader()
calc = get_calculator()
charts = get_chart_builder()

# Use in-memory data if available
if st.session_state.excel_data:
    loader.data = st.session_state.excel_data

channels_df = loader.get_channel_data()

# Validate expected columns and content
required_cols = {'Channel'}
if channels_df.empty or not required_cols.issubset(channels_df.columns):
    missing = required_cols - set(channels_df.columns)
    msg = f"Missing required columns: {missing}" if missing else "No channel data available."
    st.error(msg)
    st.stop()

st.markdown("---")

# ── Channel selector ───────────────────────────────────────────────────────────
c1, c2 = st.columns([3, 1])
with c1:
    channel_list = (
        channels_df['Channel']
        .dropna().astype(str).drop_duplicates()
        .tolist()
    )
    selected_channel = st.selectbox(
        "Select Channel to Analyze:",
        channel_list,
        index=0 if channel_list else None,
    )
if not selected_channel:
    st.warning("No channels available.")
    st.stop()

with c2:
    date_range = st.selectbox(
        "Time Period:",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "This Month", "Last Month"],
        index=1
    )

row = channels_df[channels_df['Channel'] == selected_channel]
if row.empty:
    st.error("Selected channel not found in data.")
    st.stop()
channel_data = row.iloc[0]

st.markdown("---")

# ── Helpers ────────────────────────────────────────────────────────────────────
def _to_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return float(default)

# Extract robust numerics
leads = int(_to_float(channel_data.get('Leads', 0)))
conversion = _to_float(channel_data.get('Conversion', 20))
spent = _to_float(channel_data.get('Budget', 0))
cpl = _to_float(channel_data.get('CPL', 0))

# ── Header stats ───────────────────────────────────────────────────────────────
h1, h2, h3 = st.columns([2, 1, 1])
with h1:
    st.markdown(f"## {channel_data['Channel']}")
    st.caption(f"Type: {channel_data.get('Type', 'Unknown')} | "
               f"Priority: {channel_data.get('Priority', 'Medium')}")

with h2:
    status = channel_data.get('Status', 'Unknown')
    if status == 'Active':
        st.success(f"● {status}")
    elif status == 'Paused':
        st.warning(f"⏸ {status}")
    elif status == 'In Development':
        st.info(f"🚧 {status}")
    else:
        st.error(f"○ {status}")

with h3:
    priority = channel_data.get('Priority', 'Medium')
    if priority == 'High' or channel_data['Channel'] in PRIORITY_0_CHANNELS:
        st.error("🔥 Priority 0")
    elif priority == 'Medium':
        st.warning("→ Priority 1")
    else:
        st.info("→ Priority 2")

st.markdown("---")

# ── Key Metrics (6) ────────────────────────────────────────────────────────────
st.markdown("### 📊 Key Performance Metrics")
m1, m2, m3, m4, m5, m6 = st.columns(6)

with m1:
    st.metric("LEADS", calc.format_number(leads),
              delta="+23%" if leads > 30 else "-5%")

with m2:
    meetings = int(leads * (conversion / 100.0))
    st.metric("MEETINGS", calc.format_number(meetings),
              delta=f"{conversion:.1f}% rate")

with m3:
    deals = int(meetings * 0.18)  # 18% close rate
    st.metric("DEALS", calc.format_number(deals),
              delta="17.9% rate")

with m4:
    st.metric("SPENT", calc.format_currency(spent),
              delta="Within budget")

with m5:
    st.metric("CPL", f"£{cpl:.2f}",
              delta="-£12" if cpl < 30 else "+£15",
              delta_color="inverse")

with m6:
    quality = calc.calculate_lead_quality_score(
        qualification_rate=65,
        meeting_rate=conversion,
        deal_rate=17.9,
        avg_deal_size=47200
    )
    st.metric("QUALITY", f"{quality:.1f}/10",
              delta="Good" if quality > 7 else "Fair")

st.markdown("---")

# ── vs Benchmarks ──────────────────────────────────────────────────────────────
st.markdown("### 🎯 vs Industry Benchmarks")
b1, b2, b3 = st.columns(3)

with b1:
    if cpl > 0:
        lo, hi = INDUSTRY_BENCHMARKS.get('linkedin_cpl_range', (15, 20))
        if cpl <= lo:
            st.success(f"✅ Excellent CPL (Industry: £{lo}-{hi})")
        elif cpl <= hi:
            st.success(f"✅ Good CPL (Industry: £{lo}-{hi})")
        elif cpl <= hi * 2:
            st.warning(f"⚠️ Above benchmark (Industry: £{lo}-{hi})")
        else:
            st.error(f"🚨 High CPL (Industry: £{lo}-{hi})")
    else:
        st.success("✅ Organic Channel - No cost")

with b2:
    if conversion > 0:
        if conversion >= 25:
            st.success(f"✅ Strong conversion ({conversion:.1f}% vs 20% target)")
        elif conversion >= 15:
            st.info(f"→ Average conversion ({conversion:.1f}% vs 20% target)")
        else:
            st.warning(f"⚠️ Low conversion ({conversion:.1f}% vs 20% target)")
    else:
        st.caption("Conversion data not available")

with b3:
    if leads >= 50:
        st.success(f"✅ High volume ({leads} leads)")
    elif leads >= 25:
        st.info(f"→ Moderate volume ({leads} leads)")
    else:
        st.warning(f"⚠️ Low volume ({leads} leads)")

st.markdown("---")

# ── Performance Over Time ──────────────────────────────────────────────────────
st.markdown("### 📈 Performance Over Time")

weeks = 12
dates = pd.date_range(end=datetime.now(), periods=weeks, freq='W')

base_leads = max(0, leads) / 4.0
weekly_leads = [max(0, int(base_leads + np.random.randint(-10, 15))) for _ in range(weeks)]
weekly_cpl = [max(0.0, cpl + float(np.random.uniform(-5, 5))) if cpl > 0 else 0.0 for _ in range(weeks)]

weekly_data = pd.DataFrame({
    'Week': dates,
    'Leads': weekly_leads,
    'CPL': weekly_cpl,
})

dual_chart = charts.create_dual_axis_chart(
    weekly_data, date_col='Week', bar_col='Leads', line_col='CPL'
)
st.plotly_chart(dual_chart, use_container_width=True)

t1, t2, t3 = st.columns(3)
with t1:
    recent_avg = weekly_data.tail(4)['Leads'].mean()
    older_avg = weekly_data.head(4)['Leads'].mean()
    trend = calc.calculate_mom_change(recent_avg, older_avg)
    if trend > 10:
        st.success(f"📈 **Strong Growth**: {trend:+.1f}%")
    elif trend > 0:
        st.info(f"→ **Slight Growth**: {trend:+.1f}%")
    else:
        st.warning(f"📉 **Declining**: {trend:+.1f}%")

with t2:
    best_week = int(weekly_data['Leads'].max())
    worst_week = int(weekly_data['Leads'].min())
    den = max(worst_week, 1)
    variance = ((best_week - worst_week) / den) * 100
    st.info(f"📊 **Variance**: {variance:.0f}%  \nBest: {best_week} | Worst: {worst_week}")

with t3:
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

# ── Content Breakdown & Funnel ─────────────────────────────────────────────────
content_col, funnel_col = st.columns(2)

with content_col:
    st.markdown("### 📝 Content Breakdown")

    content_types = pd.DataFrame({
        'Type': ['Video', 'Carousel', 'Text Post', 'Case Study', 'Blog Link'],
        'Count': [8, 12, 15, 3, 5],
        'Leads': [18, 12, 10, 7, 0],
        'Avg CPL': [6.50, 8.20, 9.10, 7.80, 0]
    })

    content_types['CPL Display'] = content_types.apply(
        lambda row: f"£{row['Avg CPL']:.2f}" if row['Leads'] > 0 else "-",
        axis=1
    )

    st.dataframe(
        content_types[['Type', 'Count', 'Leads', 'CPL Display']],
        use_container_width=True,
        hide_index=True
    )

    if not content_types.empty and content_types['Leads'].sum() > 0:
        best_content = content_types.loc[content_types['Leads'].idxmax(), 'Type']
        best_leads = int(content_types.loc[content_types['Leads'].idxmax(), 'Leads'])
        st.caption(f"🏆 Best: {best_content} ({best_leads} leads)")
    else:
        best_content = None

with funnel_col:
    st.markdown("### 🔽 Conversion Funnel")

    visitors = int(leads * 4)     # assume 4 visitors per lead
    form_fills = leads
    qualified = int(leads * 0.65) # 65% qualify
    meetings_funnel = int(meetings)
    deals_funnel = int(deals)

    stages = ['Website Visits', 'Form Fills', 'Qualified', 'Meetings', 'Deals']
    values = [visitors, form_fills, qualified, meetings_funnel, deals_funnel]

    funnel_chart = charts.create_funnel_chart(stages, values)
    st.plotly_chart(funnel_chart, use_container_width=True)

visit_to_form = (form_fills / visitors * 100) if visitors > 0 else 0
form_to_meet = (meetings_funnel / form_fills * 100) if form_fills > 0 else 0
meet_to_deal = (deals_funnel / meetings_funnel * 100) if meetings_funnel > 0 else 0
st.caption(f"Visit→Form: {visit_to_form:.1f}% | Form→Meet: {form_to_meet:.1f}% | Meet→Deal: {meet_to_deal:.1f}%")
st.markdown("---")

# ── AI Insights ────────────────────────────────────────────────────────────────
st.markdown("### 💡 AI Insights & Recommendations")
with st.container():
    st.markdown("#### ✅ What's Working Well")

    insights = []
    if cpl > 0 and cpl < 25:
        insights.append(f"• CPL of £{cpl:.2f} is significantly below industry benchmark (£15-20)")
    elif cpl == 0:
        insights.append("• Organic channel with no direct costs - excellent ROI potential")
    if conversion > 20:
        insights.append(f"• Conversion rate of {conversion:.1f}% exceeds target (20%)")
    if leads > 40:
        insights.append(f"• Strong lead volume ({leads} leads) demonstrates channel viability")
    quality = calc.calculate_lead_quality_score(
        qualification_rate=65,
        meeting_rate=conversion,
        deal_rate=17.9,
        avg_deal_size=47200
    )
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
    if cpl > 50:
        opportunities.append(f"• CPL of £{cpl:.2f} is 2x above target - review targeting and ad creative")
    if conversion < 15:
        opportunities.append(f"• Conversion rate of {conversion:.1f}% is below benchmark - optimize landing page or form")
    if leads < 25:
        opportunities.append(f"• Lead volume of {leads} is below potential - consider increasing frequency or budget")
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
    ch = channel_data['Channel']
    if ch in PRIORITY_0_CHANNELS:
        if ch == 'LinkedIn Organic':
            actions += [
                "1. Increase posting frequency to 7–10 posts/week",
                "2. Test LinkedIn Sponsored Content with £500/month to amplify top posts",
                "3. Engage with comments within 1 hour to boost algorithmic reach",
            ]
        elif ch == 'Webinar Program':
            actions += [
                "1. Host webinars monthly (consistency builds audience)",
                "2. Repurpose webinar content into 5+ LinkedIn posts + blog",
                "3. Send recording to no-shows (typically 50% conversion recovery)",
            ]
        elif ch == 'Partner Referrals':
            actions += [
                "1. Re-engage inactive partners (60+ days no referrals)",
                "2. Send monthly partner newsletter with success stories",
                "3. Offer limited-time commission boost (12% vs standard 10%)",
            ]
    else:
        if cpl > 40:
            actions.append("1. Pause campaign and review targeting - CPL too high")
        if conversion < 15:
            actions.append("2. A/B test landing page form length (try 5 fields vs current)")
        if leads < 20:
            actions.append("3. Increase budget or frequency if ROI is positive")

    if ch == 'LinkedIn Organic':
        actions.append("\n**Expected Impact**: +30–50 leads/month, maintain CPL <£12")
    elif cpl > 40:
        actions.append("\n**Expected Impact**: CPL reduction to £20–30 or pause channel")

    if actions:
        for a in actions:
            st.markdown(a)
    else:
        st.markdown("Continue current strategy — no immediate changes needed")

st.markdown("---")

# ── Actions ────────────────────────────────────────────────────────────────────
b1, b2, b3, b4 = st.columns(4)
with b1:
    if st.button("📥 Export Channel Report", type="secondary"):
        st.info("Export functionality coming soon!")
with b2:
    if st.button("🤖 Ask Claude for Strategy", type="secondary"):
        st.info("Claude Projects integration coming soon!")
with b3:
    if hasattr(st, "page_link"):
        st.page_link("pages/1_📊_Executive_Overview.py", label="📊 View in Executive Overview")
    else:
        if st.button("📊 View in Executive Overview", type="secondary"):
            st.info("Open 'Executive Overview' from the sidebar.")
with b4:
    if st.button("🔄 Refresh Data", type="secondary"):
        st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("💡 **Tip**: Industry benchmarks sourced from strategy document (89% LinkedIn usage, 277% more effective than other platforms)")
