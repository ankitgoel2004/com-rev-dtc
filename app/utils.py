from services.api_client import APIClient, SailingIdentifier
from typing import List, Optional
import streamlit as st

def get_client() -> APIClient:
    if 'api_client' not in st.session_state:
        st.session_state.api_client = APIClient()
    return st.session_state.api_client

def display_ship_selector(multi: bool = False) -> Optional[List[str]]:
    client = get_client()
    try:
        ships = client.get_available_ships()
        if not ships:
            st.warning("No ships available for selection")
            return None
        label = "Select Ships" if multi else "Select Ship"
        return st.multiselect(
            label,
            options=ships,
            default=ships[:2] if multi else [ships[0]] if ships else [],
            key=f"ship_selector_{'multi' if multi else 'single'}"
        )
    except Exception as e:
        st.error(f"Failed to load ships: {str(e)}")
        return None

def display_metric_selector() -> Optional[str]:
    client = get_client()
    try:
        metrics = client.get_valid_metrics()
        return st.selectbox(
            "Select Metric",
            options=metrics,
            index=metrics.index("F&B quality overall") if "F&B quality overall" in metrics else 0
        )
    except Exception as e:
        st.error(f"Failed to load metrics: {str(e)}")
        return None