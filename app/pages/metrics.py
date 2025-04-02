import streamlit as st
from ..utils import get_client, display_ship_selector, display_metric_selector
from services.api_client import SailingIdentifier
from typing import Dict
import plotly.express as px
import pandas as pd


def show():
    st.title("📈 Metric Comparison")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            metric = display_metric_selector()
            
        with col2:
            threshold = st.slider(
                "Rating Threshold",
                min_value=0.0,
                max_value=10.0,
                value=5.0,
                step=0.5
            )
        
        selected_ships = display_ship_selector(multi=True)
        
        if not metric or not selected_ships:
            return
            
        if st.button("Compare Metrics"):
            with st.spinner("Analyzing..."):
                try:
                    client = get_client()
                    sailings = [SailingIdentifier(ship, "1") for ship in selected_ships]
                    results = client.get_metric_rating(
                        sailings=sailings,
                        metric=metric,
                        filter_below=threshold,
                        compare_to_average=False
                    )
                    display_comparison(results, metric, threshold)
                except Exception as e:
                    st.error(f"Comparison failed: {str(e)}")

        

def display_comparison(results: Dict, metric: str, threshold: float):
    """Display metric comparison results in a tabular format with actionable reviews"""
    st.subheader(f"Comparison Results for: {metric}")
    st.caption(f"Showing ratings below threshold: {threshold}")
    
    # Convert results to DataFrame
    df = pd.DataFrame([{
        'Ship': r['ship'],
        'Sailing Number': r['sailingNumber'],
        'Rating': r['filteredMetric'],
        'Rating Count': int(r['ratingCount']),
        'Below Threshold': int(r['filteredCount']),
        'Reviews': r['filteredReviews']
    } for r in results['results']])
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ships Compared", len(df))
    with col2:
        st.metric("Total Reviews Analyzed", df['Rating Count'].sum())
    with col3:
        st.metric("Total Below Threshold", df['Below Threshold'].sum())
    
    # Main comparison table
    st.write("### Review Analysis")
    
    if df['Below Threshold'].sum() == 0:
        st.success(f"No reviews found below {threshold} rating threshold")
        return
    
    # Initialize session state for flagged/resolved reviews if not exists
    if 'flagged_reviews' not in st.session_state:
        st.session_state.flagged_reviews = {}
    if 'resolved_reviews' not in st.session_state:
        st.session_state.resolved_reviews = {}
    
    # Create expanded table view
    review_data = []
    for _, row in df.iterrows():
        for i, review in enumerate(row['Reviews'], 1):
            # print(i)
            review_id = f"{row['Ship']}_{row['Sailing Number']}_{i}"
            review_data.append({
                'Ship': row['Ship'],
                'Sailing Number': row['Sailing Number'],
                'Rating': row['Rating'][i-1],
                'Review Excerpt': (review[:50] + '...') if len(review) > 50 else review,
                'Full Review': review,
                'ID': review_id,
                'Flagged': st.session_state.flagged_reviews.get(review_id, False),
                'Resolved': st.session_state.resolved_reviews.get(review_id, False)
            })
    
    reviews_df = pd.DataFrame(review_data)
    reviews_df = reviews_df.sort_values(by="Rating", ascending=True)
        
    # Store the sorted DataFrame in session state
    st.session_state.reviews_df = reviews_df

# Display table manually with expanders inline
    # Create a header row
    header_cols = st.columns([2, 2, 1, 2])  # Adjust column widths as needed
    with header_cols[0]:
        st.markdown("**Ship**")
    with header_cols[1]:
        st.markdown("**Sailing Number**")
    with header_cols[2]:
        st.markdown("**Rating**")
    with header_cols[3]:
        st.markdown("**Review Excerpt**")
    
    # Display each row with an expander for the full review
    for idx, row in reviews_df.iterrows():
        with st.container():
            cols = st.columns([2, 2, 1, 4])  # Same column widths as header
            with cols[0]:
                st.write(row['Ship'])
            with cols[1]:
                st.write(row['Sailing Number'])
            with cols[2]:
                st.write(f"{row['Rating']:.2f}")
            with cols[3]:
                with st.expander(row['Review Excerpt']):
                    st.text_area(
                        "Full Review",
                        value=row['Full Review'],
                        height=200,
                        disabled=True,
                        label_visibility="collapsed",
                        key=f"full_review_{row['ID']}"  # Unique key for each text area
                    )

    
    # Add download button
    st.download_button(
        label="📥 Download Review Data",
        data=reviews_df.drop(columns=['Full Review']).to_csv(index=False).encode('utf-8'),
        file_name=f"{metric}_reviews_below_{threshold}.csv",
        mime="text/csv"
    )

# Temporary action functions
def flag_review(review_id: str):
    """Flag a review for follow-up"""
    st.session_state.flagged_reviews.add(review_id)
    st.toast(f"Review flagged for follow-up")

def resolve_review(review_id: str):
    """Mark a review as resolved"""
    st.session_state.resolved_reviews.add(review_id)
    st.toast(f"Review marked as resolved")