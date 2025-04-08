import streamlit as st
from typing import Dict, List
from ..utils import get_client, display_ship_selector
from services.api_client import SailingIdentifier
import pandas as pd
import plotly.express as px

def show():
    st.title("🚢 Cruise Analytics Dashboard")
    
    # Initialize API client
    client = get_client()
    
    with st.container():
        st.markdown("### Overview of Cruise Performance Metrics")
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            date_from = st.date_input("From Date")
        with col2:
            date_to = st.date_input("To Date")
        
        # Ship selection
        selected_ships = display_ship_selector(multi=True)
        
        if not selected_ships:
            st.warning("Please select at least one ship")
            return
            
        if st.button("Load Dashboard Data"):
            with st.spinner("Loading dashboard data..."):
                try:
                    # Convert to SailingIdentifiers (assuming sailing number 1 for dashboard)
                    sailings = [SailingIdentifier(ship, "1") for ship in selected_ships]
                    
                    # Get rating summaries for selected ships
                    summaries = client.get_rating_summary(
                        sailings=sailings,
                        from_date=date_from.isoformat(),
                        to_date=date_to.isoformat()
                    )
                    print(summaries)
                    # Display the dashboard components
                    display_overview_metrics(summaries)
                    display_metric_trends(summaries)
                    display_ship_comparison(summaries)
                    
                except Exception as e:
                    st.error(f"Failed to load dashboard data: {str(e)}")

def display_overview_metrics(summaries: List[Dict]):
    """Display key metrics in columns"""
    st.markdown("### Key Metrics")
    
    if not summaries:
        st.warning("No data available for the selected criteria")
        return
    
    # Calculate averages across all selected sailings
    metrics = [
        ('F&B Quality Overall', 'F&B Quality Overall'),
        ('Cabin Cleanliness', 'cabinCleanlinessScore'),
        ('Crew Friendliness', 'crewFriendlinessScore'),
        ('Entertainment', 'entertainmentScore')
    ]
    
    cols = st.columns(len(metrics))
    for idx, (display_name, api_name) in enumerate(metrics):
        with cols[idx]:
            values = [s.get(display_name.lower(), 0) for s in summaries if display_name.lower() in {k.lower() for k in s}]
            avg = sum(values) / len(values) if values else 0
            delta = avg - 8.0  # Compare to benchmark of 8.0
            st.metric(
                label=display_name,
                value=f"{avg:.1f}",
                delta=f"{delta:+.1f} vs benchmark"
            )

def display_metric_trends(summaries: List[Dict]):
    """Display metric trends over time"""
    st.markdown("### Metric Trends Over Time")
    
    if not summaries:
        return
    
    # Prepare data for plotting
    metrics = [
        ('F&B Quality', 'fbQualityOverall'),
        ('Cabin Cleanliness', 'cabinCleanlinessScore'),
        ('Entertainment', 'entertainmentScore')
    ]
    
    plot_data = []
    for summary in summaries:
        for display_name, api_name in metrics:
            if display_name in summary:
                plot_data.append({
                    'Date': summary.get('sailingDate', 'N/A'),
                    'Ship': summary.get('Ship Name', 'Unknown'),
                    'Metric': display_name,
                    'Score': summary[display_name]
                })
    
    if not plot_data:
        st.warning("No trend data available")
        return
    
    df = pd.DataFrame(plot_data)
    
    # Create interactive plot
    fig = px.line(
        df,
        x='Date',
        y='Score',
        color='Ship',
        line_dash='Metric',
        title='Metric Trends by Ship',
        markers=True
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def display_ship_comparison(summaries: List[Dict]):
    """Display comparison of ships across key metrics"""
    st.markdown("### Ship Comparison")
    
    if not summaries:
        return
    
    # Select metrics to compare
    comparison_metrics = st.multiselect(
        "Select metrics to compare",
        options=[
            'F&B Quality Overall',
            'Cabin Cleanliness',
            'Crew Friendliness',
            'Entertainment',
            'Excursions'
        ],
        default=['F&B Quality Overall',
            'Cabin Cleanliness',
            'Crew Friendliness',
            'Entertainment',
            'Excursions']
    )
    
    if not comparison_metrics:
        return
    
    # Prepare data for radar chart
    radar_data = []
    metric_mapping = {
        'F&B Quality Overall': 'F&B Quality Overall',
        'Cabin Cleanliness': 'Cabin Cleanliness',
        'Crew Friendliness': 'Crew Friendliness',
        'Entertainment': 'Entertainment',
        'Excursions': 'Excursions'
    }
    
    ships = set()
    for summary in summaries:
        ship = summary.get('Ship Name', 'Unknown')
        ships.add(ship)
        for metric in comparison_metrics:
            api_name = metric_mapping.get(metric, metric)
            if api_name in summary:
                radar_data.append({
                    'Ship': ship,
                    'Metric': metric,
                    'Score': summary[api_name]
                })
    
    if len(ships) < 2:
        st.warning("Need at least 2 ships for comparison")
        return
    
    # Create radar chart
    print(radar_data)
    df = pd.DataFrame(radar_data)
    fig = px.line_polar(
        df,
        r='Score',
        theta='Metric',
        color='Ship',
        line_close=True,
        template='plotly_dark',
        title='Ship Comparison Radar Chart'
    )
    fig.update_traces(fill='toself')
    st.plotly_chart(fig, use_container_width=True)
