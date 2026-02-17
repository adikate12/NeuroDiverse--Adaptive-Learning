from flask import (
    Flask, render_template, request, redirect,
    url_for, session, Response, jsonify
)
import cv2
import time
import os

from auth import auth_bp
from db import users
from scrape_lessons import fetch_lessons
from rl_module.policy_agent import PolicyAgent
from rl_module.state_builder import compute_learning_state


# ===============================
# 🚀 APP INIT
# ===============================
app = Flask(__name__)
app.secret_key = "neurodiverse_super_secret_key"
app.register_blueprint(auth_bp)


# ===============================
# 🏠 ROOT
# ===============================
@app.route("/")
def root():
    return redirect(url_for("auth.login"))


# ===============================
# 🎥 CAMERA INIT
# ===============================
camera = None
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

policy_agent = PolicyAgent()


# ===============================
# ⚠️ DISTRACTION STATE
# ===============================
distraction_start = None
DISTRACTION_LIMIT = 10

_pending_game = None
game_active = False
last_game = None
cooldown_until = 0


# ===============================
# 🧠 PROFILE SUMMARY
# ===============================
def generate_learning_profile(scores):
    if scores.get("impulse_control", 0) < 50:
        return "You’re energetic ⚡ We’ll help improve impulse control and focus."
    return "Great self-control 🚀 Let’s strengthen consistency."


# ===============================
# 🎯 RL CONTENT DIFFICULTY
# ===============================
def choose_content_difficulty(username):
    user = users.find_one({"username": username}) or {}
    scores = user.get("scores", {})
    ml_profile = user.get("ml_profile", {})

    if not ml_profile.get("presentation_code"):
        return 1

    state = compute_learning_state(
        {"focused": scores.get("attention", 50), "distracted": 100},
        user.get("games", {}),
        ml_profile["presentation_code"]
    )

    return policy_agent.choose_action(state)


# ===============================
# 🔀 FLOW CONTROL (CALIBRATION ENFORCER)
# ===============================
@app.route("/flow")
def flow():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = users.find_one({"username": session["username"]}) or {}
    games = user.get("games", {})

    # Force Game 1
    if not games.get("game1", {}).get("completed"):
        return redirect(url_for("game1"))

    # Force Game 2
    if not games.get("game2", {}).get("completed"):
        return redirect(url_for("game2"))

    return redirect(url_for("dashboard"))


# ===============================
# 🎮 GAME 1
# ===============================
@app.route("/game1", methods=["GET", "POST"])
def game1():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        users.update_one(
            {"username": session["username"]},
            {"$set": {
                "scores.attention": float(request.form.get("attention", 0)),
                "scores.impulse_control": float(request.form.get("impulse_control", 0)),
                "games.game1.completed": True
            }}
        )
        return redirect(url_for("flow"))

    return render_template("game1.html")


# ===============================
# 🎮 GAME 2
# ===============================
@app.route("/game2", methods=["GET", "POST"])
def game2():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        user = users.find_one({"username": session["username"]}) or {}
        scores = user.get("scores", {})

        scores.update({
            "organization": float(request.form.get("organization", 0)),
            "memory": float(request.form.get("working_memory", 0))
        })

        users.update_one(
            {"username": session["username"]},
            {"$set": {
                "scores": scores,
                "games.game2.completed": True,
                "profile.summary": generate_learning_profile(scores),
                "ml_profile.presentation_code": "VISUAL_FAST"
            }}
        )

        return redirect(url_for("dashboard"))

    return render_template("game2.html")


# ===============================
# 📸 VIDEO STREAM
# ===============================
def generate_frames():
    while True:
        if camera is None:
            break

        ret, frame = camera.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        state = "Focused" if len(faces) else "Distracted"
        color = (0, 255, 0) if state == "Focused" else (0, 0, 255)

        cv2.putText(frame, state, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        _, buffer = cv2.imencode(".jpg", frame)

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() + b"\r\n"
        )


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ===============================
# ⚠️ DISTRACTION CHECK
# ===============================
@app.route("/check_distraction")
def check_distraction():
    global distraction_start, _pending_game, game_active, last_game, cooldown_until

    if game_active or time.time() < cooldown_until or camera is None:
        return jsonify({"distracted": False})

    ret, frame = camera.read()
    if not ret:
        return jsonify({"distracted": False})

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    distracted = len(faces) == 0

    if distracted:
        if distraction_start is None:
            distraction_start = time.time()
        elif time.time() - distraction_start > DISTRACTION_LIMIT:

            next_game = "RELAX" if last_game != "RELAX" else "CHALLENGE"

            _pending_game = next_game
            game_active = True
            last_game = next_game
            distraction_start = None

            return jsonify({"distracted": True})
    else:
        distraction_start = None

    return jsonify({"distracted": False})


# ===============================
# 🎮 IDLE → GAME
# ===============================
@app.route("/report_idle", methods=["POST"])
def report_idle():
    global _pending_game, game_active, last_game, cooldown_until

    if game_active or time.time() < cooldown_until:
        return jsonify({"ok": False})

    next_game = "CHALLENGE" if last_game != "CHALLENGE" else "RELAX"

    _pending_game = next_game
    game_active = True
    last_game = next_game

    return jsonify({"ok": True})


# ===============================
# 🎮 PENDING GAME
# ===============================
@app.route("/pending_game")
def pending_game():
    global _pending_game

    if not _pending_game:
        return jsonify({"ok": False})

    game = _pending_game
    _pending_game = None

    if game == "RELAX":
        return jsonify({"ok": True, "url": url_for("relaxation_game")})
    else:
        return jsonify({"ok": True, "url": url_for("challenge_game")})


# ===============================
# 🎮 GAME FINISHED
# ===============================
@app.route("/log_game_result", methods=["POST"])
def log_game_result():
    global game_active, cooldown_until

    game_active = False
    cooldown_until = time.time() + 5

    return jsonify({"ok": True})


# ===============================
# 🎮 POST-DASHBOARD GAMES
# ===============================
@app.route("/games/relaxation")
def relaxation_game():
    return render_template("games/relaxation.html")


@app.route("/games/challenge")
def challenge_game():
    return render_template("games/challenge.html")


# ===============================
# 🧠 DASHBOARD
# ===============================
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    user = users.find_one({"username": session["username"]}) or {}

    lessons = fetch_lessons()
    difficulty = choose_content_difficulty(session["username"])

    lessons = lessons[:2] if difficulty == 0 else lessons[:4]

    return render_template(
        "index.html",
        lessons=lessons,
        main_video=lessons[0] if lessons else {},
        user_profile=user.get("scores", {}),
        profile_summary=user.get("profile", {}).get("summary", ""),
        presentation_code=user.get("ml_profile", {}).get("presentation_code", "")
    )


# ===============================
# 🚀 RUN
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
