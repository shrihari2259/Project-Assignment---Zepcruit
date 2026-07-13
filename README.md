# Job Match System

This is a small project I built for an AI/ML assignment.

You paste a Job Description and a Resume, and it tells you:
- How much they match (in %)
- Which skills matched
- Which skills are missing
- A final recommendation (Strong Match / Good Match / Moderate Match / Low Match)

It also keeps a history of every match you run, so you can see past candidates and their scores.

## What I used

- Python + Flask for the backend
- Plain HTML, CSS, and JavaScript for the frontend (no React or anything fancy)
- scikit-learn for comparing the text (TF-IDF + cosine similarity)

## Folder structure

```
job-match-system/
  backend/
    app.py            -> runs the server
    matcher.py         -> the actual matching logic
    skills_data.py      -> list of skills it looks for
    history_store.py    -> saves past matches
    requirements.txt
  frontend/
    index.html
    style.css
    script.js
  README.md
```

## How to run it

1. Open a terminal and go into the backend folder:
```
cd job-match-system/backend
```

2. Install the required packages:
```
pip install -r requirements.txt
```

3. Run the app:
```
python app.py
```

4. Open your browser and go to:
```
http://127.0.0.1:5000
```

That's it. The same server runs both the frontend and the backend, so there's nothing else to start.

To stop it, go back to the terminal and press `Ctrl + C`.

## How to use it

1. Paste the job description on the left side.
2. Paste the resume on the right side, or upload a file (.txt, .pdf, .docx) instead.
3. You can also type the candidate's name (optional).
4. Click "Run the Match".
5. It shows the score, matched skills, missing skills, and a recommendation.
6. Below that, there's a history table showing every match you've run so far.


**PDF upload gives empty text**
This happens if the PDF is a scanned image with no actual text in it. Works fine for normal resumes made in Word or Google Docs.

## How the matching works (in simple terms)

1. It cleans up the text (removes punctuation, common words like "the", "and", etc.)
2. It checks both the JD and resume against a list of skills (like Python, SQL, React, etc.) and finds which ones match.
3. It also compares the overall text using TF-IDF, which is a way to check how similar two pieces of text are.
4. It combines both of these into one score out of 100.
5. Based on the score, it gives a recommendation:
   - 85 and above: Strong Match
   - 70-84: Good Match
   - 50-69: Moderate Match
   - Below 50: Low Match

## Notes

- The match history is saved in a file called `history.json` inside the backend folder. If you want to clear it, just delete that file (or use the "Clear History" button on the page).
- This project uses a fixed list of skills and basic text comparison, not a trained AI model. I kept it this way so the results are easy to explain — you can see exactly why a candidate got the score they did.

## What I'd add if I had more time

- Compare resumes and JDs by meaning, not just matching words (using sentence embeddings)
- Use a real database instead of a JSON file for history
- Let a recruiter upload one JD and multiple resumes at once and get a ranked list
- Auto-detect skills instead of relying on a fixed list
