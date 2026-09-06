# ResumeAI Analyzer

ResumeAI Analyzer is a modern, clean, and professional SaaS-style web application built using Python and Streamlit to analyze, score, and offer actionable suggestions to optimize resumes for Applicant Tracking Systems (ATS).

## Features

- **ATS Compatibility Score**: Automated metrics scoring layout, contact presence, sections structure, and content length.
- **Skill Extraction**: High-accuracy extraction of programming, web dev, cloud/DevOps, database, data analytics, and soft skills using NLP dictionary lookup.
- **Target Role Match**: Align your resume against specific target roles (e.g. Python Developer, Frontend Developer, Data Analyst) and get a job match percentage breakdown.
- **Actionable Gap Recommendations**: AI-powered suggestions (using OpenAI GPT-3.5) or logic fallback engine to optimize bullet points, metrics representation, and missing keywords.
- **Visual Analytics**: Interactive, premium dashboards using Plotly charts visualizing score category breakdown and overall compatibility gauge.
- **Analysis History**: Persistent SQLite-based database logging previous resume runs for local review.
- **PDF Report Export**: Professional, styled PDF export reports compiling analysis scores and suggestions using ReportLab layout.

## Project Structure

```
ResumeAI-Analyzer/
├── app.py
├── requirements.txt
├── README.md
├── .env
├── assets/
│   └── style.css
├── modules/
│   ├── pdf_parser.py
│   ├── resume_analyzer.py
│   ├── skill_extractor.py
│   ├── ats_checker.py
│   └── ai_suggestions.py
├── database/
│   └── database.py
└── reports/
    └── pdf_generator.py
```

## Setup & Installation

### 1. Clone the repository
Navigate to your active workspace folder.

### 2. Install requirements
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Create or open `.env` at the root and insert your OpenAI API Key (optional fallback is enabled):
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run application
```bash
streamlit run app.py
```

## Future Scope
- User authentication and multi-user login.
- Cloud object storage for uploaded PDFs.
- Automated resume tailoring suggestions with custom output text files.
- Visual Resume Template Builder.
