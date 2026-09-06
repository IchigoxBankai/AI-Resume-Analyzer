from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class ATSChecker:
    # Typical skills/keywords mapping for standard roles to check when target job role is entered
    ROLE_KEYWORDS = {
        "python developer": ["python", "django", "flask", "fastapi", "sql", "git", "rest api", "docker", "unit testing", "aws", "postgresql"],
        "frontend developer": ["javascript", "react", "html", "css", "typescript", "angular", "vue", "tailwind", "bootstrap", "git", "web design"],
        "data analyst": ["sql", "excel", "python", "tableau", "power bi", "pandas", "data analytics", "r", "statistics", "data visualization", "etl"],
        "data scientist": ["python", "machine learning", "deep learning", "sql", "scikit-learn", "tensorflow", "pytorch", "r", "pandas", "statistics", "nlp"],
        "devops engineer": ["docker", "kubernetes", "aws", "jenkins", "ci/cd", "terraform", "ansible", "linux", "bash", "git", "python", "monitoring"],
        "full stack developer": ["javascript", "python", "react", "node.js", "sql", "html", "css", "django", "git", "aws", "docker", "rest api"],
        "product manager": ["agile", "scrum", "product management", "roadmap", "analytics", "market research", "communication", "leadership", "jira", "sql"]
    }

    @staticmethod
    def get_role_keywords(job_role):
        job_role_clean = job_role.lower().strip()
        # Find closest match or check substring match
        for role, keywords in ATSChecker.ROLE_KEYWORDS.items():
            if role in job_role_clean or job_role_clean in role:
                return keywords
        # If custom role, split words and try to use them as search keywords
        return [word for word in re.split(r'\W+', job_role_clean) if len(word) > 3]

    @staticmethod
    def calculate_ats_score(parsed_resume, extracted_skills, target_role=None):
        score_breakdown = {
            "contact_info": 0,    # Max 10
            "structure": 0,       # Max 20
            "formatting": 0,      # Max 20
            "skills_score": 0,    # Max 50
        }
        
        full_text = parsed_resume.get("full_text", "")
        
        # 1. Contact Info check (10 points)
        if parsed_resume.get("email"):
            score_breakdown["contact_info"] += 5
        if parsed_resume.get("phone"):
            score_breakdown["contact_info"] += 5
            
        # 2. Section presence check (20 points)
        # Check if the parsed resume segments these key sections
        if parsed_resume.get("education"):
            score_breakdown["structure"] += 5
        if parsed_resume.get("experience"):
            score_breakdown["structure"] += 5
        if parsed_resume.get("projects"):
            score_breakdown["structure"] += 5
        if extracted_skills:
            score_breakdown["structure"] += 5
            
        # 3. Formatting check (20 points)
        # - Check word count (optimal is 300 to 1000 words)
        words_count = len(full_text.split())
        if 300 <= words_count <= 1000:
            score_breakdown["formatting"] += 10
        elif 150 <= words_count < 300 or 1000 < words_count <= 1500:
            score_breakdown["formatting"] += 6
        else:
            score_breakdown["formatting"] += 3
            
        # - Check if bullet points are used
        bullet_count = len(re.findall(r'[•\-\*]\s', full_text))
        if bullet_count >= 5:
            score_breakdown["formatting"] += 10
        elif 1 <= bullet_count < 5:
            score_breakdown["formatting"] += 5
            
        # 4. Skills & Job Role Matching (50 points)
        missing_skills = []
        match_percentage = 0
        
        if target_role:
            target_keywords = ATSChecker.get_role_keywords(target_role)
            if target_keywords:
                # Calculate overlap between extracted skills (case-insensitive) and target keywords
                lower_extracted = [s.lower() for s in extracted_skills]
                matched_keywords = [kw for kw in target_keywords if kw.lower() in lower_extracted or any(kw.lower() in s.lower() for s in lower_extracted)]
                
                # Missing skills
                missing_skills = [kw.title() for kw in target_keywords if kw.lower() not in [m.lower() for m in matched_keywords]]
                
                # Set skills score based on overlap match
                overlap_ratio = len(matched_keywords) / len(target_keywords) if target_keywords else 0
                score_breakdown["skills_score"] = int(overlap_ratio * 50)
                match_percentage = int(overlap_ratio * 100)
            else:
                # Custom job role with no defined keywords, use fallback TF-IDF
                match_percentage = ATSChecker.calculate_tfidf_match(full_text, target_role)
                score_breakdown["skills_score"] = int(match_percentage * 0.5)
        else:
            # No target role, calculate skills score based on number of detected skills
            # 15+ skills = 50 pts, scaled down linearly
            num_skills = len(extracted_skills)
            score_breakdown["skills_score"] = min(50, int((num_skills / 15) * 50))
            match_percentage = int((score_breakdown["skills_score"] / 50) * 100)
            
        total_score = sum(score_breakdown.values())
        
        return {
            "ats_score": total_score,
            "breakdown": score_breakdown,
            "match_percentage": match_percentage,
            "missing_skills": missing_skills
        }

    @staticmethod
    def calculate_tfidf_match(resume_text, target_role_text):
        """Fallback TF-IDF similarity calculation for job matching when target role has no hardcoded skills."""
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([resume_text.lower(), target_role_text.lower()])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Normalize to percentage range
            return int(similarity * 100)
        except Exception:
            return 50  # default fallback
