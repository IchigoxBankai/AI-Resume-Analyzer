import os
import re
from openai import OpenAI

class AISuggestions:
    @staticmethod
    def generate_suggestions(parsed_resume, extracted_skills, ats_data, target_role=None):
        """Generates resume improvement suggestions using OpenAI API or rule-based fallback."""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if api_key:
            try:
                client = OpenAI(api_key=api_key)
                prompt = AISuggestions._build_openai_prompt(parsed_resume, extracted_skills, ats_data, target_role)
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional HR recruiter and resume optimization expert. Provide actionable resume improvement suggestions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                content = response.choices[0].message.content.strip()
                # Split response into structured points if it's raw text
                suggestions = [s.strip("- *").strip() for s in content.split("\n") if s.strip()]
                return [s for s in suggestions if len(s) > 10]
            except Exception as e:
                # If API call fails, fall back to rule-based suggestion generator
                print(f"OpenAI API call failed: {e}. Falling back to rule-based engine.")
                return AISuggestions._generate_rule_based_suggestions(parsed_resume, extracted_skills, ats_data, target_role)
        else:
            return AISuggestions._generate_rule_based_suggestions(parsed_resume, extracted_skills, ats_data, target_role)

    @staticmethod
    def _build_openai_prompt(parsed_resume, extracted_skills, ats_data, target_role):
        role_info = f"Target Job Role: {target_role}\n" if target_role else ""
        missing_skills_info = f"Missing Skills for role: {', '.join(ats_data.get('missing_skills', []))}\n" if target_role and ats_data.get('missing_skills') else ""
        
        prompt = f"""
Analyze the following resume details and provide 4-6 specific, actionable, and professional recommendations to improve the resume for ATS (Applicant Tracking Systems) and recruiters.

Resume Summary:
- Candidate Name: {parsed_resume.get('name', 'Candidate')}
- Detected Skills: {', '.join(extracted_skills)}
- Experience Section Length: {len(parsed_resume.get('experience', ''))} characters
- Projects Section Length: {len(parsed_resume.get('projects', ''))} characters
- Education Present: {'Yes' if parsed_resume.get('education') else 'No'}
- ATS Score: {ats_data.get('ats_score')}/100
{role_info}{missing_skills_info}

Please output only the bulleted suggestions, one per line. Do not include intro or outro text.
"""
        return prompt

    @staticmethod
    def _generate_rule_based_suggestions(parsed_resume, extracted_skills, ats_data, target_role=None):
        suggestions = []
        
        # 1. Contact Information
        if not parsed_resume.get("email"):
            suggestions.append("Add a professional email address to the contact section so recruiters can easily reach you.")
        if not parsed_resume.get("phone"):
            suggestions.append("Provide a phone number with country/area code in your contact header.")
            
        # 2. Key Sections
        if not parsed_resume.get("experience"):
            suggestions.append("Create a dedicated 'Experience' or 'Work History' section listing chronological positions, responsibilities, and key accomplishments.")
        else:
            # Check for metrics
            exp_text = parsed_resume.get("experience", "")
            has_metrics = any(char.isdigit() or char == '%' for char in exp_text)
            if not has_metrics:
                suggestions.append("Include measurable achievements (e.g., 'increased sales by 15%', 'reduced page load time by 30%') rather than just listing daily duties.")
            
            # Check length of experience
            if len(exp_text.split()) < 100:
                suggestions.append("Expand the 'Experience' section description. Detail your main technical stack and specific projects managed under each role.")

        if not parsed_resume.get("projects"):
            suggestions.append("Add a 'Projects' section to showcase personal or academic applications of your skills, especially if you have limited formal work experience.")
            
        if not parsed_resume.get("education"):
            suggestions.append("Add an 'Education' section outlining your degree, university name, and graduation year.")
            
        # 3. Formatting
        full_text = parsed_resume.get("full_text", "")
        word_count = len(full_text.split())
        if word_count < 250:
            suggestions.append("Your resume content is too brief. Try to expand on your technical skills, tools used, and detail project impact to reach at least 400 words.")
        elif word_count > 1200:
            suggestions.append("Your resume exceeds 1200 words. Try to keep it concise and tailored, ideally limiting it to a maximum of 2 pages.")
            
        # Check bullet points
        bullet_count = len(re.findall(r'[•\-\*]\s', full_text))
        if bullet_count < 4:
            suggestions.append("Use standard bullet points (•) instead of long paragraphs to present job duties and achievements. This improves readability for recruiters and ATS parsers.")
            
        # 4. Job Role Specific Suggestions
        if target_role:
            missing_skills = ats_data.get("missing_skills", [])
            if missing_skills:
                suggestions.append(f"Tailor your resume for the '{target_role}' role by incorporating missing keywords/skills: {', '.join(missing_skills[:3])}.")
            
            # Match score based suggestions
            match_pct = ats_data.get("match_percentage", 0)
            if match_pct < 60:
                suggestions.append(f"The resume match rate for '{target_role}' is low ({match_pct}%). Align your experience descriptions more closely with standard responsibilities of this role.")
                
        # 5. Generic checks
        if len(extracted_skills) < 8:
            suggestions.append("Increase the number of technical keywords and specific tool mentions. Add tools, frameworks, and packages you are familiar with.")
            
        # Add default general suggestions if suggestions list is too short
        if len(suggestions) < 3:
            suggestions.append("Incorporate standard action verbs (e.g., 'Developed', 'Optimized', 'Led', 'Designed') at the start of your experience bullet points.")
            suggestions.append("Ensure your resume layout is clean and uses standard fonts (e.g. Arial, Calibri) to prevent ATS rendering and parsing errors.")
            
        return suggestions
