import re

class SkillExtractor:
    # A curated list of skills categorized by domain
    SKILL_DB = {
        # Programming Languages
        "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "php", "go", "rust", "scala", "kotlin", "swift", "r", "matlab", "bash", "shell",
        # Frontend / Web
        "react", "angular", "vue", "next.js", "nextjs", "nuxt", "svelte", "html", "css", "sass", "bootstrap", "tailwind", "jquery", "webpack", "vite",
        # Backend / Frameworks
        "django", "flask", "fastapi", "spring", "spring boot", "express", "express.js", "nest.js", "laravel", "asp.net", "rails", "node.js", "nodejs",
        # Databases & Cache
        "sql", "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "firebase", "oracle",
        # Cloud & DevOps
        "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github", "gitlab", "ci/cd", "cicd", "terraform", "ansible", "nginx", "linux",
        # Data Science & AI
        "machine learning", "deep learning", "nlp", "natural language processing", "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas", "numpy", "scipy", "data science", "ai", "artificial intelligence",
        # Data Analytics & BI
        "excel", "tableau", "power bi", "looker", "spark", "hadoop", "etl", "data analytics", "data warehousing", "data visualization",
        # Soft Skills & Project Management
        "agile", "scrum", "project management", "communication", "leadership", "problem solving", "teamwork", "product management", "system design", "microservices", "testing", "unit testing", "qa", "jest", "cypress"
    }

    @staticmethod
    def extract_skills(text):
        """Extracts skills from text using a case-insensitive dictionary lookup."""
        text_lower = text.lower()
        # Clean text to normalize spaces
        text_normalized = re.sub(r'\s+', ' ', text_lower)
        
        found_skills = set()
        
        # Word boundary matching for all skills in our DB
        for skill in SkillExtractor.SKILL_DB:
            # Escape skill for safe regex matching (especially for c++, c#, .net, etc.)
            escaped_skill = re.escape(skill)
            
            # Handle special boundaries for skills containing symbols or numbers
            if skill in ["c++", "c#", "node.js", "next.js", "nest.js", "ci/cd"]:
                pattern = r'(?:^|\s|[.,/():])' + escaped_skill + r'(?:$|\s|[.,/():])'
            else:
                pattern = r'\b' + escaped_skill + r'\b'
                
            if re.search(pattern, text_normalized):
                # Standardize spelling in output display
                found_skills.add(SkillExtractor.standardize_skill_name(skill))
                
        return sorted(list(found_skills))

    @staticmethod
    def standardize_skill_name(skill):
        mapping = {
            "python": "Python",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "java": "Java",
            "c++": "C++",
            "c#": "C#",
            "ruby": "Ruby",
            "php": "PHP",
            "go": "Go",
            "rust": "Rust",
            "scala": "Scala",
            "kotlin": "Kotlin",
            "swift": "Swift",
            "r": "R",
            "matlab": "MATLAB",
            "bash": "Bash",
            "shell": "Shell Scripting",
            "react": "React",
            "angular": "Angular",
            "vue": "Vue.js",
            "next.js": "Next.js",
            "nextjs": "Next.js",
            "nuxt": "Nuxt.js",
            "svelte": "Svelte",
            "html": "HTML5",
            "css": "CSS3",
            "sass": "Sass",
            "bootstrap": "Bootstrap",
            "tailwind": "Tailwind CSS",
            "jquery": "jQuery",
            "webpack": "Webpack",
            "vite": "Vite",
            "django": "Django",
            "flask": "Flask",
            "fastapi": "FastAPI",
            "spring": "Spring",
            "spring boot": "Spring Boot",
            "express": "Express.js",
            "express.js": "Express.js",
            "nest.js": "Nest.js",
            "laravel": "Laravel",
            "asp.net": "ASP.NET",
            "rails": "Ruby on Rails",
            "node.js": "Node.js",
            "nodejs": "Node.js",
            "sql": "SQL",
            "mysql": "MySQL",
            "postgresql": "PostgreSQL",
            "postgres": "PostgreSQL",
            "sqlite": "SQLite",
            "mongodb": "MongoDB",
            "redis": "Redis",
            "elasticsearch": "Elasticsearch",
            "cassandra": "Cassandra",
            "dynamodb": "DynamoDB",
            "firebase": "Firebase",
            "oracle": "Oracle",
            "aws": "AWS",
            "azure": "Azure",
            "gcp": "Google Cloud Platform (GCP)",
            "docker": "Docker",
            "kubernetes": "Kubernetes",
            "jenkins": "Jenkins",
            "git": "Git",
            "github": "GitHub",
            "gitlab": "GitLab",
            "ci/cd": "CI/CD",
            "cicd": "CI/CD",
            "terraform": "Terraform",
            "ansible": "Ansible",
            "nginx": "Nginx",
            "linux": "Linux",
            "machine learning": "Machine Learning",
            "deep learning": "Deep Learning",
            "nlp": "Natural Language Processing (NLP)",
            "natural language processing": "Natural Language Processing (NLP)",
            "computer vision": "Computer Vision",
            "tensorflow": "TensorFlow",
            "pytorch": "PyTorch",
            "keras": "Keras",
            "scikit-learn": "Scikit-Learn",
            "sklearn": "Scikit-Learn",
            "pandas": "Pandas",
            "numpy": "NumPy",
            "scipy": "SciPy",
            "data science": "Data Science",
            "ai": "Artificial Intelligence (AI)",
            "artificial intelligence": "Artificial Intelligence (AI)",
            "excel": "Microsoft Excel",
            "tableau": "Tableau",
            "power bi": "Power BI",
            "looker": "Looker",
            "spark": "Apache Spark",
            "hadoop": "Hadoop",
            "etl": "ETL Pipelines",
            "data analytics": "Data Analytics",
            "data warehousing": "Data Warehousing",
            "data visualization": "Data Visualization",
            "agile": "Agile Methodology",
            "scrum": "Scrum",
            "project management": "Project Management",
            "communication": "Communication",
            "leadership": "Leadership",
            "problem solving": "Problem Solving",
            "teamwork": "Teamwork",
            "product management": "Product Management",
            "system design": "System Design",
            "microservices": "Microservices",
            "testing": "Software Testing",
            "unit testing": "Unit Testing",
            "qa": "Quality Assurance (QA)",
            "jest": "Jest",
            "cypress": "Cypress"
        }
        return mapping.get(skill, skill.title())
