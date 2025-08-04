"""
UI Components for AI Resume Assistant
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any
import pandas as pd


def display_score_gauge(score: float, title: str):
    """Display a gauge chart for scoring metrics."""
    
    # Ensure score is between 0 and 100
    score = max(0, min(100, float(score)))
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0.15, 1]},  # Adjusted domain to better position gauge
        title = {
            'text': title,
            'font': {'size': 18, 'color': '#2E3440'}
        },
        number = {
            'font': {'size': 36, 'color': '#2E3440'},
            'suffix': '',
            'prefix': ''
        },
        gauge = {
            'axis': {
                'range': [None, 100],
                'tickwidth': 2,
                'tickcolor': "#88C999",
                'tickfont': {'size': 12, 'color': '#2E3440'}
            },
            'bar': {'color': "#5E81AC", 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#D8DEE9",
            'steps': [
                {'range': [0, 40], 'color': "#EBCB8B", 'name': 'Poor'},
                {'range': [40, 70], 'color': "#D08770", 'name': 'Fair'},
                {'range': [70, 85], 'color': "#A3BE8C", 'name': 'Good'},
                {'range': [85, 100], 'color': "#8FBCBB", 'name': 'Excellent'}
            ],
            'threshold': {
                'line': {'color': "#BF616A", 'width': 3},
                'thickness': 0.8,
                'value': 90
            }
        }
    ))
    
    # Improved layout with better positioning
    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(size=12, color='#2E3440'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_analysis_summary(analysis: Dict[str, Any]):
    """Display a summary of the analysis results."""
    
    ai_analysis = analysis.get("ai_analysis", {})
    keyword_analysis = analysis.get("keyword_analysis", {})
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        overall_score = ai_analysis.get("overall_match_score", 0)
        st.metric(
            label="Overall Match",
            value=f"{overall_score}/100",
            delta=f"{overall_score - 50:+.0f} vs baseline"
        )
    
    with col2:
        semantic_score = analysis.get("semantic_similarity", 0)
        st.metric(
            label="Semantic Similarity",
            value=f"{semantic_score:.1f}%",
            delta=f"{semantic_score - 60:+.1f}% vs baseline"
        )
    
    with col3:
        keyword_match_rate = keyword_analysis.get("keyword_match_rate", 0)
        st.metric(
            label="Keyword Match",
            value=f"{keyword_match_rate:.1f}%",
            delta=f"{keyword_match_rate - 40:+.1f}% vs baseline"
        )
    
    with col4:
        skills_found = len(ai_analysis.get("skills_found", []))
        skills_missing = len(ai_analysis.get("skills_missing", []))
        total_skills = skills_found + skills_missing
        skills_percentage = (skills_found / total_skills * 100) if total_skills > 0 else 0
        st.metric(
            label="Skills Coverage",
            value=f"{skills_percentage:.0f}%",
            delta=f"{skills_found} of {total_skills} skills"
        )


def display_keyword_analysis(analysis: Dict[str, Any]):
    """Display keyword analysis results."""
    
    keyword_analysis = analysis.get("keyword_analysis", {})
    
    if not keyword_analysis:
        st.warning("No keyword analysis data available.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Found Keywords")
        found_keywords = keyword_analysis.get("found_keywords", [])
        
        if found_keywords:
            for keyword in found_keywords[:10]:  # Show top 10
                st.success(f"✅ {keyword}")
        else:
            st.info("No matching keywords found.")
    
    with col2:
        st.subheader("❌ Missing Keywords")
        missing_keywords = keyword_analysis.get("missing_keywords", [])
        
        if missing_keywords:
            for keyword in missing_keywords[:10]:  # Show top 10
                st.error(f"❌ {keyword}")
        else:
            st.success("All important keywords found!")
    
    # Keyword frequency chart
    if found_keywords:
        st.subheader("📊 Keyword Frequency")
        keyword_freq = keyword_analysis.get("keyword_frequency", {})
        
        if keyword_freq:
            df = pd.DataFrame(list(keyword_freq.items()), columns=['Keyword', 'Frequency'])
            df = df.sort_values('Frequency', ascending=True).tail(10)  # Top 10
            
            fig = px.bar(df, x='Frequency', y='Keyword', orientation='h',
                        title="Most Frequent Keywords in Resume")
            st.plotly_chart(fig, use_container_width=True)


def display_skills_breakdown(analysis: Dict[str, Any]):
    """Display skills analysis breakdown."""
    
    ai_analysis = analysis.get("ai_analysis", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Skills Found")
        skills_found = ai_analysis.get("skills_found", [])
        
        if skills_found:
            for skill in skills_found:
                st.success(f"✅ {skill}")
        else:
            st.info("No matching skills identified.")
    
    with col2:
        st.subheader("❓ Missing Skills")
        skills_missing = ai_analysis.get("skills_missing", [])
        
        if skills_missing:
            for skill in skills_missing:
                st.error(f"❌ {skill}")
        else:
            st.success("All required skills present!")
    
    # Skills categories breakdown
    skills_categories = ai_analysis.get("skills_categories", {})
    if skills_categories:
        st.subheader("📋 Skills by Category")
        
        for category, skills in skills_categories.items():
            with st.expander(f"{category} ({len(skills)} skills)"):
                for skill in skills:
                    st.write(f"• {skill}")


def display_experience_analysis(analysis: Dict[str, Any]):
    """Display experience analysis."""
    
    ai_analysis = analysis.get("ai_analysis", {})
    experience_analysis = analysis.get("experience_analysis", {})
    
    # Experience summary
    years_experience = experience_analysis.get("total_years", 0)
    required_years = experience_analysis.get("required_years", 0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Years of Experience",
            value=f"{years_experience} years",
            delta=f"{years_experience - required_years:+.0f} vs required"
        )
    
    with col2:
        relevance_score = experience_analysis.get("relevance_score", 0)
        st.metric(
            label="Experience Relevance",
            value=f"{relevance_score:.0f}%",
            delta=f"{relevance_score - 70:+.0f}% vs benchmark"
        )
    
    # Experience highlights
    st.subheader("💼 Experience Highlights")
    experience_highlights = ai_analysis.get("experience_highlights", [])
    
    if experience_highlights:
        for highlight in experience_highlights:
            st.info(f"💡 {highlight}")
    else:
        st.warning("No specific experience highlights identified.")
    
    # Career progression
    career_progression = experience_analysis.get("career_progression", [])
    if career_progression:
        st.subheader("📈 Career Progression")
        
        for i, role in enumerate(career_progression):
            with st.expander(f"Role {i+1}: {role.get('title', 'Unknown Title')}"):
                st.write(f"**Company:** {role.get('company', 'Not specified')}")
                st.write(f"**Duration:** {role.get('duration', 'Not specified')}")
                st.write(f"**Key Responsibilities:**")
                for responsibility in role.get('responsibilities', []):
                    st.write(f"• {responsibility}")


def display_recommendations(recommendations: List[str]):
    """Display AI-generated recommendations."""
    
    if not recommendations:
        st.info("No specific recommendations available.")
        return
    
    st.subheader("🎯 AI Recommendations")
    
    for i, recommendation in enumerate(recommendations, 1):
        st.info(f"**{i}.** {recommendation}")


def display_improvement_suggestions(suggestions: Dict[str, Any]):
    """Display improvement suggestions."""
    
    if not suggestions:
        st.info("No improvement suggestions available.")
        return
    
    # Immediate improvements
    immediate_improvements = suggestions.get("immediate_improvements", [])
    if immediate_improvements:
        st.subheader("🚀 Immediate Improvements")
        for improvement in immediate_improvements:
            if isinstance(improvement, dict):
                section = improvement.get("section", "General")
                issue = improvement.get("current_issue", "")
                change = improvement.get("suggested_change", "")
                st.warning(f"**{section}**: {issue} → {change}")
            else:
                st.warning(f"🚀 {improvement}")
    
    # Keyword optimization
    keyword_optimization = suggestions.get("keyword_optimization", [])
    if keyword_optimization:
        st.subheader("🔍 Keyword Optimization")
        for keyword_item in keyword_optimization:
            if isinstance(keyword_item, dict):
                keyword = keyword_item.get("missing_keyword", "")
                suggestion = keyword_item.get("suggestion", "")
                priority = keyword_item.get("priority", "medium")
                priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "🟡")
                st.success(f"{priority_color} **{keyword}**: {suggestion}")
            else:
                st.success(f"🔍 {keyword_item}")
    
    # Formatting improvements
    formatting_suggestions = suggestions.get("formatting_suggestions", [])
    if formatting_suggestions:
        st.subheader("🎨 Formatting Improvements")
        for suggestion in formatting_suggestions:
            st.info(f"🎨 {suggestion}")
    
    # Content enhancements
    content_enhancements = suggestions.get("content_enhancements", [])
    if content_enhancements:
        st.subheader("📝 Content Enhancements")
        for enhancement in content_enhancements:
            st.warning(f"📝 {enhancement}")


def display_file_info(file_info: Dict[str, Any]):
    """Display file information."""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        page_count = file_info.get("page_count", 0)
        st.metric(label="Pages", value=page_count)
    
    with col2:
        file_size = file_info.get("file_size", 0)
        file_size_mb = file_size / (1024 * 1024)
        st.metric(label="File Size", value=f"{file_size_mb:.2f} MB")
    
    with col3:
        method_used = file_info.get("method_used", "Unknown")
        st.metric(label="Extraction Method", value=method_used)


def display_error_message(error_message: str, title: str = "Error"):
    """Display an error message with styling."""
    
    st.error(f"**{title}**")
    st.error(error_message)
    
    # Add some troubleshooting tips
    with st.expander("💡 Troubleshooting Tips"):
        st.markdown("""
        **Common solutions:**
        - Check your internet connection
        - Verify your OpenRouter API key is valid
        - Ensure the PDF file is not corrupted
        - Try reducing the job description length
        - Restart the application if issues persist
        """)


def display_success_message(message: str):
    """Display a success message with styling."""
    
    st.success(message)


def show_loading_spinner(text: str = "Processing..."):
    """Show a loading spinner with custom text."""
    
    with st.spinner(text):
        # This function is used with context manager
        # The actual loading happens in the calling code
        pass