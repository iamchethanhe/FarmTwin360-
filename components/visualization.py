import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from database import get_db
from models import Barn
from utils import get_risk_color

def render_3d_farm():
    """Render 3D farm visualization"""
    db = get_db()
    try:
        barns = db.query(Barn).all()
        
        if not barns:
            st.warning("No barns available for visualization")
            return
        
        # Create 3D scatter plot
        fig = go.Figure()
        
        for barn in barns:
            risk_color = get_risk_color(barn.risk_level or "low")
            
            fig.add_trace(go.Scatter3d(
                x=[barn.position_x],
                y=[barn.position_y], 
                z=[barn.position_z],
                mode='markers+text',
                marker=dict(
                    size=20,
                    color=risk_color,
                    opacity=0.8,
                    line=dict(width=2, color='black')
                ),
                text=[barn.name],
                textposition="top center",
                name=f"{barn.name} ({barn.risk_level.title() if barn.risk_level else 'Unknown'})",
                hovertemplate=f"""
                <b>{barn.name}</b><br>
                Risk Level: {barn.risk_level.title() if barn.risk_level else 'Unknown'}<br>
                Capacity: {barn.capacity}<br>
                Position: ({barn.position_x}, {barn.position_y}, {barn.position_z})<br>
                <extra></extra>
                """
            ))
        
        # Add ground plane
        ground_size = 100
        xx, yy = np.meshgrid(
            np.linspace(-10, ground_size, 10),
            np.linspace(-10, ground_size, 10)
        )
        zz = np.zeros_like(xx) - 5
        
        fig.add_trace(go.Surface(
            x=xx, y=yy, z=zz,
            colorscale='Greens',
            opacity=0.3,
            showscale=False,
            name="Ground"
        ))
        
        # Layout configuration
        fig.update_layout(
            title="FarmTwin 360 - Digital Farm Visualization",
            scene=dict(
                xaxis_title="X Position (meters)",
                yaxis_title="Y Position (meters)",
                zaxis_title="Z Position (meters)",
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
                aspectmode='cube'
            ),
            height=600,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Legend
        st.markdown("""
        **Legend:**
        - 🟢 **Green**: Low Risk
        - 🟡 **Yellow**: Medium Risk  
        - 🔴 **Red**: High Risk
        """)
        
        # Farm statistics
        col1, col2, col3 = st.columns(3)
        
        risk_counts = {"high": 0, "medium": 0, "low": 0}
        total_capacity = 0
        
        for barn in barns:
            risk_level = barn.risk_level or "low"
            risk_counts[risk_level] += 1
            total_capacity += barn.capacity or 0
        
        with col1:
            st.metric("Total Barns", len(barns))
        
        with col2:
            st.metric("Total Capacity", total_capacity)
        
        with col3:
            high_risk_pct = (risk_counts["high"] / len(barns) * 100) if barns else 0
            st.metric("High Risk %", f"{high_risk_pct:.1f}%")
    
    finally:
        db.close()

def render_2d_farm_map():
    """Render 2D farm map view"""
    db = get_db()
    try:
        barns = db.query(Barn).all()
        
        if not barns:
            st.warning("No barns available for visualization")
            return
        
        # Create 2D scatter plot
        fig = go.Figure()
        
        for barn in barns:
            risk_color = get_risk_color(barn.risk_level or "low")
            
            fig.add_trace(go.Scatter(
                x=[barn.position_x],
                y=[barn.position_y],
                mode='markers+text',
                marker=dict(
                    size=30,
                    color=risk_color,
                    opacity=0.8,
                    line=dict(width=2, color='black')
                ),
                text=[barn.name],
                textposition="middle center",
                name=f"{barn.name}",
                hovertemplate=f"""
                <b>{barn.name}</b><br>
                Risk Level: {barn.risk_level.title() if barn.risk_level else 'Unknown'}<br>
                Capacity: {barn.capacity}<br>
                <extra></extra>
                """
            ))
        
        fig.update_layout(
            title="Farm Layout - Top View",
            xaxis_title="X Position (meters)",
            yaxis_title="Y Position (meters)",
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    finally:
        db.close()

def render_risk_heatmap():
    """Render risk level heatmap"""
    db = get_db()
    try:
        barns = db.query(Barn).all()
        
        if not barns:
            st.warning("No barn data available")
            return
        
        # Create heatmap data
        positions = []
        risk_levels = []
        barn_names = []
        
        for barn in barns:
            positions.append([barn.position_x, barn.position_y])
            risk_numeric = {"high": 3, "medium": 2, "low": 1}.get(barn.risk_level, 1)
            risk_levels.append(risk_numeric)
            barn_names.append(barn.name)
        
        if positions:
            fig = go.Figure(data=go.Scatter(
                x=[pos[0] for pos in positions],
                y=[pos[1] for pos in positions],
                mode='markers',
                marker=dict(
                    size=40,
                    color=risk_levels,
                    colorscale='RdYlGn_r',  # Red-Yellow-Green reversed
                    colorbar=dict(
                        title="Risk Level",
                        tickmode="array",
                        tickvals=[1, 2, 3],
                        ticktext=["Low", "Medium", "High"]
                    ),
                    cmin=1,
                    cmax=3
                ),
                text=barn_names,
                textposition="middle center",
                hovertemplate="<b>%{text}</b><br>Risk: %{marker.color}<extra></extra>"
            ))
            
            fig.update_layout(
                title="Risk Level Heatmap",
                xaxis_title="X Position",
                yaxis_title="Y Position",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    finally:
        db.close()

def render_facility_overview():
    """Render facility overview with different building types"""
    st.subheader("Facility Overview")
    
    # Sample facility data (could be extended with more building types)
    facilities = [
        {"name": "Main Office", "type": "office", "x": 10, "y": 10, "status": "operational"},
        {"name": "Feed Storage", "type": "storage", "x": 30, "y": 20, "status": "operational"},
        {"name": "Equipment Shed", "type": "equipment", "x": 50, "y": 15, "status": "maintenance"},
        {"name": "Veterinary Clinic", "type": "medical", "x": 70, "y": 25, "status": "operational"},
    ]
    
    # Add barn data
    db = get_db()
    try:
        barns = db.query(Barn).all()
        for barn in barns:
            facilities.append({
                "name": barn.name,
                "type": "barn",
                "x": barn.position_x,
                "y": barn.position_y,
                "status": barn.risk_level or "low"
            })
    finally:
        db.close()
    
    # Create visualization
    fig = go.Figure()
    
    # Define colors and symbols for different facility types
    type_config = {
        "barn": {"color": "blue", "symbol": "square", "size": 20},
        "office": {"color": "gray", "symbol": "diamond", "size": 15},
        "storage": {"color": "brown", "symbol": "triangle-up", "size": 15},
        "equipment": {"color": "orange", "symbol": "cross", "size": 15},
        "medical": {"color": "red", "symbol": "star", "size": 15}
    }
    
    for facility_type in type_config:
        facilities_of_type = [f for f in facilities if f["type"] == facility_type]
        
        if facilities_of_type:
            config = type_config[facility_type]
            
            fig.add_trace(go.Scatter(
                x=[f["x"] for f in facilities_of_type],
                y=[f["y"] for f in facilities_of_type],
                mode='markers+text',
                marker=dict(
                    size=config["size"],
                    color=config["color"],
                    symbol=config["symbol"],
                    opacity=0.8,
                    line=dict(width=1, color='black')
                ),
                text=[f["name"] for f in facilities_of_type],
                textposition="top center",
                name=facility_type.title(),
                hovertemplate="<b>%{text}</b><br>Type: " + facility_type + "<extra></extra>"
            ))
    
    fig.update_layout(
        title="Complete Facility Layout",
        xaxis_title="X Position (meters)",
        yaxis_title="Y Position (meters)",
        height=600,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
