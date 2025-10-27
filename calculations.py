# Guavas Dashboard - Calculations
# All metric calculations and data transformations

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MetricsCalculator:
    """Class to handle all metric calculations"""
    
    @staticmethod
    def calculate_cpl(spent, leads):
        """
        Calculate Cost Per Lead
        
        Args:
            spent: Amount spent (£)
            leads: Number of leads
            
        Returns:
            float: CPL in pounds
        """
        if leads == 0 or pd.isna(leads):
            return 0
        return spent / leads
    
    @staticmethod
    def calculate_conversion_rate(stage_a, stage_b):
        """
        Calculate conversion rate between two funnel stages
        
        Args:
            stage_a: Count at first stage
            stage_b: Count at second stage
            
        Returns:
            float: Conversion percentage
        """
        if stage_a == 0 or pd.isna(stage_a):
            return 0
        return (stage_b / stage_a) * 100
    
    @staticmethod
    def calculate_mom_change(current, previous):
        """
        Calculate Month-over-Month percentage change
        
        Args:
            current: Current month value
            previous: Previous month value
            
        Returns:
            float: Percentage change
        """
        if previous == 0 or pd.isna(previous):
            return 0
        return ((current - previous) / previous) * 100
    
    @staticmethod
    def calculate_wow_change(current, previous):
        """
        Calculate Week-over-Week percentage change
        
        Args:
            current: Current week value
            previous: Previous week value
            
        Returns:
            float: Percentage change
        """
        return MetricsCalculator.calculate_mom_change(current, previous)
    
    @staticmethod
    def calculate_roi(revenue, cost):
        """
        Calculate Return on Investment
        
        Args:
            revenue: Revenue generated
            cost: Cost invested
            
        Returns:
            float: ROI as ratio (e.g., 5.0 = 5:1 ROI)
        """
        if cost == 0 or pd.isna(cost):
            return 0
        return revenue / cost
    
    @staticmethod
    def calculate_ltv(avg_deal_size, avg_deals_per_customer, gross_margin=0.30):
        """
        Calculate Customer Lifetime Value
        
        Args:
            avg_deal_size: Average deal size
            avg_deals_per_customer: Average number of deals per customer
            gross_margin: Gross profit margin (default 30%)
            
        Returns:
            float: LTV in pounds
        """
        return avg_deal_size * avg_deals_per_customer * gross_margin
    
    @staticmethod
    def calculate_cac_payback_period(cac, monthly_revenue_per_customer, gross_margin=0.30):
        """
        Calculate CAC Payback Period in months
        
        Args:
            cac: Customer Acquisition Cost
            monthly_revenue_per_customer: Monthly revenue per customer
            gross_margin: Gross profit margin
            
        Returns:
            float: Months to payback CAC
        """
        monthly_profit = monthly_revenue_per_customer * gross_margin
        if monthly_profit == 0:
            return 0
        return cac / monthly_profit
    
    @staticmethod
    def calculate_pipeline_velocity(opportunities, avg_deal_size, win_rate, avg_sales_cycle_days):
        """
        Calculate Pipeline Velocity
        
        Formula: (# Opportunities * Deal Size * Win Rate) / Sales Cycle Length
        
        Args:
            opportunities: Number of opportunities
            avg_deal_size: Average deal size
            win_rate: Win rate as percentage (e.g., 25 for 25%)
            avg_sales_cycle_days: Average sales cycle in days
            
        Returns:
            float: Pipeline velocity (revenue per day)
        """
        if avg_sales_cycle_days == 0:
            return 0
        return (opportunities * avg_deal_size * (win_rate / 100)) / avg_sales_cycle_days
    
    @staticmethod
    def calculate_weighted_pipeline(pipeline_df):
        """
        Calculate weighted pipeline value based on stage probabilities
        
        Args:
            pipeline_df: DataFrame with columns: Stage, Value, Win_Rate
            
        Returns:
            float: Weighted pipeline value
        """
        if pipeline_df.empty:
            return 0
        
        if 'Value' in pipeline_df.columns and 'Win_Rate' in pipeline_df.columns:
            return (pipeline_df['Value'] * (pipeline_df['Win_Rate'] / 100)).sum()
        return 0
    
    @staticmethod
    def get_trend_indicator(current, previous, reverse_polarity=False):
        """
        Get trend indicator (up/down/neutral) and direction
        
        Args:
            current: Current value
            previous: Previous value
            reverse_polarity: If True, down is good (e.g., for CPL)
            
        Returns:
            tuple: (direction, symbol, color)
                direction: 'up', 'down', 'neutral'
                symbol: '↑', '↓', '→'
                color: 'success', 'danger', 'neutral'
        """
        if pd.isna(current) or pd.isna(previous) or previous == 0:
            return ('neutral', '→', 'neutral')
        
        change = ((current - previous) / abs(previous)) * 100
        
        if abs(change) < 1:  # Less than 1% change = neutral
            return ('neutral', '→', 'neutral')
        
        if change > 0:
            direction = 'up'
            symbol = '↑'
            color = 'danger' if reverse_polarity else 'success'
        else:
            direction = 'down'
            symbol = '↓'
            color = 'success' if reverse_polarity else 'danger'
        
        return (direction, symbol, color)
    
    @staticmethod
    def calculate_channel_efficiency_score(leads, cpl, conversion_rate, benchmark_cpl=25, benchmark_conversion=20):
        """
        Calculate overall channel efficiency score (0-100)
        
        Args:
            leads: Number of leads
            cpl: Cost per lead
            conversion_rate: Conversion percentage
            benchmark_cpl: Target CPL
            benchmark_conversion: Target conversion rate
            
        Returns:
            float: Efficiency score (0-100)
        """
        # Volume score (0-30 points)
        volume_score = min(30, (leads / 50) * 30)  # 50+ leads = full points
        
        # Cost efficiency score (0-35 points)
        if cpl > 0:
            cost_ratio = benchmark_cpl / cpl
            cost_score = min(35, cost_ratio * 35)
        else:
            cost_score = 35  # Organic = full points
        
        # Conversion score (0-35 points)
        conversion_ratio = conversion_rate / benchmark_conversion
        conversion_score = min(35, conversion_ratio * 35)
        
        return volume_score + cost_score + conversion_score
    
    @staticmethod
    def calculate_lead_quality_score(qualification_rate, meeting_rate, deal_rate, avg_deal_size, target_deal_size=47000):
        """
        Calculate lead quality score (1-10 scale)
        
        Args:
            qualification_rate: % of leads that qualify
            meeting_rate: % of qualified leads that book meeting
            deal_rate: % of meetings that close
            avg_deal_size: Average deal size
            target_deal_size: Target deal size
            
        Returns:
            float: Quality score (1-10)
        """
        # Conversion funnel score (0-6 points)
        funnel_score = (
            (qualification_rate / 100) * 2 +
            (meeting_rate / 100) * 2 +
            (deal_rate / 100) * 2
        )
        
        # Deal size score (0-4 points)
        size_ratio = avg_deal_size / target_deal_size
        size_score = min(4, size_ratio * 4)
        
        total = funnel_score + size_score
        return min(10, total)
    
    @staticmethod
    def forecast_monthly_leads(weekly_data, weeks_ahead=4):
        """
        Forecast leads for next month using simple moving average
        
        Args:
            weekly_data: DataFrame with 'Week' and lead counts
            weeks_ahead: Number of weeks to forecast
            
        Returns:
            dict: Forecasted leads by week
        """
        if weekly_data.empty or len(weekly_data) < 4:
            return {}
        
        # Calculate moving average of last 4 weeks
        recent_weeks = weekly_data.tail(4)
        
        # Get numeric columns (excluding Week column)
        numeric_cols = recent_weeks.select_dtypes(include=[np.number]).columns
        
        forecast = {}
        for col in numeric_cols:
            avg = recent_weeks[col].mean()
            # Add some variance (±10%)
            forecast[col] = [avg * (1 + np.random.uniform(-0.1, 0.1)) for _ in range(weeks_ahead)]
        
        return forecast
    
    @staticmethod
    def calculate_content_performance_score(views, engagement_rate, conversions, benchmark_conversion=2.5):
        """
        Calculate content performance score (0-100)
        
        Args:
            views: Number of views/impressions
            engagement_rate: Engagement rate (%)
            conversions: Number of conversions
            benchmark_conversion: Target conversion rate (%)
            
        Returns:
            float: Performance score (0-100)
        """
        # Reach score (0-30)
        reach_score = min(30, (views / 500) * 30)  # 500+ views = full points
        
        # Engagement score (0-30)
        engagement_score = min(30, (engagement_rate / 5) * 30)  # 5%+ engagement = full points
        
        # Conversion score (0-40)
        if views > 0:
            actual_conversion = (conversions / views) * 100
            conversion_ratio = actual_conversion / benchmark_conversion
            conversion_score = min(40, conversion_ratio * 40)
        else:
            conversion_score = 0
        
        return reach_score + engagement_score + conversion_score
    
    @staticmethod
    def calculate_partner_health_score(total_referrals, last_referral_days, avg_deal_size, target_deal_size=47000):
        """
        Calculate partner health score (0-100)
        
        Args:
            total_referrals: Total referrals all-time
            last_referral_days: Days since last referral
            avg_deal_size: Average deal size from partner
            target_deal_size: Target deal size
            
        Returns:
            float: Health score (0-100)
        """
        # Activity score (0-40)
        if last_referral_days <= 30:
            activity_score = 40
        elif last_referral_days <= 60:
            activity_score = 25
        elif last_referral_days <= 90:
            activity_score = 10
        else:
            activity_score = 0
        
        # Volume score (0-30)
        volume_score = min(30, (total_referrals / 10) * 30)  # 10+ referrals = full points
        
        # Quality score (0-30)
        deal_ratio = avg_deal_size / target_deal_size
        quality_score = min(30, deal_ratio * 30)
        
        return activity_score + volume_score + quality_score
    
    @staticmethod
    def format_currency(value, include_symbol=True):
        """Format value as GBP currency"""
        if pd.isna(value):
            return "£0"
        
        symbol = "£" if include_symbol else ""
        
        if abs(value) >= 1000000:
            return f"{symbol}{value/1000000:.1f}M"
        elif abs(value) >= 1000:
            return f"{symbol}{value/1000:.1f}K"
        else:
            return f"{symbol}{value:.2f}"
    
    @staticmethod
    def format_percentage(value, decimal_places=1):
        """Format value as percentage"""
        if pd.isna(value):
            return "0%"
        return f"{value:.{decimal_places}f}%"
    
    @staticmethod
    def format_number(value):
        """Format number with thousand separators"""
        if pd.isna(value):
            return "0"
        return f"{int(value):,}"

# Singleton instance
_calculator = None

def get_calculator():
    """Get or create MetricsCalculator instance"""
    global _calculator
    if _calculator is None:
        _calculator = MetricsCalculator()
    return _calculator
