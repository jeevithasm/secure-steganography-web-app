from flask import Flask, render_template, request, redirect, session, url_for
import os
import sqlite3
import uuid

from steg import hide_message, extract_message, detect_message
from audio_secure import encode_audio, decode_audio
from video_steg import encode_video, decode_video

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()


# ================= LANDING =================
@app.route("/")
def landing():
    return render_template("landing.html")


# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "❌ Invalid credentials"

    return render_template("login.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# ================= IMAGE =================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    result = ""
    output_image = None

    if request.method == "POST":
        action = request.form["action"]
        file = request.files["image"]

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        if action == "hide":
            message = request.form["message"]
            output_image = hide_message(filepath, message)
            result = "✅ Message hidden successfully!"

        elif action == "extract":
            msg = extract_message(filepath)
            result = msg if msg else "❌ No hidden message"

        elif action == "detect":
            found = detect_message(filepath)
            result = "⚠️ Hidden data detected!" if found else "✅ No hidden data"

    return render_template("index.html", result=result, output_image=output_image)


# ================= AUDIO =================
@app.route("/audio", methods=["GET", "POST"])
def audio():
    if "user" not in session:
        return redirect("/login")

    result = ""
    file_out = None

    if request.method == "POST":
        action = request.form["action"]
        file = request.files["file"]
        password = request.form["password"]

        if not file.filename.lower().endswith(".wav"):
            return render_template("audio.html", result="❌ Upload .wav only")

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        if action == "encode":
            filename = f"audio_{uuid.uuid4().hex}.wav"
            output_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            message = request.form.get("message", "")
            encode_audio(filepath, output_path, message, password)

            result = "✅ Audio encoded"
            file_out = filename

        elif action == "decode":
            msg = decode_audio(filepath, password)
            result = msg if msg else "❌ No message or wrong password"

    return render_template("audio.html", result=result, file=file_out)


# ================= VIDEO =================
@app.route("/video", methods=["GET", "POST"])
def video():
    if "user" not in session:
        return redirect("/login")

    result = ""
    file_out = None

    if request.method == "POST":
        action = request.form["action"]
        file = request.files["file"]
        password = request.form["password"]

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        if action == "encode":
            filename = f"video_{uuid.uuid4().hex}.avi"
            output_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            message = request.form.get("message", "")

            encode_video(filepath, output_path, message, password)

            result = "✅ Video encoded successfully!"
            file_out = filename

        elif action == "decode":
            msg = decode_video(filepath, password)
            result = msg if msg else "❌ No message or wrong password"

    return render_template("video.html", result=result, file=file_out)


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)