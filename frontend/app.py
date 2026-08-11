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

if st.button("Analyze Resume",type="primary"):
    if resume_file is None:
        st.warning("Please upload a resume.")
        st.stop()
    if not job_description.strip():
        st.warning("Please enter a job description.")
        st.stop()

    try:
        with st.spinner("Analyzing resume and detecting relevant skills..."):
            result = analyze_resume(resume_file, job_description)
        st.session_state["result"] = result
        st.session_state.pop("ai_result", None)
    except ValueError as e:
        st.error(f"Invalid input: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Something went wrong while analyzing the resume: {e}")
        st.stop()


def show_categories(categories):
    if not categories:
        st.write("No skill categories available.")
        return

    for category, skills in categories.items():
        st.markdown(f"### {category}")
        col1, col2 = st.columns(2)

        with col1:
            st.write("✅ Matched")
            matched = skills.get("matched") if isinstance(skills, dict) else None
            if matched:
                for skill in matched:
                    st.write(f"• {skill}")
            else:
                st.write("None")

        with col2:
            st.write("❌ Missing")
            missing = skills.get("missing") if isinstance(skills, dict) else None
            if missing:
                for skill in missing:
                    st.write(f"• {skill}")
            else:
                st.write("None")


def count_matched_missing(categories):
    matched_count = 0
    missing_count = 0
    for skills in categories.values():
        if isinstance(skills, dict):
            matched_count += len(skills.get("matched") or [])
            missing_count += len(skills.get("missing") or [])
    return matched_count, missing_count

st.divider()
if "result" in st.session_state:
    result = st.session_state["result"]

    st.success("Analysis Completed Successfully!")

    if result.get("document_warning"):
        st.warning(f"⚠️ {result['document_warning']}")

    if result.get("domain"):
        st.info(f"🌐 Detected Domain: {result['domain']}")

    if result.get("schema_error"):
        st.warning(
            "⚠️ AI-based category analysis could not be completed "
            f"({result['schema_error']}). Showing the overall ATS similarity "
            "score below; detailed skill matching is unavailable for this run."
        )

    st.subheader("ATS Similarity Score")
    score = result.get("ats_score")
    if score is not None:
        st.metric("Score", f"{score}%")
        st.progress(min(int(score), 100) / 100)
        if score >= 70:
            st.success("Strong match with this job description.")
        elif score >= 40:
            st.info("Moderate match with this job description.")
        else:
            st.warning("Low match with this job description.")
    else:
        st.write("Score unavailable.")

    categories_for_summary = result.get("skill_categories", {})
    matched_count, missing_count = count_matched_missing(categories_for_summary)
    if matched_count or missing_count:
        st.write(f"**{matched_count} skills matched** · **{missing_count} skills missing**")

    st.subheader("Confidence Level")
    confidence = result.get("confidence") or {}
    level = confidence.get("level", "Low")
    message = confidence.get("message", "")

    if level == "High":
        st.success(f"✅ {level} Confidence — {message}")
    elif level == "Medium":
        st.info(f"ℹ️ {level} Confidence — {message}")
    else:
        st.warning(f"⚠️ {level} Confidence — {message}")

    if level == "Low":
        st.divider()
        if st.button("✨ AI Enhance",type="primary"):
            try:
                with st.spinner("Running AI-powered analysis..."):
                    ai_result = analyze_with_ai(
                        result.get("raw_resume_text", ""),
                        result.get("raw_job_text", ""),
                        result.get("domain", "General"),
                        result.get("skill_categories", {})
                    )
                st.session_state["ai_result"] = ai_result
            except Exception as e:
                st.session_state["ai_result"] = {"error": str(e)}

    if "ai_result" in st.session_state:
        ai_result = st.session_state["ai_result"] or {}

        if ai_result.get("error"):
            st.error(f"AI analysis failed: {ai_result['error']}")
        else:
            ai_categories = ai_result.get("categories", {})
            ai_matched, ai_missing = count_matched_missing(ai_categories)
            if ai_matched or ai_missing:
                st.write(f"**{ai_matched} skills matched** · **{ai_missing} skills missing**")

            st.subheader("✨ AI-Enhanced Skill Analysis")
            show_categories(ai_categories)

            st.subheader("✨ AI-Personalized Suggestions")
            suggestions = ai_result.get("suggestions")
            if suggestions:
                for suggestion in suggestions:
                    st.write(f"• {suggestion}")
            else:
                st.write("No suggestions available.")

    else:
        st.subheader("Skill Category Analysis")
        categories = result.get("skill_categories", {})
        show_categories(categories)

        st.subheader("Suggestions")
        suggestions = result.get("suggestions")
        if suggestions:
            for suggestion in suggestions:
                st.write(f"• {suggestion}")
        else:
            st.write("No suggestions available.")
    st.divider()
    left_co, cent_co, last_co = st.columns((2,1,2))
    with cent_co:
         if st.button("🔄 Analyze Another Resume",type="primary"):
            st.session_state.pop("result", None)
            st.session_state.pop("ai_result", None)
            st.rerun()