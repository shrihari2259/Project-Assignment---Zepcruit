import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skills_data import SKILL_TAXONOMY


STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be because
been before being below between both but by can't cannot could couldn't did
didn't do does doesn't doing don't down during each few for from further had
hadn't has hasn't have haven't having he he'd he'll he's her here here's hers
herself him himself his how how's i i'd i'll i'm i've if in into is isn't it
it's its itself let's me more most mustn't my myself no nor not of off on once
only or other ought our ours ourselves out over own same shan't she she'd
she'll she's should shouldn't so some such than that that's the their theirs
them themselves then there there's these they they'd they'll they're they've
this those through to too under until up very was wasn't we we'd we'll we're
we've were weren't what what's when when's where where's which while who
who's whom why why's with won't would wouldn't you you'd you'll you're you've
your yours yourself yourselves
""".split())


def clean_text(text: str) -> str:
    
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\#\./\s]", " ", text)  
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS]
    return " ".join(tokens)


def extract_skills(raw_text: str) -> set:

    if not raw_text:
        return set()
    text = " " + raw_text.lower() + " "
    text = re.sub(r"[^a-z0-9\+\#\./\s]", " ", text)

    found = set()
    for canonical, synonyms in SKILL_TAXONOMY.items():
        for syn in synonyms:
            pattern = r"(?<![a-z0-9])" + re.escape(syn.strip()) + r"(?![a-z0-9])"
            if re.search(pattern, text):
                found.add(canonical)
                break
    return found


def text_similarity(jd_clean: str, cv_clean: str) -> float:
   
    if not jd_clean.strip() or not cv_clean.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([jd_clean, cv_clean])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return float(sim)
    except ValueError:
       
        return 0.0


def recommendation_for(score: float) -> str:
    if score >= 85:
        return "Strong Match"
    elif score >= 70:
        return "Good Match"
    elif score >= 50:
        return "Moderate Match"
    else:
        return "Low Match"


def match(jd_text: str, cv_text: str) -> dict:
    
    jd_clean = clean_text(jd_text)
    cv_clean = clean_text(cv_text)

    jd_skills = extract_skills(jd_text)
    cv_skills = extract_skills(cv_text)

    matched_skills = sorted(jd_skills & cv_skills)
    missing_skills = sorted(jd_skills - cv_skills)
    extra_candidate_skills = sorted(cv_skills - jd_skills)

   
    if jd_skills:
        skill_score = len(matched_skills) / len(jd_skills) * 100
    else:
        skill_score = 0.0

    
    sim_score = text_similarity(jd_clean, cv_clean) * 100

    
    final_score = round(0.7 * skill_score + 0.3 * sim_score)
    final_score = max(0, min(100, final_score))

    return {
        "match_score": final_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_candidate_skills": extra_candidate_skills,
        "recommendation": recommendation_for(final_score),
        "breakdown": {
            "skill_coverage_score": round(skill_score, 1),
            "text_similarity_score": round(sim_score, 1),
        },
    }
