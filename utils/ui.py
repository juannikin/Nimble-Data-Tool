import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List

def setup_page():
    """Configure page settings and load custom CSS"""
    st.set_page_config(
        page_title="Nimble - LinkedIn Data Pipeline",
        page_icon="📊",
        layout="wide"
    )
    
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def create_metrics_chart(metrics: Dict) -> go.Figure:
    """Create engagement metrics visualization"""
    fig = go.Figure()
    
    # Add bars for main metrics
    fig.add_trace(go.Bar(
        x=['Likes', 'Comments', 'Shares'],
        y=[metrics.get('likes', 0), metrics.get('comments', 0), metrics.get('shares', 0)],
        marker_color='#45B6EC'
    ))
    
    fig.update_layout(
        title="Engagement Metrics",
        plot_bgcolor='white',
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_reactions_chart(reactions: Dict) -> go.Figure:
    """Create reactions breakdown visualization"""
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=list(reactions.keys()),
        values=list(reactions.values()),
        marker_colors=['#45B6EC', '#E30768', '#2D2D2D', '#EFEFEF']
    ))
    
    fig.update_layout(
        title="Reactions Breakdown",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def display_profile_card(author: Dict):
    """Display author profile information"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.image(author.get("image_url", ""), width=100)
    
    with col2:
        st.markdown(f"### {author.get('title', 'N/A')}")
        st.markdown(f"*{author.get('occupation', 'N/A')}*")
        st.markdown(f"[View Profile]({author.get('url', '#')})")
