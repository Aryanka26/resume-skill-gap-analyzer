from flask import Flask, render_template, request
import os
from utils.database import init_db, save_analysis, fetch_analysis_history, generate_resume_hash

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
        user_type = request.form["user_type"]
        role = request.form["role"]
        files = request.files.getlist("resume")

        # Load job description once
        with open(f"data/job_descriptions/{role}.txt", "r") as f:
            job_text = clean_text(f.read())

        results = []

        for file in files:
            if file.filename == "":
                continue

            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            resume_text = clean_text(extract_text_from_pdf(file_path))

            match_score = calculate_match_score(resume_text, job_text)
            present, missing = analyze_skill_gap(resume_text, ROLE_SKILLS[role])

            resume_hash = generate_resume_hash(resume_text)
            save_analysis(user_type, role, match_score, present, missing, resume_text)

            results.append({
                "resume_hash": resume_hash[:10],
                "score": match_score,
                "present": present,
                "missing": missing
            })

        # 🔹 Applicant: only one resume expected
        if user_type == "applicant":
            result = results[0]
            return render_template(
                "result.html",
                score=result["score"],
                present=result["present"],
                missing=result["missing"],
                role=role.upper()
            )

        # 🔹 Recruiter: rank multiple resumes
        ranked_results = sorted(results, key=lambda x: x["score"], reverse=True)

        return render_template(
            "recruiter_result.html",
            results=ranked_results,
            role=role.upper()
        )

    return render_template("index.html")


@app.route("/history")
def history():
    history_data = fetch_analysis_history()
    return render_template("history.html", history=history_data)

if __name__ == "__main__":
    app.run(debug=True)
