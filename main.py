import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import jwt

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"

db_path = "appointments.db"


# Database Initialization
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        role TEXT NOT NULL,
                        password TEXT NOT NULL
                      )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS availability (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        professor_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        time_slot TEXT NOT NULL,
                        is_booked INTEGER DEFAULT 0
                      )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS appointments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER NOT NULL,
                        professor_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        time_slot TEXT NOT NULL
                      )"""
    )

    conn.commit()
    conn.close()


# Token Utility Functions
def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1),  # Token expires in 1 hour
    }
    token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")
    return token


def decode_token(token):
    try:
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401


# Routes
@app.route("/api/v1/register", methods=["POST"])
def register():
    data = request.json
    username = data["username"]
    password = data["password"]
    role = data["role"]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, role, password) VALUES (?, ?, ?)",
            (username, role, password),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"message": "User already exists"}), 400
    finally:
        conn.close()

    return jsonify({"message": "User registered successfully"})


@app.route("/api/v1/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ? AND password = ?", (username, password)
    )
    user = cursor.fetchone()

    conn.close()

    if not user:
        return jsonify({"message": "Invalid username or password"}), 401

    token = generate_token(user[0])
    return jsonify({"token": token})


@app.route("/api/v1/set_availability", methods=["POST"])
def set_availability():
    token = request.headers.get("Authorization")
    professor_id = decode_token(token)

    if not professor_id:
        return jsonify({"message": "Invalid or expired token"}), 401

    data = request.json
    date = data["date"]
    time_slot = data["time_slot"]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO availability (professor_id, date, time_slot) VALUES (?, ?, ?)",
        (professor_id, date, time_slot),
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Availability set successfully"})


@app.route("/api/v1/view_professors", methods=["GET"])
def view_professors():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username FROM users WHERE role = 'professor'")
    professors = cursor.fetchall()

    conn.close()

    professor_list = [{"id": row[0], "username": row[1]} for row in professors]
    return jsonify({"professors": professor_list})


@app.route("/api/v1/view_availability/<int:professor_id>", methods=["GET"])
def view_availability(professor_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT date, time_slot FROM availability WHERE professor_id = ? AND is_booked = 0",
        (professor_id,),
    )
    availability = cursor.fetchall()

    conn.close()

    slots = [{"date": row[0], "time_slot": row[1]} for row in availability]
    return jsonify({"available_slots": slots})


@app.route("/api/v1/book_appointment", methods=["POST"])
def book_appointment():
    token = request.headers.get("Authorization")
    student_id = decode_token(token)

    if not student_id:
        return jsonify({"message": "Invalid or expired token"}), 401

    data = request.json
    professor_id = data["professor_id"]
    date = data["date"]
    time_slot = data["time_slot"]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM availability WHERE professor_id = ? AND date = ? AND time_slot = ? AND is_booked = 0",
        (professor_id, date, time_slot),
    )
    availability = cursor.fetchone()

    if not availability:
        conn.close()
        return jsonify({"message": "Slot not available"}), 400

    cursor.execute(
        "INSERT INTO appointments (student_id, professor_id, date, time_slot) VALUES (?, ?, ?, ?)",
        (student_id, professor_id, date, time_slot),
    )
    cursor.execute(
        "UPDATE availability SET is_booked = 1 WHERE id = ?", (availability[0],)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Appointment booked successfully"})


@app.route("/api/v1/view_professor_appointments", methods=["GET"])
def view_professor_appointments():
    token = request.headers.get("Authorization")
    professor_id = decode_token(token)

    if not professor_id:
        return jsonify({"message": "Invalid or expired token"}), 401

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT a.id, a.date, a.time_slot, u.username AS student_name
        FROM appointments a
        JOIN users u ON a.student_id = u.id
        WHERE a.professor_id = ?
    """,
        (professor_id,),
    )
    appointments = cursor.fetchall()

    conn.close()

    appointment_list = [
        {
            "appointment_id": row[0],
            "date": row[1],
            "time_slot": row[2],
            "student_name": row[3],
        }
        for row in appointments
    ]
    return jsonify({"appointments": appointment_list})


@app.route("/api/v1/cancel_appointment/<int:appointment_id>", methods=["DELETE"])
def cancel_appointment(appointment_id):
    token = request.headers.get("Authorization")
    professor_id = decode_token(token)

    if not professor_id:
        return jsonify({"message": "Invalid or expired token"}), 401

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT professor_id, date, time_slot FROM appointments WHERE id = ?",
        (appointment_id,),
    )
    appointment = cursor.fetchone()

    if not appointment:
        conn.close()
        return jsonify({"message": "Appointment not found"}), 404

    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    cursor.execute(
        "UPDATE availability SET is_booked = 0 WHERE professor_id = ? AND date = ? AND time_slot = ?",
        (appointment[0], appointment[1], appointment[2]),
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Appointment canceled successfully"})


@app.route("/api/v1/view_appointments", methods=["GET"])
def view_appointments():
    token = request.headers.get("Authorization")
    user_id = decode_token(token)

    if not user_id:
        return jsonify({"message": "Invalid or expired token"}), 401

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT date, time_slot, professor_id FROM appointments WHERE student_id = ?",
        (user_id,),
    )
    appointments = cursor.fetchall()

    conn.close()

    appointment_details = [
        {"date": row[0], "time_slot": row[1], "professor_id": row[2]}
        for row in appointments
    ]
    return jsonify({"appointments": appointment_details})


# Initialize Database
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
