import pdfplumber
from docx import Document


def extract_resume_text(file):
    
    filename = file.name.lower()

    if filename.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()

    elif filename.endswith(".docx"):
        doc = Document(file)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        return text.strip()

    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")
    




def extract_job_text(text_input):
    
    if not text_input or not text_input.strip():
        raise ValueError("Job description text cannot be empty.")

    return text_input.strip()