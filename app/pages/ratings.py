import streamlit as st
from ..utils import get_client, display_ship_selector
from typing import List, Dict
from services.api_client import SailingIdentifier
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import linregress



def add_trendline(ax, x_values, y_values, color="red"):
    """Add a trendline to the plot"""
    if len(x_values) > 1:
        x_numeric = np.arange(len(x_values))
        slope, intercept, _, _, _ = linregress(x_numeric, y_values)
        ax.plot(x_numeric, intercept + slope * x_numeric, 
                color=color, linestyle="--", linewidth=2,
                label=f"Trend (slope: {slope:.2f})")
        ax.legend(loc='upper right')

def show():
    st.title("📊 Ratings Summary")
    client = get_client()
    
    with st.container():
        selected_ships = display_ship_selector(multi=True)
        
        if not selected_ships:
            return
            
        if st.button("Generate Report"):
            # with st.spinner("Loading data..."):
            try:
                sailings = [SailingIdentifier(ship, "1") for ship in selected_ships]
                data = client.get_rating_summary(sailings)
                display_ratings(client,data)
            except Exception as e:
                st.error(f"Failed to load ratings: {str(e)}")

def display_ratings(client, data: List[Dict]):
    # Implementation of ratings visualization
    app_config = client.config["app"]

    def get_color_palette(n):
        """Return n distinct colors from config palette"""
        return app_config["color_palette"][:n]
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)
    
    # Display raw data toggle
    # if st.checkbox("Show raw data"):
    #     st.dataframe(df)
    st.dataframe(df, hide_index=True)
    
    # Get all metric columns (exclude ship identifiers)
    metric_columns = [col for col in df.columns if col not in ["Sailing Number", "Ship Name"]]
    
    # Group metrics by category
    metric_categories = app_config["metric_categories"]
    
    # Create tabs for each metric category
    tabs = st.tabs(list(metric_categories.keys()))
    
    for i, (category_name, metrics) in enumerate(metric_categories.items()):
        with tabs[i]:
            st.subheader(f"{category_name} Metrics")
            
            # Display metrics in pairs (2 per row)
            for j in range(0, len(metrics), 2):
                metric_pair = metrics[j:j+2]
                cols = st.columns(2)
                
                for k, metric in enumerate(metric_pair):
                    if metric in df.columns:
                        with cols[k]:
                            # Create figure
                            fig, ax = plt.subplots(figsize=(6, 4))
                            
                            # Get colors for bars
                            colors = get_color_palette(len(df))
                            
                            # Create bar plot
                            x_values = df["Ship Name"]
                            y_values = df[metric]
                            bars = ax.bar(
                                x_values,
                                y_values,
                                color=colors
                            )
                            
                            # Add trendline
                            add_trendline(ax, x_values, y_values)
                            
                            # Customize plot
                            ax.set_title(metric, pad=10)
                            ax.set_ylim(0, 10)
                            ax.set_ylabel("Rating")
                            ax.tick_params(axis='x', rotation=45)
                            
                            # Add value labels on bars
                            for bar in bars:
                                height = bar.get_height()
                                ax.text(
                                    bar.get_x() + bar.get_width()/2.,
                                    height,
                                    f'{height:.2f}',
                                    ha='center',
                                    va='bottom'
                                )
                            
                            # Display plot
                            st.pyplot(fig)
                            
                            # Display metrics below chart
                            st.markdown(f"""
                            <div style="text-align: center">
                                <strong>Stats:</strong><br>
                                Highest: {df[metric].max():.2f} | 
                                Lowest: {df[metric].min():.2f} | 
                                Avg: {df[metric].mean():.2f}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("<div style='margin-bottom:30px'></div>", unsafe_allow_html=True)
    
    # Display comparison summary
    st.subheader("Comparison Summary")
    
    # Calculate overall averages
    summary_df = df[metric_columns].mean().to_frame(name="Average Rating").reset_index()
    summary_df.columns = ["Metric", "Average Rating"]
    
    # Display as a table with color coding
    st.dataframe(
        summary_df.style.background_gradient(
            cmap="YlGnBu",
            subset=["Average Rating"],
            vmin=0,
            vmax=10
        ),
        use_container_width=True,
        height=(len(summary_df) + 1) * 35 + 3
    )