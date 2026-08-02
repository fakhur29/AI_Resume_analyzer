import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def analyze_with_ai(resume_text, job_text, domain, categories):
    if not GEMINI_API_KEY:
        return {"categories": {}, "suggestions": [], "error": "GEMINI_API_KEY not found in .env"}

    categories_json = json.dumps(categories)

    prompt = f"""
You are an ATS (Applicant Tracking System) analyzer performing a deeper,
semantic re-check of a resume against a job description.

Domain: {domain}

Use exactly these categories and skills (do not add or remove any):
{categories_json}

Your tasks:
1. For each category and each skill listed, determine if the resume
   demonstrates that skill - not just literal keyword presence, but also
   equivalent phrasing, related projects, or clearly implied experience.
2. Put each skill into "matched" or "missing" for its category.
3. For every missing skill, write one short, personalized, one-line
   actionable suggestion referencing that specific skill by name.

The "suggestions" list must have exactly one entry per missing skill
across all categories, in the same order the missing skills appear.

Return ONLY valid JSON, no markdown fences, in exactly this structure:

{{
  "categories": {{
    "Category Name": {{
      "matched": ["skill1"],
      "missing": ["skill2"]
    }}
  }},
  "suggestions": [
    "personalized suggestion for skill2"
  ]
}}

Resume:
{resume_text}

Job Description:
{job_text}
"""

    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content(prompt)
        raw_output = response.text.strip()
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw_output)
        return {
            "categories": result.get("categories", {}),
            "suggestions": result.get("suggestions", [])
        }
    except Exception as e:
        return {"categories": {}, "suggestions": [], "error": str(e)}