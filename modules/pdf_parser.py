import fitz  # PyMuPDF
import re

class PDFParser:
    @staticmethod
    def extract_text(pdf_file_path_or_bytes):
        """Extracts text from a PDF file path or file-like object."""
        text = ""
        # If it is bytes (from streamlit uploaded file)
        if isinstance(pdf_file_path_or_bytes, bytes):
            doc = fitz.open(stream=pdf_file_path_or_bytes, filetype="pdf")
        else:
            doc = fitz.open(pdf_file_path_or_bytes)
            
        for page in doc:
            text += page.get_text()
        return text

    @staticmethod
    def parse_resume(pdf_file_path_or_bytes):
        """Parses a resume and returns a structured dictionary of information."""
        text = PDFParser.extract_text(pdf_file_path_or_bytes)
        
        email = PDFParser.extract_email(text)
        phone = PDFParser.extract_phone(text)
        name = PDFParser.extract_name(text)
        
        # Segment sections
        sections = PDFParser.segment_sections(text)
        
        parsed_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "education": sections.get("education", ""),
            "experience": sections.get("experience", ""),
            "projects": sections.get("projects", ""),
            "certifications": sections.get("certifications", ""),
            "full_text": text
        }
        return parsed_data

    @staticmethod
    def extract_email(text):
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""

    @staticmethod
    def extract_phone(text):
        # Matches various formats: +1-234-567-8901, (123) 456-7890, 1234567890, etc.
        phone_pattern = r'(?:(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,12})'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else ""

    @staticmethod
    def extract_name(text):
        # A simple fallback name extractor: Usually the first line contains the name
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return "Unknown"
        
        # Check first 3 lines, avoid lines containing emails, phone numbers, or links
        for line in lines[:3]:
            if "@" not in line and not any(char.isdigit() for char in line) and len(line.split()) <= 4:
                return line
        return lines[0]

    @staticmethod
    def segment_sections(text):
        # We search for headings and group text between them
        lines = text.split('\n')
        sections = {
            "education": "",
            "experience": "",
            "projects": "",
            "certifications": ""
        }
        
        # Define common heading aliases
        headings = {
            "education": ["education", "academic background", "qualification", "studies"],
            "experience": ["experience", "work history", "employment", "professional experience", "work experience"],
            "projects": ["projects", "personal projects", "key projects", "academic projects"],
            "certifications": ["certifications", "licenses", "courses", "certificates"]
        }
        
        current_section = None
        section_text = []
        
        for line in lines:
            cleaned_line = line.strip().lower()
            # Remove ending colon or spaces
            cleaned_line = re.sub(r'[:\s]+$', '', cleaned_line)
            
            # Detect section change
            found_header = False
            for sec, aliases in headings.items():
                if cleaned_line in aliases or any(alias in cleaned_line and len(cleaned_line) < 30 for alias in aliases):
                    if current_section:
                        sections[current_section] = "\n".join(section_text).strip()
                    current_section = sec
                    section_text = []
                    found_header = True
                    break
            
            if not found_header:
                if current_section:
                    section_text.append(line)
        
        # Capture last section
        if current_section:
            sections[current_section] = "\n".join(section_text).strip()
            
        return sections
