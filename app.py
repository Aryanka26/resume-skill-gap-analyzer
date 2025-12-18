from flask import Flask, render_template, request
import os
from utils.database import init_db, save_analysis, fetch_analysis_history

from utils.text_extractor import extract_text_from_pdf, clean_text
from model.matcher import calculate_match_score
from model.skill_gap import analyze_skill_gap
from model.skills import ROLE_SKILLS

app = Flask(__name__)

init_db()

UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        role = request.form["role"]
        file = request.files["resume"]
        user_type = request.form["user_type"]

        if file.filename == "":
            return "No file uploaded"

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        resume_text = extract_text_from_pdf(file_path)
        resume_text = clean_text(resume_text)

        with open(f"data/job_descriptions/{role}.txt", "r") as f:
            job_text = f.read()

        job_text = clean_text(job_text)

        match_score = calculate_match_score(resume_text, job_text)
        present, missing = analyze_skill_gap(resume_text, ROLE_SKILLS[role])

        save_analysis(user_type, role, match_score, present, missing, resume_text)

        return render_template(
            "result.html",
            score=match_score,
            present=present,
            missing=missing,
            role=role.upper()
        )

    return render_template("index.html")


@app.route("/history")
def history():
    history_data = fetch_analysis_history()
    return render_template("history.html", history=history_data)

if __name__ == "__main__":
    app.run(debug=True)
