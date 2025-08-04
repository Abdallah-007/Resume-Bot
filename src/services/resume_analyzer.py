"""
Resume analysis service using OpenRouter.ai and LangChain for intelligent resume evaluation.
"""

import os
import re
from typing import Dict, List, Any, Optional
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    try:
        nltk.download('punkt_tab')  # New NLTK version
    except:
        nltk.download('punkt')     # Fallback for older versions
    nltk.download('stopwords')


class ResumeAnalyzer:
    """Service for analyzing resumes against job descriptions using AI via OpenRouter."""
    
    def __init__(self, openrouter_api_key: str):
        self.openrouter_api_key = openrouter_api_key
        self.llm = ChatOpenAI(
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model_name="openai/gpt-3.5-turbo",
            temperature=0.3
        )
        
        # Initialize sentence transformer for semantic similarity
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.error(f"Failed to load sentence transformer: {e}")
            self.sentence_model = None
        
        # Common stop words
        self.stop_words = set(stopwords.words('english'))
        
        # Analysis prompts
        self.setup_prompts()
    
    def setup_prompts(self):
        """Setup LangChain prompts for different analysis tasks."""
        
        self.match_analysis_prompt = PromptTemplate(
            input_variables=["resume_text", "job_description"],
            template="""
            You are an expert HR professional and resume analyst. Analyze how well this resume matches the job description.

            RESUME:
            {resume_text}

            JOB DESCRIPTION:
            {job_description}

            Please provide a detailed analysis in JSON format with the following structure:
            {{
                "overall_match_score": <integer 0-100>,
                "strengths": ["strength1", "strength2", ...],
                "weaknesses": ["weakness1", "weakness2", ...],
                "missing_keywords": ["keyword1", "keyword2", ...],
                "recommendations": ["recommendation1", "recommendation2", ...],
                "skill_matches": {{
                    "technical_skills": ["skill1", "skill2", ...],
                    "soft_skills": ["skill1", "skill2", ...],
                    "missing_skills": ["skill1", "skill2", ...]
                }},
                "experience_analysis": {{
                    "relevant_experience": "description",
                    "experience_gaps": "description",
                    "years_match": "assessment"
                }}
            }}

            Focus on:
            1. Keyword matching between resume and job description
            2. Skills alignment (technical and soft skills)
            3. Experience relevance and level
            4. Education requirements
            5. Specific qualifications mentioned in the job posting
            """
        )
        
        self.improvement_prompt = PromptTemplate(
            input_variables=["resume_text", "job_description", "analysis"],
            template="""
            Based on the resume analysis, provide specific, actionable improvement suggestions.

            RESUME:
            {resume_text}

            JOB DESCRIPTION:
            {job_description}

            ANALYSIS:
            {analysis}

            Provide improvement suggestions in JSON format:
            {{
                "immediate_improvements": [
                    {{
                        "section": "section_name",
                        "current_issue": "description",
                        "suggested_change": "specific_suggestion"
                    }}
                ],
                "keyword_optimization": [
                    {{
                        "missing_keyword": "keyword",
                        "suggestion": "how_to_incorporate",
                        "priority": "high/medium/low"
                    }}
                ],
                "formatting_suggestions": ["suggestion1", "suggestion2", ...],
                "content_enhancements": ["enhancement1", "enhancement2", ...]
            }}
            
            Be specific and actionable. Focus on changes that will improve the match score.
            """
        )
    
    def extract_keywords(self, text: str, top_n: int = 20) -> List[str]:
        """Extract important keywords from text."""
        try:
            # Clean and tokenize text
            text = re.sub(r'[^\w\s]', ' ', text.lower())
            
            try:
                # Try NLTK tokenization first
                tokens = word_tokenize(text)
            except Exception as nltk_error:
                logger.warning(f"NLTK tokenization failed: {nltk_error}, using simple split")
                # Fallback to simple tokenization
                tokens = text.split()
            
            # Remove stop words and short words
            keywords = [
                word for word in tokens 
                if word not in self.stop_words and len(word) > 2
            ]
            
            # Count frequency and return top keywords
            keyword_freq = Counter(keywords)
            return [word for word, _ in keyword_freq.most_common(top_n)]
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def calculate_semantic_similarity(self, resume_text: str, job_description: str) -> float:
        """Calculate semantic similarity between resume and job description."""
        try:
            if not self.sentence_model:
                return 0.0
            
            # Generate embeddings
            resume_embedding = self.sentence_model.encode([resume_text])
            job_embedding = self.sentence_model.encode([job_description])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {e}")
            return 0.0
    
    def analyze_resume(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Perform comprehensive resume analysis against job description.
        
        Args:
            resume_text: Extracted text from resume PDF
            job_description: Target job description text
            
        Returns:
            Comprehensive analysis results
        """
        try:
            # Get AI analysis
            prompt = self.match_analysis_prompt.format(
                resume_text=resume_text,
                job_description=job_description
            )
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse JSON response
            try:
                ai_analysis = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                ai_analysis = self._parse_fallback_response(response.content)
            
            # Add keyword analysis
            resume_keywords = self.extract_keywords(resume_text)
            job_keywords = self.extract_keywords(job_description)
            
            # Calculate keyword overlap
            common_keywords = set(resume_keywords) & set(job_keywords)
            keyword_match_rate = len(common_keywords) / len(job_keywords) if job_keywords else 0
            
            # Calculate semantic similarity
            semantic_score = self.calculate_semantic_similarity(resume_text, job_description)
            
            # Combine results
            analysis_result = {
                "ai_analysis": ai_analysis,
                "keyword_analysis": {
                    "resume_keywords": resume_keywords,
                    "job_keywords": job_keywords,
                    "common_keywords": list(common_keywords),
                    "keyword_match_rate": round(keyword_match_rate * 100, 2),
                    "missing_keywords": list(set(job_keywords) - set(resume_keywords))
                },
                "semantic_similarity": round(semantic_score * 100, 2),
                "analysis_timestamp": self._get_timestamp()
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            return {
                "error": str(e),
                "ai_analysis": {},
                "keyword_analysis": {},
                "semantic_similarity": 0,
                "analysis_timestamp": self._get_timestamp()
            }
    
    def get_improvement_suggestions(self, resume_text: str, job_description: str, analysis: Dict) -> Dict[str, Any]:
        """Generate specific improvement suggestions based on analysis."""
        try:
            prompt = self.improvement_prompt.format(
                resume_text=resume_text,
                job_description=job_description,
                analysis=json.dumps(analysis.get("ai_analysis", {}))
            )
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            try:
                suggestions = json.loads(response.content)
            except json.JSONDecodeError:
                suggestions = self._parse_fallback_suggestions(response.content)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Improvement suggestions failed: {e}")
            return {
                "immediate_improvements": [],
                "keyword_optimization": [],
                "formatting_suggestions": [],
                "content_enhancements": []
            }
    
    def _parse_fallback_response(self, response_text: str) -> Dict[str, Any]:
        """Fallback parser for malformed JSON responses."""
        return {
            "overall_match_score": 50,
            "strengths": ["Analysis completed"],
            "weaknesses": ["Response parsing issue"],
            "missing_keywords": [],
            "recommendations": ["Consider manual review"],
            "skill_matches": {
                "technical_skills": [],
                "soft_skills": [],
                "missing_skills": []
            },
            "experience_analysis": {
                "relevant_experience": "Analysis incomplete",
                "experience_gaps": "Unknown",
                "years_match": "Cannot determine"
            }
        }
    
    def _parse_fallback_suggestions(self, response_text: str) -> Dict[str, Any]:
        """Fallback parser for improvement suggestions."""
        return {
            "immediate_improvements": [
                {
                    "section": "General",
                    "current_issue": "Response parsing issue",
                    "suggested_change": "Manual review recommended"
                }
            ],
            "keyword_optimization": [],
            "formatting_suggestions": ["Review document formatting"],
            "content_enhancements": ["Consider professional review"]
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for analysis."""
        from datetime import datetime
        return datetime.now().isoformat() 