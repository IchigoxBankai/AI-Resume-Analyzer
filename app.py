import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App imports
from database.database import ResumeDatabase
from modules.pdf_parser import PDFParser
from modules.skill_extractor import SkillExtractor
from modules.ats_checker import ATSChecker
from modules.ai_suggestions import AISuggestions
from modules.resume_analyzer import ResumeAnalyzer
from reports.pdf_generator import PDFReportGenerator

# Page config
st.set_page_config(
    page_title="ResumeAI Analyzer - Next-Gen ATS Optimization",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB
db = ResumeDatabase()

# Load Custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
local_css(css_path)

# Ensure session state variables
if "api_key" not in st.session_state:
    st.session_state["api_key"] = os.getenv("OPENAI_API_KEY", "")

# Update environment variable with state key
if st.session_state["api_key"]:
    os.environ["OPENAI_API_KEY"] = st.session_state["api_key"]

# Sidebar Navigation Header
st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem 0 1.5rem 0;'>
        <div style='font-size: 2.5rem; margin-bottom: 0.25rem;'>💼</div>
        <h2 style='color: #F8FAFC; margin: 0; font-size: 1.5rem; font-weight: 800;'>ResumeAI</h2>
        <span style='background: rgba(99, 102, 241, 0.2); color: #a5b4fc; font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.4);'>PRO v2.0</span>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigation", ["🏠 Home", "📊 Analyze Resume", "📜 Analysis History", "⚙️ Settings"])

st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style='padding: 0.75rem; background: rgba(30, 41, 59, 0.6); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.08); font-size: 0.8rem; color: #94a3b8;'>
        <strong style='color: #f8fafc;'>🔒 Privacy First:</strong><br>Resumes are parsed securely in-memory and logged to your local database.
    </div>
""", unsafe_allow_html=True)

# ----------------- HOME PAGE -----------------
if menu == "🏠 Home":
    st.markdown("""
        <div class="hero-container">
            <div class="hero-badge">
                <span>⚡ Powered by Advanced NLP & OpenAI</span>
            </div>
            <h1 class="hero-title">Optimize Your Resume for ATS</h1>
            <p class="hero-subtitle">Elevate your career profile with AI-driven keyword density checks, format verification, target role matching, and automated bullet recommendations.</p>
        </div>
    """, unsafe_allow_html=True)

    # Visual Cards Layout using HTML Grid
    st.markdown("""
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon-wrapper">📈</div>
                <div class="feature-title">ATS Compatibility</div>
                <div class="feature-desc">Rigorous evaluation of contact info, structural headers, section density, and bullet formatting.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon-wrapper">🧠</div>
                <div class="feature-title">Smart Skill Extraction</div>
                <div class="feature-desc">Extract engineering, technical, data, cloud, and leadership competencies automatically.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon-wrapper">🎯</div>
                <div class="feature-title">Target Role Match</div>
                <div class="feature-desc">Compare your profile against benchmark role requirements to reveal critical keyword gaps.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon-wrapper">💡</div>
                <div class="feature-title">AI Action Items</div>
                <div class="feature-desc">Receive impactful, quantitative bullet point improvements tailored to your career goal.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center; color: #f8fafc; font-weight: 700; margin-top: 2rem;'>Get Started in 3 Simple Steps</h3>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="step-container">
            <div class="step-card">
                <div class="step-number">1</div>
                <div class="step-text">
                    <h4>Upload PDF Resume</h4>
                    <p>Select your existing PDF resume file in the <strong>Analyze Resume</strong> section.</p>
                </div>
            </div>
            <div class="step-card">
                <div class="step-number">2</div>
                <div class="step-text">
                    <h4>Select Target Role</h4>
                    <p>Choose or input your target job title to trigger tailored keyword gap analysis.</p>
                </div>
            </div>
            <div class="step-card">
                <div class="step-number">3</div>
                <div class="step-text">
                    <h4>Export PDF Report</h4>
                    <p>Review interactive charts and download a executive PDF evaluation report.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ----------------- ANALYZE RESUME -----------------
elif menu == "📊 Analyze Resume":
    st.markdown("""
        <div style='margin-bottom: 1.5rem;'>
            <h2 style='color: #f8fafc; font-weight: 800; margin-bottom: 0.25rem;'>📊 Resume Analysis Dashboard</h2>
            <p style='color: #94a3b8;'>Upload your PDF resume to generate instant scoring, skill tags, and optimization suggestions.</p>
        </div>
    """, unsafe_allow_html=True)

    # Two column input layout
    col_upload, col_role = st.columns([3, 2])
    
    with col_upload:
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="resume_uploader")
        
    with col_role:
        target_role = st.selectbox(
            "Target Job Role",
            ["", "Python Developer", "Frontend Developer", "Data Analyst", "Data Scientist", "DevOps Engineer", "Full Stack Developer", "Product Manager", "Custom Role"]
        )
        if target_role == "Custom Role":
            custom_role = st.text_input("Enter Custom Job Title (e.g. Backend Architect)")
        else:
            custom_role = None

    # Determine job role name
    final_role = custom_role if target_role == "Custom Role" else target_role
    if not final_role:
        final_role = None

    if uploaded_file is not None:
        if st.button("🚀 Run AI Analysis", use_container_width=True):
            with st.spinner("Parsing text, evaluating formatting, and analyzing skill density..."):
                try:
                    # Read bytes
                    pdf_bytes = uploaded_file.read()
                    
                    # Orchestrate all analysis steps
                    analysis_result = ResumeAnalyzer.analyze(pdf_bytes, uploaded_file.name, final_role)
                    
                    parsed_resume = analysis_result["parsed_resume"]
                    skills = analysis_result["skills"]
                    ats_results = analysis_result["ats_results"]
                    suggestions = analysis_result["suggestions"]
                    
                    # Store variables in session state for rendering
                    st.session_state["active_analysis"] = {
                        "filename": uploaded_file.name,
                        "parsed_resume": parsed_resume,
                        "skills": skills,
                        "ats_results": ats_results,
                        "suggestions": suggestions,
                        "job_role": final_role if final_role else "General Check"
                    }
                    
                    # Save to database
                    db.save_analysis(
                        resume_name=uploaded_file.name,
                        ats_score=ats_results["ats_score"],
                        job_role=final_role if final_role else "General Check",
                        skills=skills,
                        missing_skills=ats_results.get("missing_skills", []),
                        suggestions=suggestions,
                        details={
                            "email": parsed_resume.get("email"),
                            "phone": parsed_resume.get("phone"),
                            "name": parsed_resume.get("name"),
                            "breakdown": ats_results["breakdown"]
                        }
                    )
                    st.success("✅ Analysis completed and saved to history!")
                except Exception as e:
                    st.error(f"Error during analysis: {e}")

    # Display Active Analysis Results
    if "active_analysis" in st.session_state:
        analysis = st.session_state["active_analysis"]
        st.markdown("---")
        
        st.markdown(f"""
            <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;'>
                <h3 style='color: #f8fafc; font-weight: 700; margin: 0;'>Evaluation Results: <span style='color: #818cf8;'>{analysis['filename']}</span></h3>
                <span style='background: rgba(99, 102, 241, 0.2); color: #a5b4fc; padding: 0.35rem 0.85rem; border-radius: 20px; border: 1px solid rgba(99, 102, 241, 0.4); font-size: 0.85rem; font-weight: 600;'>Role: {analysis['job_role']}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # KPI Metric Cards
        ats_score = analysis["ats_results"]["ats_score"]
        skills_count = len(analysis["skills"])
        match_pct = analysis["ats_results"]["match_percentage"]
        
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        with col_kpi1:
            st.markdown(f"""
                <div class="metric-card ats-score">
                    <div class="metric-header">
                        <span class="metric-label">ATS Score</span>
                        <span class="metric-icon">🎯</span>
                    </div>
                    <div class="metric-value">{ats_score}<span style="font-size: 1.2rem; color: #94a3b8;">/100</span></div>
                </div>
            """, unsafe_allow_html=True)
        with col_kpi2:
            st.markdown(f"""
                <div class="metric-card skills-count">
                    <div class="metric-header">
                        <span class="metric-label">Skills Detected</span>
                        <span class="metric-icon">💡</span>
                    </div>
                    <div class="metric-value">{skills_count}</div>
                </div>
            """, unsafe_allow_html=True)
        with col_kpi3:
            st.markdown(f"""
                <div class="metric-card match-rate">
                    <div class="metric-header">
                        <span class="metric-label">Job Match Rate</span>
                        <span class="metric-icon">📈</span>
                    </div>
                    <div class="metric-value">{match_pct}%</div>
                </div>
            """, unsafe_allow_html=True)

        # Plotly Charts Section
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Breakdown Chart
            breakdown = analysis["ats_results"]["breakdown"]
            breakdown_df = pd.DataFrame({
                "Category": ["Contact Details", "Structure & Sections", "Formatting & Bullets", "Skill Density / Role Match"],
                "Score": [breakdown["contact_info"], breakdown["structure"], breakdown["formatting"], breakdown["skills_score"]],
                "Max Score": [10, 20, 20, 50]
            })
            
            fig_breakdown = px.bar(
                breakdown_df,
                x="Score",
                y="Category",
                orientation='h',
                title="<b>Resume Score Breakdown</b>",
                range_x=[0, 55],
                text="Score",
                color="Score",
                color_continuous_scale=["#6366f1", "#8b5cf6", "#10b981"]
            )
            fig_breakdown.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f8fafc', family='Plus Jakarta Sans'),
                showlegend=False,
                height=320,
                margin=dict(l=20, r=20, t=50, b=20),
                xaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.08)')
            )
            st.plotly_chart(fig_breakdown, use_container_width=True)

        with col_chart2:
            # ATS score Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = ats_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "<b>Overall ATS Compatibility</b>", 'font': {'size': 18, 'color': '#f8fafc'}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
                    'bar': {'color': "#6366f1"},
                    'bgcolor': "rgba(30, 41, 59, 0.6)",
                    'borderwidth': 1,
                    'bordercolor': "rgba(255, 255, 255, 0.1)",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.2)'},
                        {'range': [50, 80], 'color': 'rgba(245, 158, 11, 0.2)'},
                        {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.2)'}
                    ],
                    'threshold': {
                        'line': {'color': "#10b981", 'width': 4},
                        'thickness': 0.75,
                        'value': 80
                    }
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f8fafc', family='Plus Jakarta Sans'),
                height=320,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        # Profile Summary Card
        parsed = analysis["parsed_resume"]
        st.markdown(f"""
            <div style='background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem;'>
                <h4 style='color: #f8fafc; font-weight: 700; margin: 0 0 0.5rem 0;'>Candidate Profile Extracted</h4>
                <div style='display: flex; gap: 1.5rem; flex-wrap: wrap; color: #cbd5e1; font-size: 0.95rem;'>
                    <span>👤 <strong>Name:</strong> {parsed.get('name', 'N/A')}</span>
                    <span>📧 <strong>Email:</strong> {parsed.get('email', 'N/A')}</span>
                    <span>📞 <strong>Phone:</strong> {parsed.get('phone', 'N/A')}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Detected & Missing Skills
        col_skills, col_missing = st.columns(2)
        
        with col_skills:
            st.markdown("#### Detected Skills Tag Cloud")
            skills_html = "".join([f'<span class="skill-tag">{skill}</span>' for skill in analysis["skills"]])
            if skills_html:
                st.markdown(f'<div class="tags-wrapper">{skills_html}</div>', unsafe_allow_html=True)
            else:
                st.info("No explicit skills detected in resume body.")

        with col_missing:
            if analysis.get("job_role") and analysis["ats_results"].get("missing_skills"):
                st.markdown("#### Missing Target Keywords")
                missing_html = "".join([f'<span class="missing-tag">{skill}</span>' for skill in analysis["ats_results"]["missing_skills"]])
                st.markdown(f'<div class="tags-wrapper">{missing_html}</div>', unsafe_allow_html=True)

        # AI Actionable Suggestions
        st.markdown("### 💡 Strategic Improvement Suggestions")
        for sug in analysis["suggestions"]:
            st.markdown(f"""
                <div class="suggestion-card">
                    <span class="suggestion-icon">💡</span>
                    <div>{sug}</div>
                </div>
            """, unsafe_allow_html=True)

        # PDF Download Report Section
        st.markdown("---")
        st.markdown("### 📥 Download Executive PDF Evaluation")
        
        report_pdf_name = f"report_{analysis['filename']}"
        report_pdf_path = os.path.join(os.path.dirname(__file__), "reports", report_pdf_name)
        
        try:
            PDFReportGenerator.generate_report(
                output_pdf_path=report_pdf_path,
                resume_name=analysis['filename'],
                ats_score=ats_score,
                job_role=analysis['job_role'],
                skills=analysis['skills'],
                missing_skills=analysis['ats_results'].get("missing_skills", []),
                suggestions=analysis['suggestions']
            )
            
            with open(report_pdf_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()
                
            st.download_button(
                label="📥 Download Detailed PDF Evaluation Report",
                data=pdf_data,
                file_name=f"ResumeAI_Analysis_{analysis['filename']}",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Could not generate downloadable PDF report: {e}")

# ----------------- ANALYSIS HISTORY -----------------
elif menu == "📜 Analysis History":
    st.markdown("""
        <div style='margin-bottom: 1.5rem;'>
            <h2 style='color: #f8fafc; font-weight: 800; margin-bottom: 0.25rem;'>📜 Evaluation History & Archives</h2>
            <p style='color: #94a3b8;'>Review and search past candidate evaluations stored in SQLite.</p>
        </div>
    """, unsafe_allow_html=True)

    history_data = db.get_history()
    
    if not history_data:
        st.info("No saved logs found. Upload and analyze a resume to populate history.")
    else:
        # Calculate summary KPIs for history
        total_evals = len(history_data)
        avg_score = round(sum(item["ats_score"] for item in history_data) / total_evals, 1)
        top_score = max(item["ats_score"] for item in history_data)

        st.markdown(f"""
            <div class="metric-card-grid">
                <div class="metric-card ats-score">
                    <div class="metric-label">Total Resumes Scanned</div>
                    <div class="metric-value">{total_evals}</div>
                </div>
                <div class="metric-card skills-count">
                    <div class="metric-label">Average ATS Score</div>
                    <div class="metric-value">{avg_score}</div>
                </div>
                <div class="metric-card match-rate">
                    <div class="metric-label">Highest Score Logged</div>
                    <div class="metric-value">{top_score}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Search Filter Bar
        search_query = st.text_input("🔍 Search History by Candidate Name, Resume, or Job Role", "")

        # Convert to DataFrame
        records = []
        filtered_items = []
        for idx, item in enumerate(history_data):
            cand_name = item['details'].get('name', 'N/A') if item.get('details') else 'N/A'
            matches_search = (
                search_query.lower() in item["resume_name"].lower() or 
                search_query.lower() in item["job_role"].lower() or
                search_query.lower() in str(cand_name).lower()
            )
            if matches_search:
                filtered_items.append(item)
                records.append({
                    "Index": idx + 1,
                    "Date": item["timestamp"],
                    "Resume File": item["resume_name"],
                    "Candidate Name": cand_name,
                    "Target Role": item["job_role"],
                    "ATS Score": item["ats_score"],
                    "Skills Count": len(item["skills"])
                })
            
        if records:
            history_df = pd.DataFrame(records)
            st.dataframe(history_df, use_container_width=True)

            st.markdown("### 🔍 Detailed Resume Logs")
            for item in filtered_items:
                with st.expander(f"📄 {item['resume_name']} ({item['job_role']}) — Score: {item['ats_score']}/100 — {item['timestamp']}"):
                    col_left, col_right = st.columns([1, 1])
                    
                    with col_left:
                        email = item['details'].get('email', 'N/A') if item.get('details') else 'N/A'
                        phone = item['details'].get('phone', 'N/A') if item.get('details') else 'N/A'
                        st.markdown(f"**Email:** {email} | **Phone:** {phone}")
                        
                        st.markdown("**Skills Found:**")
                        skills_chips = "".join([f'<span class="skill-tag">{s}</span>' for s in item["skills"]])
                        st.markdown(f'<div class="tags-wrapper">{skills_chips}</div>', unsafe_allow_html=True)
                        
                        if item.get("missing_skills"):
                            st.markdown("**Missing Target Skills:**")
                            missing_chips = "".join([f'<span class="missing-tag">{s}</span>' for s in item["missing_skills"]])
                            st.markdown(f'<div class="tags-wrapper">{missing_chips}</div>', unsafe_allow_html=True)
                    
                    with col_right:
                        st.markdown("**Actionable Suggestions:**")
                        for sug in item["suggestions"]:
                            st.markdown(f"- {sug}")
                    
                    # PDF generator trigger
                    report_pdf_name = f"report_hist_{item['id']}_{item['resume_name']}"
                    report_pdf_path = os.path.join(os.path.dirname(__file__), "reports", report_pdf_name)
                    
                    try:
                        PDFReportGenerator.generate_report(
                            output_pdf_path=report_pdf_path,
                            resume_name=item['resume_name'],
                            ats_score=item['ats_score'],
                            job_role=item['job_role'],
                            skills=item['skills'],
                            missing_skills=item.get("missing_skills", []),
                            suggestions=item['suggestions']
                        )
                        
                        with open(report_pdf_path, "rb") as pdf_file:
                            pdf_data = pdf_file.read()
                            
                        st.download_button(
                            label=f"📥 Download Archived PDF Report ({item['resume_name']})",
                            data=pdf_data,
                            file_name=f"ResumeAI_Analysis_{item['resume_name']}",
                            mime="application/pdf",
                            key=f"dl_btn_{item['id']}"
                        )
                    except Exception as ex:
                        st.error(f"Failed to generate report: {ex}")
        else:
            st.warning("No records found matching your search query.")

# ----------------- SETTINGS PAGE -----------------
elif menu == "⚙️ Settings":
    st.markdown("""
        <div style='margin-bottom: 1.5rem;'>
            <h2 style='color: #f8fafc; font-weight: 800; margin-bottom: 0.25rem;'>⚙️ System Settings & Integrations</h2>
            <p style='color: #94a3b8;'>Configure API credentials and inspect service status.</p>
        </div>
    """, unsafe_allow_html=True)

    col_api, col_status = st.columns([3, 2])

    with col_api:
        st.markdown("### OpenAI API Credentials")
        api_key_input = st.text_input("OpenAI API Key", value=st.session_state["api_key"], type="password", help="Providing this enables OpenAI LLM tailored recommendation points.")
        
        if st.button("💾 Save Credentials", use_container_width=True):
            st.session_state["api_key"] = api_key_input
            os.environ["OPENAI_API_KEY"] = api_key_input
            
            # Save key to .env
            env_path = os.path.join(os.path.dirname(__file__), ".env")
            try:
                with open(env_path, "w") as f:
                    f.write(f"OPENAI_API_KEY={api_key_input}\n")
                st.success("✅ Configuration saved to `.env` file successfully!")
            except Exception as e:
                st.error(f"Could not write to `.env`: {e}")
                st.success("API key stored in session state.")

    with col_status:
        st.markdown("### System Health Monitor")
        
        db_status = "🟢 Active (SQLite)"
        openai_status = "🟢 Configured" if st.session_state["api_key"] else "🟡 Fallback (Heuristic Rules)"
        pdf_engine = "🟢 Active (PyMuPDF)"
        
        st.markdown(f"""
            <div style='background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.25rem;'>
                <div style='margin-bottom: 0.75rem;'><strong>Database:</strong> {db_status}</div>
                <div style='margin-bottom: 0.75rem;'><strong>AI Recommendation Engine:</strong> {openai_status}</div>
                <div><strong>PDF Parser:</strong> {pdf_engine}</div>
            </div>
        """, unsafe_allow_html=True)
