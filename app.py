import cv2
import face_recognition
import numpy as np
import sqlite3
import datetime
import pickle
import io
import csv
from flask import Flask, render_template, request, redirect, url_for, Response, send_file, flash

app = Flask(__name__)
app.secret_key = "academic_secret"
DB_NAME = "attendance_system.db"


# -------------------------
# DATABASE INITIALIZATION
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            embedding BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_str TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    conn.commit()
    conn.close()


init_db()


# -------------------------
# LOAD FACE ENCODINGS
# -------------------------
known_face_encodings = []
known_face_ids = []
known_face_names = []


def load_encodings():
    global known_face_encodings, known_face_ids, known_face_names

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT id, name, embedding FROM students")
    rows = c.fetchall()

    known_face_encodings = []
    known_face_ids = []
    known_face_names = []

    for sid, name, emb in rows:
        try:
            encoding = pickle.loads(emb)
            known_face_encodings.append(encoding)
            known_face_ids.append(sid)
            known_face_names.append(name)
        except:
            pass

    conn.close()


load_encodings()


# -------------------------
# ATTENDANCE LOGGING
# -------------------------
def register_attendance(student_id):
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        "SELECT * FROM attendance WHERE student_id = ? AND date_str = ?",
        (student_id, date_str),
    )
    row = c.fetchone()

    if not row:
        c.execute(
            "INSERT INTO attendance (student_id, date_str) VALUES (?, ?)",
            (student_id, date_str),
        )
        conn.commit()

    conn.close()


# -------------------------
# VIDEO STREAM
# -------------------------
def generate_frames():
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        return

    while True:
        success, frame = cam.read()
        if not success:
            break

        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small)
        encodings = face_recognition.face_encodings(rgb_small, face_locations)

        names_out = []

        for enc in encodings:
            name = "Unknown"
            sid = None

            if len(known_face_encodings) > 0:
                matches = face_recognition.compare_faces(known_face_encodings, enc, 0.6)
                distances = face_recognition.face_distance(known_face_encodings, enc)

                best_idx = np.argmin(distances)
                if matches[best_idx]:
                    name = known_face_names[best_idx]
                    sid = known_face_ids[best_idx]
                    register_attendance(sid)

            names_out.append(name)

        for (top, right, bottom, left), name in zip(face_locations, names_out):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, -1)
            cv2.putText(frame, name, (left + 5, bottom - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)

        _, buffer = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")


# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def dashboard():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    c.execute("SELECT COUNT(*) FROM attendance WHERE date_str = ?", (today,))
    today_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM students")
    student_count = c.fetchone()[0]

    c.execute("""
        SELECT a.date_str, a.timestamp, s.id, s.name, s.course
        FROM attendance a
        JOIN students s ON s.id = a.student_id
        ORDER BY a.timestamp DESC
    """)
    data = c.fetchall()

    conn.close()

    return render_template("dashboard.html",
                           attendance=data,
                           today_count=today_count,
                           student_count=student_count)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        sid = request.form["student_id"].strip()
        name = request.form["name"].strip()
        course = request.form["course"].strip()
        file = request.files["file"]

        if not sid or not name or not course or not file:
            flash("All fields are required.", "error")
            return redirect("/register")

        img = face_recognition.load_image_file(io.BytesIO(file.read()))
        encs = face_recognition.face_encodings(img)

        if len(encs) == 0:
            flash("No face detected. Try another photo.", "error")
            return redirect("/register")

        embedding = pickle.dumps(encs[0])

        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO students (id, name, course, embedding) VALUES (?, ?, ?, ?)",
                      (sid, name, course, embedding))
            conn.commit()
            conn.close()
        except:
            flash("Student ID already exists.", "error")
            return redirect("/register")

        load_encodings()
        flash("Student registered successfully!", "success")
        return redirect("/")

    return render_template("register.html")


@app.route("/live")
def live():
    return render_template("live.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/export")
def export():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT a.date_str, a.timestamp, s.id, s.name, s.course
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.timestamp DESC
    """)
    rows = c.fetchall()

    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Date", "Time", "Student ID", "Name", "Course"])
    for r in rows:
        writer.writerow(r)

    mem = io.BytesIO()
    mem.write(output.getvalue().encode())
    mem.seek(0)

    return send_file(mem, download_name="attendance.csv", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
