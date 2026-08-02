import re


def generate_suggestions(missing_keywords, resume_text):
   
    if not missing_keywords:
        return []

    resume_lower = resume_text.lower() if resume_text else ""

    suggestions = []
    for keyword, score in missing_keywords:
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
        if re.search(pattern, resume_lower):
            continue  # already present as a whole word, skip

        suggestions.append(
            f"Consider adding '{keyword}' if you have practical experience."
        )

        if len(suggestions) == 5:
            break

    return suggestions