# Page 1: Executive Overview
# High-level KPIs, trends, and alerts

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from config import load_custom_css  # COLORS not needed here
from utils.data_loader import get_data_loader
from utils.calculations import get_calculator
from utils.visualizations import get_chart_builder
from utils.session_state import initialize_session_state, DEFAULT_BENCHMARKS

# ── Initialize session state ───────────────────────────────────────────────────
initialize_session_state()
st.session_state.setdefault("data_loaded", False)
st.session_state.setdefault("excel_data", None)
st.session_state.setdefault("benchmarks", DEFAULT_BENCHMARKS.copy())
st.session_state.setdefault("last_upload_time", None)

# ── CSS ────────────────────────────────────────────────────────────────────────
load_custom_css()

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("📊 Executive Overview")
st.markdown("*High-level performance snapshot across all channels*")

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

# ── Data fetch (guard against None/empty) ──────────────────────────────────────
kpis = loader.get_kpi_data() or {}
channels_df = loader.get_channel_data()
weekly_trend = loader.get_weekly_trend_data()
alerts = loader.get_alerts() or []

# ── Last updated ───────────────────────────────────────────────────────────────
c1, c2 = st.columns([3, 1])
with c2:
    if st.session_state.get("last_upload_time"):
        ts = st.session_state["last_upload_time"].strftime("%Y-%m-%d %H:%M")
        st.caption(f"📅 Last updated: {ts}")

st.markdown("---")

# ── Helper for safe numerics ───────────────────────────────────────────────────
def _to_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return float(default)

# ── PRIMARY KPIs (Top Row) ─────────────────────────────────────────────────────
st.markdown("### 🎯 This Month's Performance")

k1, k2, k3, k4 = st.columns(4)

with k1:
    leads = int(_to_float(kpis.get("Total Leads", 0)))
    leads_prev = int(_to_float(kpis.get("Total Leads (Prev)", 232)))
    leads_change = calc.calculate_mom_change(leads, leads_prev)
    st.metric("TOTAL LEADS", calc.format_number(leads), delta=f"{leads_change:+.1f}% MoM")

    target = _to_float(st.session_state.benchmarks.get("monthly_lead_goal", DEFAULT_BENCHMARKS["monthly_lead_goal"]))
    progress = (leads / target * 100) if target > 0 else 0
    st.progress(min(progress / 100, 1.0))
    st.caption(f"{progress:.0f}% of {int(target)} target")

with k2:
    meetings = int(_to_float(kpis.get("Total Meetings", 0)))
    meetings_prev = int(_to_float(kpis.get("Total Meetings (Prev)", 58)))
    meetings_change = calc.calculate_mom_change(meetings, meetings_prev)
    st.metric("MEETINGS BOOKED", calc.format_number(meetings), delta=f"{meetings_change:+.1f}% MoM")

    if leads > 0:
        conversion = meetings / leads * 100
        st.caption(f"{conversion:.1f}% conversion rate")
        target_conv = _to_float(st.session_state.benchmarks.get("target_lead_to_meeting", DEFAULT_BENCHMARKS["target_lead_to_meeting"]))
        st.caption(("✅ Above" if conversion >= target_conv else "⚠️ Below") + f" {target_conv:.0f}% target")

with k3:
    deals = int(_to_float(kpis.get("Total Deals", 0)))
    deals_prev = int(_to_float(kpis.get("Total Deals (Prev)", 11)))
    deals_change = calc.calculate_mom_change(deals, deals_prev)
    st.metric("DEALS CLOSED", calc.format_number(deals), delta=f"{deals_change:+.1f}% MoM")

    if meetings > 0:
        win_rate = deals / meetings * 100
        st.caption(f"{win_rate:.1f}% win rate")
        target_win = _to_float(st.session_state.benchmarks.get("target_meeting_to_deal", DEFAULT_BENCHMARKS["target_meeting_to_deal"]))
        st.caption(("✅ Above" if win_rate >= target_win else "⚠️ Below") + f" {target_win:.0f}% target")

with k4:
    pipeline = _to_float(kpis.get("Pipeline Value", 0))
    st.metric("PIPELINE VALUE", calc.format_currency(pipeline), delta="+12% MoM")
    weighted = pipeline * 0.35
    st.caption(f"{calc.format_currency(weighted)} weighted")
    st.caption(f"Avg: {calc.format_currency(pipeline / max(deals, 1))} per deal")

st.markdown("---")

# ── SECONDARY KPIs (Bottom Row) ────────────────────────────────────────────────
st.markdown("### 💰 Efficiency Metrics")

e1, e2, e3, e4 = st.columns(4)

with e1:
    cpl = _to_float(kpis.get("Avg CPL", 0))
    cpl_prev = _to_float(kpis.get("Avg CPL (Prev)", 45.00))
    cpl_change = cpl - cpl_prev
    st.metric("AVG COST PER LEAD", f"£{cpl:.2f}", delta=f"£{cpl_change:+.2f} vs last month", delta_color="inverse")
    target_cpl = _to_float(st.session_state.benchmarks.get("target_cpl", DEFAULT_BENCHMARKS["target_cpl"]))
    st.caption(("✅ Below" if cpl <= target_cpl else "⚠️ Above") + f" £{target_cpl:.0f} target")

with e2:
    lead_to_meeting = _to_float(kpis.get("Lead to Meeting %", 0))
    st.metric("LEAD → MEETING", f"{lead_to_meeting:.1f}%", delta="+2.1% vs last month")
    target = _to_float(st.session_state.benchmarks.get("target_lead_to_meeting", DEFAULT_BENCHMARKS["target_lead_to_meeting"]))
    st.caption(f"Target: {target:.0f}%")

with e3:
    meeting_to_deal = _to_float(kpis.get("Meeting to Deal %", 0))
    st.metric("MEETING → DEAL", f"{meeting_to_deal:.1f}%", delta="-1.3% vs last month", delta_color="inverse")
    target = _to_float(st.session_state.benchmarks.get("target_meeting_to_deal", DEFAULT_BENCHMARKS["target_meeting_to_deal"]))
    st.caption(f"Target: {target:.0f}%")

with e4:
    avg_deal = _to_float(kpis.get("Avg Deal Size", 0))
    st.metric("AVG DEAL SIZE", calc.format_currency(avg_deal), delta="+£3K vs last month")
    st.caption("Median: £45K")

st.markdown("---")

# ========== WEEKLY TREND CHART ==========
st.markdown("### 📈 Weekly Lead Trend (Last 12 Weeks)")

# Create trend chart with new accessible colors
trend_fig = charts.create_kpi_trend_chart(
    weekly_trend,
    title="Weekly Lead Trend (Last 12 Weeks)",
    palette="okabe_ito",   # high-contrast, color-blind-safe
    fill_opacity=0.55       # tweak transparency if desired (0.4–0.6 works well)
)

st.plotly_chart(trend_fig, use_container_width=True)


    t1, t2, t3 = st.columns(3)

    with t1:
        totals = weekly_trend.drop(columns=["Week"]).sum(axis=1)
        recent_avg = totals.tail(4).mean() if len(totals) >= 4 else totals.mean()
        older_avg = totals.head(4).mean() if len(totals) >= 4 else totals.mean()
        trend_pct = calc.calculate_mom_change(recent_avg, older_avg)
        if trend_pct > 5:
            st.success(f"📈 **Trending Up**: {trend_pct:+.1f}% vs 8 weeks ago")
        elif trend_pct < -5:
            st.error(f"📉 **Trending Down**: {trend_pct:+.1f}% vs 8 weeks ago")
        else:
            st.info(f"→ **Stable**: {trend_pct:+.1f}% vs 8 weeks ago")

    with t2:
        weekly_totals = totals
        best_week_leads = int(weekly_totals.max() if not weekly_totals.empty else 0)
        st.info(f"🏆 **Best Week**: {best_week_leads} leads")

    with t3:
        std_dev = weekly_totals.std() if len(weekly_totals) > 1 else 0
        mean_leads = weekly_totals.mean() if len(weekly_totals) > 0 else 0
        consistency = (1 - (std_dev / mean_leads)) * 100 if mean_leads > 0 else 0
        if consistency > 80:
            st.success(f"✅ **Consistent**: {consistency:.0f}% stable")
        else:
            st.warning(f"⚠️ **Variable**: {consistency:.0f}% consistency")
else:
    st.info("Trend data not available yet.")
st.markdown("---")

# ── TOP PERFORMERS & ACTION REQUIRED ───────────────────────────────────────────
perf_col, alert_col = st.columns(2)

with perf_col:
    st.markdown("### 🏆 Top Performers This Month")
    if isinstance(channels_df, pd.DataFrame) and not channels_df.empty:
        # Ensure required columns exist
        for col in ["Leads", "CPL", "Conversion", "Channel"]:
            if col not in channels_df.columns:
                channels_df[col] = 0

        # Build efficiency safely
        def _eff(row):
            return calc.calculate_channel_efficiency_score(
                _to_float(row.get("Leads", 0)),
                _to_float(row.get("CPL", 0)),
                _to_float(row.get("Conversion", 20)),
            )
        channels_df = channels_df.copy()
        channels_df["Efficiency"] = channels_df.apply(_eff, axis=1)

        top_channels = channels_df.nlargest(3, "Efficiency") if "Efficiency" in channels_df else channels_df.head(3)

        for idx, (_, channel) in enumerate(top_channels.iterrows(), 1):
            st.markdown(f"**{idx}. {channel.get('Channel', 'Unknown')}**")
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.caption(f"**{int(_to_float(channel.get('Leads', 0)))}** leads")
            with mc2:
                cpl_val = _to_float(channel.get("CPL", 0))
                st.caption(f"**£{cpl_val:.2f}** CPL" if cpl_val > 0 else "**£0** CPL")
            with mc3:
                conv = _to_float(channel.get("Conversion", 0))
                st.caption(f"**{conv:.1f}%** conv" if conv > 0 else "N/A conv")

            # Indicator
            if cpl_val == 0:
                st.success("✅ Organic channel - Excellent ROI")
            elif cpl_val < 25:
                st.success("✅ Great CPL - Keep scaling")
            elif cpl_val < 50:
                st.info("→ Good CPL - Monitor closely")
            else:
                st.warning("⚠️ High CPL - Review strategy")
            st.markdown("---")
    else:
        st.info("No channel data available")

with alert_col:
    st.markdown("### 🚨 Action Required")
    if alerts:
        urgent = [a for a in alerts if a.get("type") == "urgent"]
        warnings = [a for a in alerts if a.get("type") == "warning"]
        info_alerts = [a for a in alerts if a.get("type") == "info"]

        for alert in urgent:
            st.error(f"**{alert.get('title','Alert')}**  \n{alert.get('message','')}  \n→ *{alert.get('action','') }*")
            st.markdown("---")

        for alert in warnings[:2]:
            st.warning(f"**{alert.get('title','Alert')}**  \n{alert.get('message','')}  \n→ *{alert.get('action','') }*")
            st.markdown("---")

        for alert in info_alerts[:1]:
            st.info(f"**{alert.get('title','Alert')}**  \n{alert.get('message','')}  \n→ *{alert.get('action','') }*")
            st.markdown("---")

        total_shown = len(urgent) + min(2, len(warnings)) + min(1, len(info_alerts))
        if len(alerts) > total_shown:
            st.caption(f"... and {len(alerts) - total_shown} more alerts")
    else:
        st.success("✅ **All Clear!**  \nNo urgent actions required.")
        st.info("System is performing within expected parameters.")

st.markdown("---")

# ── PRIORITY ACTIONS CHECKLIST ─────────────────────────────────────────────────
st.markdown("### 🎯 Priority Actions This Week")

content_df = loader.get_content_calendar()
actions = []

if isinstance(content_df, pd.DataFrame) and not content_df.empty and "Due_Date" in content_df.columns:
    # Ensure datetime
    if not pd.api.types.is_datetime64_any_dtype(content_df["Due_Date"]):
        with pd.option_context("mode.chained_assignment", None):
            content_df["Due_Date"] = pd.to_datetime(content_df["Due_Date"], errors="coerce")

    today = datetime.now()
    this_week = today + timedelta(days=7)
    due_this_week = content_df[
        (content_df["Due_Date"].notna()) &
        (content_df["Due_Date"] >= today) &
        (content_df["Due_Date"] <= this_week)
    ].sort_values("Due_Date")

    for _, item in due_this_week.head(5).iterrows():
        due_date = item["Due_Date"].strftime("%b %d")
        topic = item.get("Topic", "Unknown")
        status = item.get("Status", "Unknown")

        if status == "Completed":
            icon = "✅"
        elif status == "In Progress":
            icon = "⏳"
        elif pd.notna(item["Due_Date"]) and item["Due_Date"] < today:
            icon = "🔴"
        else:
            icon = "⏳"

        actions.append({"icon": icon, "task": f"Complete: {topic}", "due": due_date, "status": status})

# Strategy-driven priorities (static examples)
priority_actions = [
    {"icon": "⏳", "task": "Host monthly webinar", "due": "Wed 15:00", "status": "Scheduled"},
    {"icon": "⏳", "task": "Re-engage 3 inactive partners", "due": "This week", "status": "Pending"},
    {"icon": "⏳", "task": "Create case study from recent deal", "due": "End of week", "status": "Not Started"},
]

all_actions = actions + priority_actions
if all_actions:
    for action in all_actions[:7]:
        a1, a2, a3 = st.columns([1, 6, 2])
        with a1:
            st.checkbox("", key=f"action_{action['task']}", label_visibility="collapsed")
        with a2:
            st.markdown(f"{action['icon']} {action['task']}")
        with a3:
            st.caption(action["due"])
else:
    st.info("No pending actions. Great job staying on top of everything! 🎉")

st.markdown("---")

# ── CHANNEL COMPARISON TABLE ───────────────────────────────────────────────────
st.markdown("### 📊 All Channels at a Glance")

if isinstance(channels_df, pd.DataFrame) and not channels_df.empty:
    # Ensure required columns
    for col in ["Channel", "Status", "Leads", "CPL", "Budget"]:
        if col not in channels_df.columns:
            channels_df[col] = 0

    display_df = channels_df[["Channel", "Status", "Leads", "CPL", "Budget"]].copy()

    display_df["CPL"] = display_df["CPL"].apply(lambda x: f"£{_to_float(x):.2f}" if _to_float(x) > 0 else "£0")
    display_df["Budget"] = display_df["Budget"].apply(lambda x: f"£{int(_to_float(x))}" if _to_float(x) > 0 else "-")

    display_df = display_df.sort_values("Leads", ascending=False).reset_index(drop=True)
    display_df.insert(0, "Rank", range(1, len(display_df) + 1))

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
            "Budget": st.column_config.TextColumn("Monthly Budget", width="small"),
        },
    )

    st.caption(f"📌 Tracking {len(display_df)} channels | {int(pd.to_numeric(channels_df['Leads'], errors='coerce').fillna(0).sum())} total leads this month")
else:
    st.info("No channel data available")

# ── Footer actions ─────────────────────────────────────────────────────────────
st.markdown("---")
b1, b2, _ = st.columns([1, 1, 2])
with b1:
    if st.button("📥 Export Report", type="secondary"):
        st.info("Export functionality coming soon!")
with b2:
    if st.button("🔄 Refresh Data", type="secondary"):
        st.rerun()

st.markdown("---")
st.caption("💡 **Tip**: Use the Channel Performance page for deep dives by channel.")
