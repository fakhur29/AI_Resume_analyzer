import re
from .skills_data import ALIASES
from .cleaner import clean_text

SUFFIXES = ["ment", "ing", "ed", "es", "s"]

REVERSE_ALIASES = {}
for _alias_key, _canonical in ALIASES.items():
    REVERSE_ALIASES.setdefault(_canonical, []).append(_alias_key)


def _strip_suffix(word):
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[:-len(suffix)]
    return word


def _normalize(skill):
    return ALIASES.get(skill, skill)


def _phrase_present(phrase, normalized_text, compact_text):
    words = phrase.split()
    normalized_words = [_strip_suffix(w) for w in words]
    normalized_phrase = " ".join(normalized_words)
    compact_phrase = "".join(normalized_words)

    if re.search(r"\b" + re.escape(normalized_phrase) + r"\b", normalized_text):
        return True
    if len(compact_phrase) >= 6 and compact_phrase in compact_text:
        return True
    return False


def _find_skills_in_text(text, skills, top_n=None):
    if not text or not text.strip() or not skills:
        return []

    text_words = text.split()
    normalized_text_words = [_strip_suffix(w) for w in text_words]
    normalized_text = " ".join(normalized_text_words)
    compact_text = "".join(normalized_text_words)

    counts = {}
    for skill in skills:
        canonical = _normalize(skill)
        forms_to_try = [skill, canonical] + REVERSE_ALIASES.get(canonical, [])
        forms_to_try = list(dict.fromkeys(forms_to_try))

        if any(_phrase_present(form, normalized_text, compact_text) for form in forms_to_try):
            counts[canonical] = counts.get(canonical, 0) + 1

    found = list(counts.items())
    found.sort(key=lambda x: x[1], reverse=True)

    if top_n:
        return found[:top_n]
    return found


def extract_keywords(text, skills, top_n=20):
    return _find_skills_in_text(text, skills, top_n=top_n)


def compare_keywords(resume, job, skill_categories, top_n=20):
    if not resume or not resume.strip() or not job or not job.strip() or not skill_categories:
        return {"matched": [], "missing": [], "categories": {}}

    all_skills = set()
    active_categories = {}

    for category, skills in skill_categories.items():
        normalized_skills = []
        for skill in skills:
            normalized = clean_text(skill)
            normalized = _normalize(normalized)
            normalized_skills.append(normalized)
            all_skills.add(normalized)
        active_categories[category] = normalized_skills

    job_skills = _find_skills_in_text(job, all_skills, top_n=top_n)
    resume_skill_set = {skill for skill, _ in _find_skills_in_text(resume, all_skills)}

    matched = []
    missing = []
    category_result = {category: {"matched": [], "missing": []} for category in active_categories}

    for skill, count in job_skills:
        if skill in resume_skill_set:
            matched.append((skill, count))
            status = "matched"
        else:
            missing.append((skill, count))
            status = "missing"

        for category, skills in active_categories.items():
            if skill in skills:
                category_result[category][status].append(skill)

    return {"matched": matched, "missing": missing, "categories": category_result}