# Guavas Dashboard - Data Loader
# Handles Excel file upload, parsing, and validation

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import numpy as np
from config import EXPECTED_TABS, DATE_FORMAT

class DataLoader:
    """Class to handle all data loading and parsing operations"""
    
    def __init__(self):
        self.data = {}
        self.validation_results = {}
    
    def load_excel(self, uploaded_file):
        """
        Load Excel file with 14 tabs
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            dict: Dictionary with tab names as keys and DataFrames as values
        """
        try:
            # Read Excel file
            xl_file = pd.ExcelFile(uploaded_file)
            
            # Load all sheets
            for sheet_name in xl_file.sheet_names:
                self.data[sheet_name] = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            
            # Validate data
            self.validate_data()
            
            # Store in session state
            st.session_state.excel_data = self.data
            st.session_state.data_loaded = True
            st.session_state.last_upload_time = datetime.now()
            
            return self.data
            
        except Exception as e:
            st.error(f"Error loading Excel file: {str(e)}")
            return None
    
    def validate_data(self):
        """Validate loaded data structure and completeness"""
        
        for tab_name in EXPECTED_TABS:
            if tab_name in self.data:
                df = self.data[tab_name]
                self.validation_results[tab_name] = {
                    'exists': True,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'status': 'Valid',
                    'issues': []
                }
                
                # Check for missing data
                if len(df) == 0:
                    self.validation_results[tab_name]['status'] = 'Warning'
                    self.validation_results[tab_name]['issues'].append('No data rows')
                
                # Check for mostly empty rows
                empty_rows = df.isna().all(axis=1).sum()
                if empty_rows > len(df) * 0.5:
                    self.validation_results[tab_name]['status'] = 'Warning'
                    self.validation_results[tab_name]['issues'].append(f'{empty_rows} empty rows')
                    
            else:
                self.validation_results[tab_name] = {
                    'exists': False,
                    'status': 'Missing',
                    'issues': ['Tab not found in Excel file']
                }
        
        return self.validation_results
    
    def get_kpi_data(self):
        """
        Extract KPI metrics from the KPI Dashboard tab
        
        Returns:
            dict: Dictionary of KPI metrics
        """
        if '12_KPI Dashboard' not in self.data:
            return self._get_default_kpis()
        
        df = self.data['12_KPI Dashboard']
        
        # Try to extract metrics (structure may vary)
        kpis = {}
        
        try:
            # Look for standard KPI rows
            # This is flexible - adjust based on actual Excel structure
            for idx, row in df.iterrows():
                metric_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None
                
                if metric_name:
                    # Try to find current month value
                    if 'Current Month' in df.columns:
                        kpis[metric_name] = row['Current Month']
                    elif len(row) > 1 and pd.notna(row.iloc[1]):
                        kpis[metric_name] = row.iloc[1]
            
            # Ensure we have key metrics
            return self._ensure_key_metrics(kpis)
            
        except Exception as e:
            st.warning(f"Could not parse KPI data: {str(e)}. Using defaults.")
            return self._get_default_kpis()
    
    def _ensure_key_metrics(self, kpis):
        """Ensure all key metrics exist, use defaults if missing"""
        defaults = self._get_default_kpis()
        
        for key in defaults:
            if key not in kpis or pd.isna(kpis[key]):
                kpis[key] = defaults[key]
        
        return kpis
    
    def _get_default_kpis(self):
        """Return default KPI values for demo/testing"""
        return {
            'Total Leads': 285,
            'Total Meetings': 67,
            'Total Deals': 12,
            'Pipeline Value': 2800000,
            'Avg CPL': 32.50,
            'Lead to Meeting %': 23.5,
            'Meeting to Deal %': 17.9,
            'Avg Deal Size': 47200
        }
    
    def get_channel_data(self):
        """
        Extract channel performance data from Funnel Master Map and Attribution Tracking
        
        Returns:
            DataFrame: Channel performance data
        """
        channels = []
        
        # Try to get data from Funnel Master Map
        if '1_Funnel Master Map' in self.data:
            df = self.data['1_Funnel Master Map']
            
            try:
                # Skip header rows and get actual data
                # Adjust column indices based on your Excel structure
                for idx, row in df.iterrows():
                    if idx < 2:  # Skip header rows
                        continue
                    
                    channel_name = row.iloc[0] if pd.notna(row.iloc[0]) else None
                    
                    if channel_name and str(channel_name).strip() and not str(channel_name).startswith('FUNNEL'):
                        channel_data = {
                            'Channel': str(channel_name).strip(),
                            'Type': row.iloc[1] if pd.notna(row.iloc[1]) else 'Unknown',
                            'Status': row.iloc[13] if len(row) > 13 and pd.notna(row.iloc[13]) else 'Unknown',
                            'Priority': row.iloc[14] if len(row) > 14 and pd.notna(row.iloc[14]) else 'Medium',
                            'Budget': row.iloc[16] if len(row) > 16 and pd.notna(row.iloc[16]) else 0,
                            'Leads': 0,  # Will be filled from Attribution Tracking
                            'CPL': 0,
                            'Conversion': 0
                        }
                        channels.append(channel_data)
            except Exception as e:
                st.warning(f"Error parsing Funnel Master Map: {str(e)}")
        
        # Try to enhance with Attribution Tracking data
        if '9_Attribution Tracking' in self.data:
            tracking_df = self.data['9_Attribution Tracking']
            
            try:
                for idx, row in tracking_df.iterrows():
                    if idx < 2:  # Skip headers
                        continue
                    
                    channel = row.iloc[0] if pd.notna(row.iloc[0]) else None
                    leads = row.iloc[6] if len(row) > 6 and pd.notna(row.iloc[6]) else 0
                    cpl = row.iloc[8] if len(row) > 8 and pd.notna(row.iloc[8]) else 0
                    
                    if channel:
                        # Find matching channel and update
                        for ch in channels:
                            if ch['Channel'] == channel:
                                ch['Leads'] = leads
                                ch['CPL'] = cpl
                                break
            except Exception as e:
                st.warning(f"Error parsing Attribution Tracking: {str(e)}")
        
        # If no channels found, create demo data
        if not channels:
            channels = self._get_demo_channels()
        
        return pd.DataFrame(channels)
    
    def _get_demo_channels(self):
        """Return demo channel data for testing"""
        return [
            {'Channel': 'LinkedIn Organic', 'Type': 'Inbound', 'Status': 'Active', 'Priority': 'High', 'Budget': 0, 'Leads': 47, 'CPL': 8.20, 'Conversion': 14.9},
            {'Channel': 'Webinar Program', 'Type': 'Inbound', 'Status': 'Active', 'Priority': 'High', 'Budget': 500, 'Leads': 38, 'CPL': 13.16, 'Conversion': 18.4},
            {'Channel': 'Partner Referrals', 'Type': 'Inbound', 'Status': 'Active', 'Priority': 'High', 'Budget': 0, 'Leads': 25, 'CPL': 0, 'Conversion': 68.0},
            {'Channel': 'Email Marketing', 'Type': 'Inbound', 'Status': 'Active', 'Priority': 'Medium', 'Budget': 200, 'Leads': 18, 'CPL': 11.11, 'Conversion': 22.2},
            {'Channel': 'Google Ads', 'Type': 'Paid', 'Status': 'Active', 'Priority': 'Low', 'Budget': 300, 'Leads': 5, 'CPL': 60.00, 'Conversion': 20.0},
            {'Channel': 'SEO Organic', 'Type': 'Inbound', 'Status': 'Active', 'Priority': 'High', 'Budget': 0, 'Leads': 42, 'CPL': 0, 'Conversion': 12.8},
        ]
    
    def get_content_calendar(self):
        """
        Extract content calendar data
        
        Returns:
            DataFrame: Content calendar with status
        """
        if '3_Content Calendar' not in self.data:
            return pd.DataFrame()
        
        df = self.data['3_Content Calendar'].copy()
        
        # Clean up and parse
        try:
            # Skip header rows
            if len(df) > 2:
                df = df.iloc[2:].reset_index(drop=True)
            
            # Rename columns for easier access (adjust based on your structure)
            if len(df.columns) >= 7:
                df.columns = ['Week', 'Week_Starting', 'Asset_Type', 'Topic', 'Status', 'Distribution', 'Repurpose', 'Owner', 'Due_Date', 'Notes'][:len(df.columns)]
            
            # Convert dates
            if 'Due_Date' in df.columns:
                df['Due_Date'] = pd.to_datetime(df['Due_Date'], errors='coerce')
            
            # Filter out empty rows
            df = df[df['Topic'].notna()]
            
            return df
            
        except Exception as e:
            st.warning(f"Error parsing Content Calendar: {str(e)}")
            return pd.DataFrame()
    
    def get_partner_performance(self):
        """
        Extract partner performance data
        
        Returns:
            DataFrame: Partner performance metrics
        """
        if '13_Partner Performance' not in self.data:
            return pd.DataFrame()
        
        df = self.data['13_Partner Performance'].copy()
        
        try:
            # Skip empty rows
            df = df.dropna(how='all')
            
            # Convert dates
            date_cols = ['Onboarded Date', 'Last Referral', 'Next Touchpoint']
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            st.warning(f"Error parsing Partner Performance: {str(e)}")
            return pd.DataFrame()
    
    def get_weekly_trend_data(self, weeks=12):
        """
        Generate weekly trend data for charts
        
        Args:
            weeks: Number of weeks to include
            
        Returns:
            DataFrame: Weekly data with leads by channel
        """
        # This is demo data - in production, calculate from actual historical data
        channels = ['LinkedIn Organic', 'Webinar Program', 'Partner Referrals', 'Email Marketing', 'SEO Organic']
        
        dates = pd.date_range(end=datetime.now(), periods=weeks, freq='W')
        
        data = []
        for date in dates:
            week_data = {'Week': date}
            for channel in channels:
                # Generate realistic-looking random data
                base = {'LinkedIn Organic': 45, 'Webinar Program': 35, 'Partner Referrals': 20, 'Email Marketing': 15, 'SEO Organic': 38}
                week_data[channel] = base.get(channel, 10) + np.random.randint(-10, 10)
            data.append(week_data)
        
        return pd.DataFrame(data)
    
    def get_alerts(self):
        """
        Generate alerts based on thresholds
        
        Returns:
            list: List of alert dictionaries
        """
        alerts = []
        
        # Get channel data
        channels_df = self.get_channel_data()
        
        # Check CPL thresholds
        high_cpl = channels_df[channels_df['CPL'] > st.session_state.thresholds['max_cpl']]
        for _, channel in high_cpl.iterrows():
            if channel['CPL'] > 0:  # Exclude £0 CPL channels
                alerts.append({
                    'type': 'warning',
                    'title': f"{channel['Channel']}: High CPL",
                    'message': f"£{channel['CPL']:.2f} exceeds target £{st.session_state.thresholds['max_cpl']}",
                    'action': 'Review campaign performance'
                })
        
        # Check for overdue content
        content_df = self.get_content_calendar()
        if not content_df.empty and 'Due_Date' in content_df.columns and 'Status' in content_df.columns:
            today = datetime.now()
            overdue = content_df[
                (content_df['Due_Date'] < today) & 
                (content_df['Status'] != 'Completed')
            ]
            
            if len(overdue) > 0:
                alerts.append({
                    'type': 'urgent',
                    'title': f"{len(overdue)} content item(s) overdue",
                    'message': 'Review Content Calendar',
                    'action': 'Complete or reschedule'
                })
        
        # Check for inactive partners
        partners_df = self.get_partner_performance()
        if not partners_df.empty and 'Last Referral' in partners_df.columns:
            today = datetime.now()
            threshold_date = today - timedelta(days=st.session_state.thresholds['partner_inactive_days'])
            
            inactive = partners_df[
                (partners_df['Last Referral'] < threshold_date) |
                (partners_df['Last Referral'].isna())
            ]
            
            for _, partner in inactive.iterrows():
                if pd.notna(partner['Partner Name']):
                    days_inactive = (today - partner['Last Referral']).days if pd.notna(partner['Last Referral']) else 999
                    alerts.append({
                        'type': 'info',
                        'title': f"Partner: {partner['Partner Name']}",
                        'message': f"No referrals in {days_inactive} days",
                        'action': 'Re-engage partner'
                    })
        
        return alerts
    
    def get_validation_summary(self):
        """Return data validation summary"""
        return self.validation_results

# Singleton instance
@st.cache_resource
def get_data_loader():
    """Get or create DataLoader instance"""
    return DataLoader()
