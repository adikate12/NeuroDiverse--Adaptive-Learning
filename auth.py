from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from db import users

auth_bp = Blueprint("auth", __name__)

# ===============================
# 🔐 LOGIN
# ===============================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = users.find_one({"username": username})

        if user and check_password_hash(user["password_hash"], password):
            session["username"] = username

            # ✅ IMPORTANT: Go to flow (NOT dashboard)
            return redirect(url_for("flow"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ===============================
# 📝 REGISTER
# ===============================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if users.find_one({"username": username}):
            return render_template("register.html", error="Username already exists")

        users.insert_one({
            "username": username,
            "email": email,
            "password_hash": generate_password_hash(password),

            # ✅ Scores start empty (calculated by games)
            "scores": {},

            # ✅ Games start incomplete
            "games": {
                "game1": {"completed": False},
                "game2": {"completed": False}
            },

            "profile": {},
            "ml_profile": {},
            "email_verified": False,
            "created_at": datetime.utcnow()
        })

        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ===============================
# 🚪 LOGOUT
# ===============================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
