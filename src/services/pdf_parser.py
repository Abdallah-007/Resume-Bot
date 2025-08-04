"""
PDF parsing service for extracting text from resume PDFs.
Uses PyMuPDF for reliable text extraction.
"""

import fitz  # PyMuPDF
import io
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """Service for parsing PDF files and extracting text content."""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_text_pymupdf(self, pdf_file) -> str:
        """
        Extract text using PyMuPDF (fitz).
        Robust text extraction with better formatting preservation.
        """
        try:
            if hasattr(pdf_file, 'read'):
                pdf_bytes = pdf_file.read()
                pdf_file.seek(0)  # Reset file pointer
            else:
                pdf_bytes = pdf_file
            
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                # Use get_text with layout preservation
                page_text = page.get_text("text")
                if page_text.strip():
                    text += page_text
                    text += "\n\n"  # Add page break with spacing
            
            doc.close()
            return text.strip()
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {str(e)}")
            return ""
    
    def extract_text(self, pdf_file, method: str = "auto") -> Dict[str, Any]:
        """
        Extract text from PDF using PyMuPDF.
        
        Args:
            pdf_file: PDF file object or bytes
            method: Extraction method (kept for compatibility, always uses PyMuPDF)
        
        Returns:
            Dict containing extracted text and metadata
        """
        result = {
            "text": "",
            "method_used": "pymupdf",
            "success": False,
            "error": None,
            "page_count": 0
        }
        
        try:
            # Get page count first
            if hasattr(pdf_file, 'read'):
                pdf_bytes = pdf_file.read()
                pdf_file.seek(0)
            else:
                pdf_bytes = pdf_file
            
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            result["page_count"] = doc.page_count
            doc.close()
            
            # Reset file pointer if it's a file object
            if hasattr(pdf_file, 'seek'):
                pdf_file.seek(0)
            
            # Always use PyMuPDF for extraction
            text = self.extract_text_pymupdf(pdf_file)
            
            if text and len(text.strip()) > 10:
                result["text"] = text
                result["success"] = True
            else:
                result["error"] = "No text extracted or text too short"
                
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"PDF extraction failed: {str(e)}")
        
        return result
    
    def validate_pdf(self, pdf_file) -> Dict[str, Any]:
        """
        Validate if the uploaded file is a valid PDF.
        
        Returns:
            Dict with validation results
        """
        validation = {
            "is_valid": False,
            "error": None,
            "file_size": 0,
            "page_count": 0
        }
        
        try:
            if hasattr(pdf_file, 'read'):
                pdf_bytes = pdf_file.read()
                pdf_file.seek(0)
                validation["file_size"] = len(pdf_bytes)
            else:
                pdf_bytes = pdf_file
                validation["file_size"] = len(pdf_bytes)
            
            # Try to open with PyMuPDF to validate
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            validation["page_count"] = doc.page_count
            validation["is_valid"] = True
            doc.close()
            
        except Exception as e:
            validation["error"] = f"Invalid PDF file: {str(e)}"
            logger.error(f"PDF validation failed: {str(e)}")
        
        return validation 