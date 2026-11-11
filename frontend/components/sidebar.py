import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🕳️ **Pothole Detection**")
        st.caption("Deep learning road-safety intelligence")
        st.divider()
        
        page = st.radio(
            "Navigation",
            ["New Report", "Dashboard", "Reports", "Map View", "Work Orders", "Analytics", "Settings"],
            index=0
        )
        st.divider()
        st.success("🟢 System Status: Operational")
        return page