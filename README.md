# AI Resume Assistant

An intelligent tool that analyzes resumes against job descriptions to provide improvement suggestions, matching scores, and keyword recommendations.

## Features

- 📄 PDF resume parsing and text extraction
- 🎯 Job description analysis and comparison
- 📊 Resume-job matching score
- 💡 Improvement suggestions and recommendations
- 🔑 Missing keywords identification
- 🎨 Modern Streamlit web interface

## Technologies Used

- **PDF Parsing**: PyMuPDF (fitz) and pdfplumber
- **NLP & Analysis**: OpenRouter.ai GPT models via LangChain
- **UI**: Streamlit
- **Text Processing**: NLTK, sentence-transformers
- **Vector Search**: FAISS
- **Visualization**: matplotlib, seaborn, plotly

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-resume-assistant
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenRouter API key
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Upload your resume (PDF format)
3. Paste the target job description
4. Get analysis results with:
   - Match score
   - Improvement suggestions
   - Missing keywords
   - Detailed feedback

## Project Structure

```
ai-resume-assistant/
├── app.py                 # Main Streamlit application
├── src/
│   ├── components/        # UI components
│   ├── services/          # Core business logic
│   └── utils/            # Utility functions
├── tests/                # Test files
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## License

MIT License 