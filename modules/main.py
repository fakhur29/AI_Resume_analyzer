from .parser import extract_resume_text, extract_job_text
from .keywords import compare_keywords
from .cleaner import clean_text
from .scorer import calculate_similarity
from .suggestions import generate_suggestions
from .schema_generator import generate_schema


def analyze_resume(resume_file, job_description):
    raw_resume_text = extract_resume_text(resume_file)
    raw_job_text = extract_job_text(job_description)

    cleaned_resume_text = clean_text(raw_resume_text)
    cleaned_job_text = clean_text(raw_job_text)

    schema = generate_schema(raw_job_text)
    domain = schema.get("domain", "General")
    categories = schema.get("categories", {})
    schema_error = schema.get("error")

    keyword_result = compare_keywords(cleaned_resume_text, cleaned_job_text, skill_categories=categories)

    cosine_score = calculate_similarity(cleaned_resume_text, cleaned_job_text)

    matched_count = len(keyword_result["matched"])
    missing_count = len(keyword_result["missing"])
    total_count = matched_count + missing_count
    skill_match_score = round((matched_count / total_count) * 100, 2) if total_count > 0 else 0.0

    ats_score = round((0.6 * skill_match_score) + (0.4 * cosine_score), 2)

    suggestions = generate_suggestions(keyword_result["missing"], raw_resume_text)

    if matched_count >= 10 and ats_score >= 60:
        confidence = {"level": "High", "message": "Offline analysis is reliable."}
    elif matched_count >= 5 or ats_score >= 40:
        confidence = {"level": "Medium", "message": "Offline analysis found a reasonable number of relevant skills."}
    else:
        confidence = {
            "level": "Low",
            "message": "Only a limited number of relevant skills were detected. AI-enhanced analysis may improve accuracy."
        }

    RESUME_SECTION_HEADERS = [
        "experience", "education", "skills", "objective", "summary",
        "projects", "certification", "certifications", "contact",
        "profile", "qualification", "qualifications", "work history",
        "employment", "achievements"
    ]
    resume_text_lower = raw_resume_text.lower()
    headers_found = sum(1 for h in RESUME_SECTION_HEADERS if h in resume_text_lower)

    document_warning = None
    if headers_found < 2:
        document_warning = (
            "This document doesn't look like a resume — no recognizable resume "
            "sections were found in it. Please confirm the correct file was uploaded."
        )

    return {
        "ats_score": ats_score,
        "matched_keywords": keyword_result["matched"],
        "missing_keywords": keyword_result["missing"],
        "skill_categories": keyword_result["categories"],
        "suggestions": suggestions,
        "confidence": confidence,
        "raw_resume_text": raw_resume_text,
        "raw_job_text": raw_job_text,
        "document_warning": document_warning,
        "domain": domain,
        "schema_error": schema_error
    }