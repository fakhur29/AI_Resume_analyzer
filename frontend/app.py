import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.main import analyze_resume
from modules.generator import analyze_with_ai

import streamlit as st

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.title("📄 AI Resume Analyzer")

resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
job_description = st.text_area("Job Description", height=200, placeholder="Paste the job description here...")

if st.button("Analyze Resume"):
    if resume_file is None:
        st.warning("Please upload a resume.")
        st.stop()
    if not job_description.strip():
        st.warning("Please enter a job description.")
        st.stop()

    try:
        result = analyze_resume(resume_file, job_description)
        st.session_state["result"] = result
        st.session_state.pop("ai_result", None)
    except Exception as e:
        st.error(f"Error: {e}")


def show_categories(categories):
    for category, skills in categories.items():
        st.markdown(f"### {category}")
        col1, col2 = st.columns(2)

        with col1:
            st.write("✅ Matched")
            if skills.get("matched"):
                for skill in skills["matched"]:
                    st.write(f"• {skill}")
            else:
                st.write("None")

        with col2:
            st.write("❌ Missing")
            if skills.get("missing"):
                for skill in skills["missing"]:
                    st.write(f"• {skill}")
            else:
                st.write("None")


if "result" in st.session_state:
    result = st.session_state["result"]

    st.success("Analysis Completed Successfully!")

    if result.get("document_warning"):
        st.warning(f"⚠️ {result['document_warning']}")

    if result.get("domain"):
        st.info(f"🌐 Detected Domain: {result['domain']}")

    if result.get("schema_error"):
        st.error(f"Category generation failed: {result['schema_error']}")

    st.subheader("ATS Similarity Score")
    st.metric("Score", f"{result['ats_score']}%")

    st.subheader("Confidence Level")
    confidence = result["confidence"]
    level = confidence["level"]

    if level == "High":
        st.success(f"✅ {level} Confidence — {confidence['message']}")
    elif level == "Medium":
        st.info(f"ℹ️ {level} Confidence — {confidence['message']}")
    else:
        st.warning(f"⚠️ {level} Confidence — {confidence['message']}")

    if level == "Low":
        if st.button("✨ AI Enhance"):
            with st.spinner("Running AI-powered analysis..."):
                ai_result = analyze_with_ai(
                    result["raw_resume_text"],
                    result["raw_job_text"],
                    result["domain"],
                    result["skill_categories"]
                )
            st.session_state["ai_result"] = ai_result

    if "ai_result" in st.session_state:
        ai_result = st.session_state["ai_result"]

        if ai_result.get("error"):
            st.error(f"AI analysis failed: {ai_result['error']}")
        else:
            st.subheader("✨ AI-Enhanced Skill Analysis")
            show_categories(ai_result.get("categories", {}))

            st.subheader("✨ AI-Personalized Suggestions")
            if ai_result.get("suggestions"):
                for suggestion in ai_result["suggestions"]:
                    st.write(f"• {suggestion}")
            else:
                st.write("No suggestions available.")

    else:
        st.subheader("Skill Category Analysis")
        categories = result.get("skill_categories", {})
        if categories:
            show_categories(categories)
        else:
            st.write("No skill categories available.")

        st.subheader("Suggestions")
        if result["suggestions"]:
            for suggestion in result["suggestions"]:
                st.write(f"• {suggestion}")
        else:
            st.write("No suggestions available.")