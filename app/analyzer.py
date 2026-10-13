import re
from typing import Dict, List

SKILL_ALIASES: Dict[str, List[str]] = {
    "Python": ["python"],
    "Java": ["java"],
    "FastAPI": ["fastapi"],
    "React": ["react", "react.js"],
    "SQL": ["sql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "Docker": ["docker"],
    "Machine Learning": ["machine learning", "ml"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "REST APIs": ["rest api", "rest apis"],
    "AWS": ["aws", "amazon web services"],
    "Git": ["git", "github"],
}

NEGATION_WORDS = {
    "not",
    "no",
    "never",
    "without",
    "lack",
    "lacks",
    "lacking",
    "isnt",
    "isn't",
    "arent",
    "aren't",
    "wasnt",
    "wasn't",
    "dont",
    "don't",
    "doesnt",
    "doesn't",
    "cant",
    "can't",
}


def _build_boundary_pattern(alias: str) -> str:
    escaped = re.escape(alias)
    return rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])"


def _is_negated_context(sentence: str, match_start: int) -> bool:
    context = sentence[:match_start].lower()
    recent_tokens = re.findall(r"[a-z0-9]+", context)
    return any(token in NEGATION_WORDS for token in recent_tokens[-6:])


def analyze_job_description(text: str) -> dict:
    if not text or not isinstance(text, str):
        return {"detected_skills": [], "skill_count": 0}

    normalized = text.strip()
    if not normalized:
        return {"detected_skills": [], "skill_count": 0}

    lowered = normalized.lower()
    sentences = re.split(r"(?<=[.!?])\s+", lowered)
    detected = set()

    for skill_name, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            pattern = re.compile(_build_boundary_pattern(alias.lower()))
            for sentence in sentences:
                for match in pattern.finditer(sentence):
                    if _is_negated_context(sentence, match.start()):
                        continue
                    detected.add(skill_name)
                    break
                if skill_name in detected:
                    break
            if skill_name in detected:
                break

    ordered_skills = sorted(detected)
    return {"detected_skills": ordered_skills, "skill_count": len(ordered_skills)}
