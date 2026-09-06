from modules.pdf_parser import PDFParser
from modules.skill_extractor import SkillExtractor
from modules.ats_checker import ATSChecker
from modules.ai_suggestions import AISuggestions

class ResumeAnalyzer:
    @staticmethod
    def analyze(pdf_bytes, resume_name, target_role=None):
        """Runs the entire resume analysis pipeline and returns aggregated structured results."""
        # 1. Parse Resume Text and Sections
        parsed_resume = PDFParser.parse_resume(pdf_bytes)
        
        # 2. Extract Skills
        skills = SkillExtractor.extract_skills(parsed_resume["full_text"])
        
        # 3. Score ATS details
        ats_results = ATSChecker.calculate_ats_score(parsed_resume, skills, target_role=target_role)
        
        # 4. Generate recommendations
        suggestions = AISuggestions.generate_suggestions(parsed_resume, skills, ats_results, target_role=target_role)
        
        return {
            "parsed_resume": parsed_resume,
            "skills": skills,
            "ats_results": ats_results,
            "suggestions": suggestions,
            "job_role": target_role if target_role else "General Check"
        }
