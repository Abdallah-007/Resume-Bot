"""
AI Resume Assistant - Main Streamlit Application
"""

import streamlit as st
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.pdf_parser import PDFParser
from services.resume_analyzer import ResumeAnalyzer
from components.ui_components import (
    display_score_gauge, display_keyword_analysis, display_skills_breakdown,
    display_recommendations, display_improvement_suggestions, display_experience_analysis,
    display_analysis_summary, show_loading_spinner, display_file_info,
    display_error_message, display_success_message
)
from utils.config import Config, UI_CONFIG, ANALYSIS_CONFIG


def initialize_app():
    """Initialize the Streamlit app with configuration."""
    
    # Page configuration
    st.set_page_config(**UI_CONFIG["page_config"])
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    
    .analysis-section {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .success-text {
        color: #2ca02c;
        font-weight: bold;
    }
    
    .warning-text {
        color: #ff7f0e;
        font-weight: bold;
    }
    
    .error-text {
        color: #d62728;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown(f"""
    <div class="main-header">
        <h1>🤖 {Config.APP_TITLE}</h1>
        <p>{Config.APP_DESCRIPTION}</p>
    </div>
    """, unsafe_allow_html=True)


def validate_inputs(uploaded_file, job_description: str) -> tuple:
    """Validate user inputs and return validation status."""
    
    errors = []
    
    # Check file upload
    if not uploaded_file:
        errors.append("Please upload a resume PDF file.")
    else:
        # Check file type
        if not uploaded_file.name.lower().endswith('.pdf'):
            errors.append("Please upload a PDF file only.")
        
        # Check file size
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > Config.MAX_FILE_SIZE_MB:
            errors.append(f"File size ({file_size_mb:.1f} MB) exceeds maximum allowed size ({Config.MAX_FILE_SIZE_MB} MB).")
    
    # Check job description
    if not job_description or len(job_description.strip()) < 50:
        errors.append("Please provide a detailed job description (at least 50 characters).")
    
    return len(errors) == 0, errors


def process_resume_analysis(uploaded_file, job_description: str) -> dict:
    """Process the resume analysis workflow."""
    
    try:
        # Validate configuration
        config_validation = Config.validate_config()
        if not config_validation["valid"]:
            return {
                "success": False,
                "error": f"Configuration error: {'; '.join(config_validation['issues'])}"
            }
        
        # Initialize services
        pdf_parser = PDFParser()
        
        # Step 1: Validate PDF
        with st.status("Validating PDF file...", expanded=True) as status:
            validation = pdf_parser.validate_pdf(uploaded_file)
            
            if not validation["is_valid"]:
                return {
                    "success": False,
                    "error": f"PDF validation failed: {validation.get('error', 'Unknown error')}"
                }
            
            st.write(f"✅ PDF validated - {validation['page_count']} pages, {validation['file_size']/1024/1024:.1f} MB")
            status.update(label="PDF validation complete!", state="complete", expanded=False)
        
        # Step 2: Extract text
        with st.status("Extracting text from PDF...", expanded=True) as status:
            extraction_result = pdf_parser.extract_text(uploaded_file, method="auto")
            
            if not extraction_result["success"]:
                return {
                    "success": False,
                    "error": f"Text extraction failed: {extraction_result.get('error', 'Unknown error')}"
                }
            
            resume_text = extraction_result["text"]
            st.write(f"✅ Text extracted using {extraction_result['method_used']}")
            st.write(f"📝 Extracted {len(resume_text)} characters")
            status.update(label="Text extraction complete!", state="complete", expanded=False)
        
        # Step 3: Analyze resume
        with st.status("Analyzing resume with AI...", expanded=True) as status:
            try:
                api_key = Config.get_openrouter_api_key()
                analyzer = ResumeAnalyzer(api_key)
                
                st.write("🤖 Initializing AI analyzer...")
                analysis_result = analyzer.analyze_resume(resume_text, job_description)
                
                if "error" in analysis_result:
                    return {
                        "success": False,
                        "error": f"Analysis failed: {analysis_result['error']}"
                    }
                
                st.write("✅ Resume analysis complete")
                status.update(label="AI analysis complete!", state="complete", expanded=False)
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"AI analysis error: {str(e)}"
                }
        
        # Step 4: Generate improvement suggestions
        with st.status("Generating improvement suggestions...", expanded=True) as status:
            try:
                suggestions = analyzer.get_improvement_suggestions(
                    resume_text, job_description, analysis_result
                )
                
                st.write("✅ Improvement suggestions generated")
                status.update(label="Suggestions complete!", state="complete", expanded=False)
                
            except Exception as e:
                st.warning(f"Could not generate suggestions: {str(e)}")
                suggestions = {}
        
        return {
            "success": True,
            "resume_text": resume_text,
            "analysis": analysis_result,
            "suggestions": suggestions,
            "file_info": {
                "page_count": validation["page_count"],
                "file_size": validation["file_size"],
                "method_used": extraction_result["method_used"]
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Processing error: {str(e)}"
        }


def display_results(results: dict):
    """Display analysis results in organized sections."""
    
    analysis = results["analysis"]
    suggestions = results["suggestions"]
    file_info = results["file_info"]
    
    # File information
    st.subheader("📁 Document Information")
    display_file_info(file_info)
    
    st.divider()
    
    # Main analysis summary
    st.subheader("📊 Analysis Summary")
    display_analysis_summary(analysis)
    
    st.divider()
    
    # Score gauge
    ai_analysis = analysis.get("ai_analysis", {})
    overall_score = ai_analysis.get("overall_match_score", 0)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        display_score_gauge(overall_score, "Overall Match Score")
    
    with col2:
        semantic_score = analysis.get("semantic_similarity", 0)
        display_score_gauge(semantic_score, "Semantic Similarity")
    
    st.divider()
    
    # Detailed analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔑 Keywords", "💼 Skills", "📈 Experience", "💡 Recommendations", "🚀 Improvements"
    ])
    
    with tab1:
        display_keyword_analysis(analysis)
    
    with tab2:
        display_skills_breakdown(analysis)
    
    with tab3:
        display_experience_analysis(analysis)
    
    with tab4:
        recommendations = ai_analysis.get("recommendations", [])
        display_recommendations(recommendations)
    
    with tab5:
        display_improvement_suggestions(suggestions)
    
    # Download section
    st.divider()
    st.subheader("💾 Download Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Prepare analysis summary for download
        summary_text = f"""
AI Resume Assistant - Analysis Report
=====================================

Overall Match Score: {overall_score}/100
Semantic Similarity: {semantic_score}%
Keyword Match Rate: {analysis.get('keyword_analysis', {}).get('keyword_match_rate', 0)}%

STRENGTHS:
{chr(10).join([f"• {s}" for s in ai_analysis.get('strengths', [])])}

AREAS FOR IMPROVEMENT:
{chr(10).join([f"• {w}" for w in ai_analysis.get('weaknesses', [])])}

MISSING KEYWORDS:
{chr(10).join([f"• {k}" for k in analysis.get('keyword_analysis', {}).get('missing_keywords', [])])}

RECOMMENDATIONS:
{chr(10).join([f"{i+1}. {r}" for i, r in enumerate(ai_analysis.get('recommendations', []))])}
        """
        
        st.download_button(
            label="📄 Download Summary Report",
            data=summary_text,
            file_name="resume_analysis_summary.txt",
            mime="text/plain"
        )
    
    with col2:
        # Raw analysis data as JSON
        import json
        
        analysis_json = json.dumps({
            "analysis": analysis,
            "suggestions": suggestions,
            "file_info": file_info
        }, indent=2)
        
        st.download_button(
            label="📋 Download Full Analysis (JSON)",
            data=analysis_json,
            file_name="resume_analysis_full.json",
            mime="application/json"
        )


def main():
    """Main application function."""
    
    # Initialize app
    initialize_app()
    
    # Sidebar for input
    with st.sidebar:
        st.header("📤 Upload & Configure")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose your resume (PDF)",
            type=['pdf'],
            help=f"Maximum file size: {Config.MAX_FILE_SIZE_MB} MB"
        )
        
        # Job description input
        job_description = st.text_area(
            "Job Description",
            placeholder="Paste the complete job description here...",
            height=300,
            help="Include requirements, qualifications, and responsibilities"
        )
        
        # Analysis options
        st.subheader("⚙️ Analysis Options")
        
        analysis_depth = st.selectbox(
            "Analysis Depth",
            ["Standard", "Detailed"],
            help="Detailed analysis provides more comprehensive feedback"
        )
        
        include_formatting = st.checkbox(
            "Include Formatting Suggestions",
            value=True,
            help="Analyze document formatting and structure"
        )
        
        # Process button
        process_button = st.button(
            "🚀 Analyze Resume",
            type="primary",
            use_container_width=True
        )
    
    # Main content area
    if not process_button:
        # Welcome message
        st.info("""
        👋 **Welcome to AI Resume Assistant!**
        
        **How it works:**
        1. Upload your resume (PDF format)
        2. Paste the target job description
        3. Click "Analyze Resume" to get insights
        
        **You'll receive:**
        - Match score analysis
        - Missing keywords identification
        - Skills gap analysis
        - Improvement recommendations
        - Actionable suggestions
        """)
        
        # Sample job description for demo
        if st.button("📝 Load Sample Job Description"):
            sample_job = """
Software Engineer - Full Stack Development

We are seeking a talented Full Stack Developer to join our innovative team. 

Requirements:
• Bachelor's degree in Computer Science or related field
• 3+ years of experience in web development
• Strong proficiency in JavaScript, Python, and React
• Experience with Node.js, Express, and MongoDB
• Knowledge of RESTful APIs and microservices architecture
• Familiarity with cloud platforms (AWS, Azure)
• Experience with version control (Git)
• Understanding of Agile development methodologies

Responsibilities:
• Develop and maintain web applications
• Collaborate with cross-functional teams
• Write clean, maintainable code
• Participate in code reviews
• Troubleshoot and debug applications

Preferred Qualifications:
• Experience with Docker and Kubernetes
• Knowledge of CI/CD pipelines
• Familiarity with testing frameworks
• Experience with database design and optimization
            """
            st.session_state.sample_job = sample_job
            st.rerun()
        
        if hasattr(st.session_state, 'sample_job'):
            st.text_area("Sample Job Description", value=st.session_state.sample_job, height=200)
    
    else:
        # Validate inputs
        is_valid, errors = validate_inputs(uploaded_file, job_description)
        
        if not is_valid:
            st.error("Please fix the following issues:")
            for error in errors:
                st.error(f"• {error}")
            return
        
        # Process analysis
        with st.container():
            results = process_resume_analysis(uploaded_file, job_description)
            
            if not results["success"]:
                display_error_message(results["error"], "Analysis Failed")
                return
            
            # Display results
            display_success_message("✅ Analysis completed successfully!")
            display_results(results)


if __name__ == "__main__":
    main() 