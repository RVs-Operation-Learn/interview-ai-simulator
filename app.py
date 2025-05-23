
from flask import Flask, render_template, request, redirect, url_for, session
from interview_bot import build_system_prompt, get_interview_question, get_feedback_on_answer
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")  # Keep this secure!

# --- Routes ---

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get interview config from form
        role = request.form.get("role")
        level = request.form.get("level")
        difficulty = request.form.get("difficulty")

        # Store config and state in session
        session.clear()
        session["role"] = role
        session["level"] = level
        session["difficulty"] = difficulty
        session["round"] = 1
        session["total_score"] = 0.0
        session["history"] = [
            {"role": "system", "content": build_system_prompt(role, level, difficulty)}
        ]

        return redirect(url_for("interview"))

    return render_template("index.html")

@app.route("/interview", methods=["GET", "POST"])
def interview():
    history = session.get("history", [])
    round_number = session.get("round", 1)

    if request.method == "POST":
        user_answer = request.form.get("answer")
        feedback, score, updated_history = get_feedback_on_answer(history, user_answer)

        session["history"] = updated_history
        session["feedback"] = feedback
        session["round"] = round_number + 1
        session["total_score"] = float(session.get("total_score", 0.0)) + float(score or 0.0)

        if session["round"] > 3:
            average_score = round(float(session.get("total_score", 0.0)) / 3, 2)
            return render_template("end.html", history=updated_history, score=average_score)
        return redirect(url_for("interview"))

    # First round or refresh
    if round_number <= 3 and not any(msg["role"] == "assistant" for msg in history[-2:]):
        question = get_interview_question(history)
        history.append({"role": "assistant", "content": question})
        session["history"] = history
        session["current_question"] = question
    else:
        question = session.get("current_question", history[-1]["content"])

    return render_template(
        "interview.html",
        round_number=round_number,
        question=question,
        feedback=session.pop("feedback", None)
    )


@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)