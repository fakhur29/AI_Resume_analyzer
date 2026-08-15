import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

import streamlit as st
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def generate_schema(job_text):
    if not GEMINI_API_KEY:
        return {"domain": "General", "categories": {}, "error": "GEMINI_API_KEY not found"}

    prompt = f"""
You are a professional ATS skill taxonomy generator.

Analyze this job description and:
1. Identify the professional domain (e.g. Software Engineering, Mechanical Engineering, Healthcare, Finance, Marketing, Civil Engineering, etc. - choose the single best label, not a fixed list).
2. Create relevant skill categories for that domain.

Rules:
- Categories must match the professional field.
- Do not use fixed IT categories unless the job is actually IT-related.
- Each category must contain only exact, atomic skill names taken directly from the job description.
- Do NOT rename, expand, summarize, or generalize skills.
- Do NOT append generic filler words to a skill name, such as "Skills", "Experience", "Concepts", "Development", "Practices", "Operations", "Knowledge of", or similar. Return only the core skill itself.
- If a skill contains a slash (e.g. "Permit to Work/Receiver"), treat it as ONE single atomic skill exactly as written - do not split it into separate skills.
- For example, if the text says "teamwork skills", return "Teamwork", not "Teamwork Skills".
- If the text says "communication and representation", return them as two separate skills: "Communication" and "Representation".
- Remove brackets such as "(EDA)" and keep the base skill name only.
- If the job description says "AutoML", return "AutoML".
- If it says "Exploratory Data Analysis (EDA)", return "Exploratory Data Analysis".
- Return only valid JSON, no markdown fences.

Format:

{{
  "domain": "Domain Name",
  "categories": {{
    "Category Name": [
      "skill1",
      "skill2"
    ]
  }}
}}

Job Description:
{job_text}
"""

    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.1)
        )
        output = response.text.strip()
        output = output.replace("```json", "").replace("```", "").strip()
        result = json.loads(output)
        return {
            "domain": result.get("domain", "General"),
            "categories": result.get("categories", {})
        }
    except Exception as e:
        return {"domain": "General", "categories": {}, "error": str(e)}