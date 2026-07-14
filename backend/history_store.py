import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")


def _load_all() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_all(records: list) -> None:
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def add_record(candidate_name: str, jd_text: str, result: dict) -> dict:
    """Save one match result and return the record that was stored."""
    records = _load_all()

    record = {
        "id": len(records) + 1,
        "candidate_name": candidate_name or "Unnamed Candidate",
        "jd_preview": (jd_text[:100] + "...") if len(jd_text) > 100 else jd_text,
        "match_score": result["match_score"],
        "recommendation": result["recommendation"],
        "matched_skills": result["matched_skills"],
        "missing_skills": result["missing_skills"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    records.append(record)
    _save_all(records)
    return record


def get_all_records() -> list:
    """Return all saved records, most recent first."""
    records = _load_all()
    return list(reversed(records))


def clear_history() -> None:
    _save_all([])
