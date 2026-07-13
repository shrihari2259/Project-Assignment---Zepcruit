# Matchbook — Candidate ↔ Job Match System

An AI/ML assignment submission: paste any Job Description and any Candidate CV,
and get a Match Score, Matched Skills, Missing Skills, and a hiring
recommendation — computed live, no hardcoding.

```
job-match-system/
├── backend/
│   ├── app.py            Flask server: serves the frontend + JSON API
│   ├── matcher.py         Core NLP/ML pipeline (cleaning, skills, scoring)
│   ├── skills_data.py     Skill taxonomy (canonical skill -> synonyms)
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js          Vanilla HTML/CSS/JS — no build step, no framework
└── README.md
```

## How it works (the actual "AI/ML")

1. **Clean** — lowercase, strip punctuation, remove stopwords (`matcher.clean_text`).
2. **Extract skills** — regex-match JD and CV text against a curated skills
   taxonomy (`skills_data.py`) that maps synonyms to one canonical skill
   (e.g. "ML", "machine learning" → `Machine Learning`). This gives you the
   Matched / Missing / Bonus skill lists.
3. **Semantic similarity** — the *whole* JD and CV text (not just skills) are
   vectorized with **TF-IDF** and compared with **cosine similarity**
   (`scikit-learn`). This captures context and phrasing overlap that a pure
   keyword match would miss.
4. **Score fusion** — `final_score = 0.7 × skill_coverage + 0.3 × text_similarity`,
   rounded to an integer 0–100. Skill coverage is weighted higher because for
   hiring, "does the JD's required skill exist on the CV" matters more than
   general wording similarity.
5. **Recommendation bands**:
   - 85–100 → Strong Match
   - 70–84 → Good Match
   - 50–69 → Moderate Match
   - 0–49 → Low Match

Every run is JD-agnostic — paste a different JD and CV each time and the
system re-computes everything from scratch, exactly like the assignment asks.

## Running it

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in your browser. The Flask server serves
the plain HTML/CSS/JS frontend directly, so there's nothing else to start.

- Paste a JD on the left, a CV on the right (or upload a `.txt`/`.pdf`/`.docx`
  resume file), and click **Run the match**.
- The report shows the score dial, the skill-coverage vs text-similarity
  breakdown, and three chip lists: matched, missing, and "bonus" skills the
  candidate has that the JD didn't ask for.

## Tips to improve this further (for the interview / take it further)

**Make the NLP smarter**
- Swap TF-IDF + cosine similarity for **sentence embeddings**
  (`sentence-transformers`, e.g. `all-MiniLM-L6-v2`) and cosine similarity on
  the embeddings. This catches semantic matches TF-IDF misses — e.g. "led a
  team of 5 engineers" matching a JD's "leadership experience" even with zero
  shared keywords.
- Replace the hand-written skill taxonomy with a trained **NER model**
  (spaCy `en_core_web_trf` fine-tuned, or a skills-extraction library like
  `skillNer`) so you're not limited to a fixed list — this matters a lot once
  you're hiring across many different roles, not just tech.
- Weight skills by how many times / how prominently they appear in the JD
  ("must-have" vs "nice-to-have" sections) rather than treating every skill
  in the JD equally.
- Add **experience-level matching**: extract years-of-experience from both
  documents and penalize/boost the score if the CV is well under or over
  what the JD asks for.

**Make it production-ready**
- Add authentication and per-recruiter accounts if this becomes a real
  internal tool for the hiring team.
- Store JD/CV pairs and results in a database (Postgres) instead of computing
  in-memory each time, so recruiters can revisit past scans and build a
  dataset for future model training.
- Add a **feedback loop**: let recruiters mark whether a "Strong Match" the
  system predicted actually got hired/performed well, and use that signal to
  retrain scoring weights over time (this is where it becomes genuinely
  "learning", not just rule-based NLP).
- Batch mode: let a recruiter upload one JD and 50 CVs at once, and return a
  ranked shortlist instead of one-at-a-time scoring — this is the realistic
  use case for a company that does student/campus hiring at volume.
- Swap the Flask dev server for a production WSGI server (gunicorn) and add
  input size limits / rate limiting before exposing this publicly.

**Make the evaluation more rigorous**
- Right now this is a heuristic score (skill coverage + doc similarity). For
  an ML-flavored version, you could label ~200 real (JD, CV) pairs as
  hire/no-hire and train a lightweight classifier (logistic regression /
  gradient boosting) on features like skill overlap %, years of experience
  delta, and embedding similarity — then you can say "final_score" comes from
  an actual trained model rather than fixed weights.
- Add a short write-up (which this README doubles as) explaining *why* you
  chose TF-IDF/skill-taxonomy over a heavier model — interviewers usually care
  as much about your reasoning on trade-offs (speed vs accuracy, no-GPU
  friendliness, explainability of "why this candidate scored 75%") as the
  final score itself. Explainability is a genuine selling point here: a
  recruiter can see *exactly* why a candidate scored 75% (which skills
  matched/missing), which a black-box embedding-only model would not give
  you as clearly.

## Notes for your submission

- Everything runs locally, no API keys or paid services required — good for
  an assignment reviewer to clone and run in under a minute.
- The skill taxonomy in `skills_data.py` is intentionally small and focused
  on tech/data roles to match the sample I/O in the assignment brief (Python,
  SQL, Pandas, NLP, TensorFlow). Extend the dict with more skills/domains as
  needed (marketing, sales, finance, etc.) if you want to demo it beyond
  tech roles.
