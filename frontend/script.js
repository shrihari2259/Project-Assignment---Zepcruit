const jdInput = document.getElementById("jd-input");
const cvInput = document.getElementById("cv-input");
const jdCount = document.getElementById("jd-count");
const cvCount = document.getElementById("cv-count");
const cvFile = document.getElementById("cv-file");
const candidateNameInput = document.getElementById("candidate-name");
const runBtn = document.getElementById("run-btn");
const runError = document.getElementById("run-error");
const report = document.getElementById("report");
const historyBody = document.getElementById("history-body");
const historyEmpty = document.getElementById("history-empty");
const clearHistoryBtn = document.getElementById("clear-history-btn");

function updateCounts() {
  jdCount.textContent = jdInput.value.length + " characters";
  cvCount.textContent = cvInput.value.length + " characters";
}

jdInput.addEventListener("input", updateCounts);
cvInput.addEventListener("input", updateCounts);
updateCounts();

cvFile.addEventListener("change", async function () {
  const chosenFile = cvFile.files[0];
  if (!chosenFile) {
    return;
  }

  runError.textContent = "";

  const formData = new FormData();
  formData.append("file", chosenFile);

  try {
    const response = await fetch("/api/extract-file", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (!response.ok) {
      runError.textContent = result.error || "Could not read that file.";
      return;
    }

    cvInput.value = result.text;
    updateCounts();

  } catch (error) {
    runError.textContent = "Upload failed. Is the backend running?";
  }
});

runBtn.addEventListener("click", async function () {
  const jdText = jdInput.value.trim();
  const cvText = cvInput.value.trim();

  runError.textContent = "";

  if (jdText === "" || cvText === "") {
    runError.textContent = "Please paste both a job description and a resume.";
    return;
  }

  runBtn.disabled = true;
  runBtn.textContent = "Matching...";
  report.hidden = true;

  try {
    const candidateName = candidateNameInput.value.trim();

    const response = await fetch("/api/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd: jdText, cv: cvText, candidate_name: candidateName }),
    });

    const result = await response.json();

    if (!response.ok) {
      runError.textContent = result.error || "Something went wrong.";
      return;
    }

    showResult(result);
    loadHistory();

  } catch (error) {
    runError.textContent = "Could not reach the backend. Is app.py running?";

  } finally {
    runBtn.disabled = false;
    runBtn.textContent = "Run the match";
  }
});

function showResult(data) {
  report.hidden = false;

  document.getElementById("dial-number").textContent = data.match_score;
  document.getElementById("verdict").textContent = data.recommendation;

  let color = "#2fbf9f";
  if (data.match_score < 50) {
    color = "#ff6b57";
  } else if (data.match_score < 70) {
    color = "#e8a33d";
  }
  document.getElementById("verdict").style.color = color;

  document.getElementById("bar-skill").style.width = data.breakdown.skill_coverage_score + "%";
  document.getElementById("bar-text").style.width = data.breakdown.text_similarity_score + "%";
  document.getElementById("val-skill").textContent = data.breakdown.skill_coverage_score + "%";
  document.getElementById("val-text").textContent = data.breakdown.text_similarity_score + "%";

  fillSkillList("matched-skills", data.matched_skills, "No overlapping skills found.");
  fillSkillList("missing-skills", data.missing_skills, "Nothing missing.");
  fillSkillList("extra-skills", data.extra_candidate_skills, "No extra skills.");

  document.getElementById("matched-count").textContent = data.matched_skills.length;
  document.getElementById("missing-count").textContent = data.missing_skills.length;
  document.getElementById("extra-count").textContent = data.extra_candidate_skills.length;

  report.scrollIntoView({ behavior: "smooth" });
}

function fillSkillList(containerId, skills, emptyMessage) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  if (!skills || skills.length === 0) {
    const emptyNote = document.createElement("span");
    emptyNote.className = "empty-note";
    emptyNote.textContent = emptyMessage;
    container.appendChild(emptyNote);
    return;
  }

  for (let i = 0; i < skills.length; i++) {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = skills[i];
    container.appendChild(chip);
  }
}

function recommendationClass(recommendation) {
  if (recommendation === "Strong Match") return "tag-strong";
  if (recommendation === "Good Match") return "tag-good";
  if (recommendation === "Moderate Match") return "tag-moderate";
  return "tag-low";
}

async function loadHistory() {
  try {
    const response = await fetch("/api/history");
    const records = await response.json();

    historyBody.innerHTML = "";

    if (!records || records.length === 0) {
      historyEmpty.hidden = false;
      return;
    }

    historyEmpty.hidden = true;

    for (let i = 0; i < records.length; i++) {
      const r = records[i];
      const row = document.createElement("tr");

      row.innerHTML =
        "<td>" + r.candidate_name + "</td>" +
        "<td class='history-score'>" + r.match_score + "%</td>" +
        "<td class='" + recommendationClass(r.recommendation) + "'>" + r.recommendation + "</td>" +
        "<td>" + r.timestamp + "</td>";

      historyBody.appendChild(row);
    }

  } catch (error) {
    historyEmpty.hidden = false;
    historyEmpty.textContent = "Could not load history.";
  }
}

clearHistoryBtn.addEventListener("click", async function () {
  try {
    await fetch("/api/history/clear", { method: "POST" });
    loadHistory();
  } catch (error) {
    runError.textContent = "Could not clear history.";
  }
});

loadHistory();
