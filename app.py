from flask import Flask, jsonify, request, render_template
from datetime import datetime
from functools import wraps
import oracledb

app = Flask(__name__)

# ----------------------------
# Global connection
# ----------------------------
_conn = None

def get_conn():
    return _conn

def is_connected():
    return _conn is not None

def require_connection(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_connected():
            return jsonify({"error": "Not connected to Oracle. Please connect first."}), 503
        return f(*args, **kwargs)
    return wrapper


# ----------------------------
# Serve Front-End
# ----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# CONNECTION API
# ----------------------------
@app.route("/api/connect", methods=["POST"])
def connect_db():
    global _conn
    data = request.json or {}

    username     = data.get("username", "").strip()
    password     = data.get("password", "").strip()
    host         = data.get("host", "").strip()
    port         = data.get("port", "1521")
    service_name = data.get("service_name", "").strip()

    if not all([username, password, host, service_name]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        port = int(port)
    except ValueError:
        return jsonify({"error": "Port must be a number"}), 400

    try:
        conn = oracledb.connect(
            user=username,
            password=password,
            dsn=f"{host}:{port}/{service_name}"
        )
        # Test it works
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM DUAL")
        cur.close()

        # Close old connection if any
        if _conn:
            try: _conn.close()
            except: pass

        _conn = conn
        print(f"✅ Connected to Oracle at {host}:{port}/{service_name} as {username}")
        return jsonify({"message": f"Connected to {host}:{port}/{service_name} as {username}"}), 200

    except Exception as e:
        _conn = None
        print(f"❌ Connection failed: {e}")
        return jsonify({"error": f"Connection failed: {str(e)}"}), 400


@app.route("/api/disconnect", methods=["POST"])
def disconnect_db():
    global _conn
    if _conn:
        try: _conn.close()
        except: pass
    _conn = None
    return jsonify({"message": "Disconnected from Oracle"}), 200


@app.route("/api/status", methods=["GET"])
def db_status():
    return jsonify({"connected": is_connected()})


# ----------------------------
# ROOMS API
# ----------------------------
@app.route("/api/rooms", methods=["GET"])
@require_connection
def get_rooms():
    cur = _conn.cursor()
    cur.execute("SELECT id, name, capacity, location FROM rooms ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    return jsonify([
        {"id": r[0], "name": r[1], "capacity": r[2], "location": r[3] or ""}
        for r in rows
    ])


@app.route("/api/rooms", methods=["POST"])
@require_connection
def add_room():
    cur = _conn.cursor()
    cur.execute("SELECT COUNT(*) FROM rooms")
    count = cur.fetchone()[0]
    if count >= 50:
        cur.close()
        return jsonify({"error": "Maximum of 50 rooms allowed"}), 400

    data = request.json
    if not data or not data.get("name") or not data.get("capacity"):
        cur.close()
        return jsonify({"error": "name and capacity are required"}), 400

    cur.execute(
        "INSERT INTO rooms (name, capacity, location) VALUES (:1, :2, :3)",
        [data["name"], int(data["capacity"]), data.get("location", "")]
    )
    _conn.commit()

    cur.execute("SELECT MAX(id) FROM rooms")
    new_id = cur.fetchone()[0]
    cur.close()
    return jsonify({"message": "Room created", "id": new_id}), 201


@app.route("/api/rooms/<int:room_id>", methods=["DELETE"])
@require_connection
def delete_room(room_id):
    cur = _conn.cursor()
    cur.execute("SELECT id FROM rooms WHERE id = :1", [room_id])
    if not cur.fetchone():
        cur.close()
        return jsonify({"error": f"Room {room_id} not found"}), 404

    cur.execute("DELETE FROM bookings WHERE room_id = :1", [room_id])
    cur.execute("DELETE FROM rooms WHERE id = :1", [room_id])
    _conn.commit()
    cur.close()
    return jsonify({"message": f"Room {room_id} deleted successfully"})


# ----------------------------
# USERS API
# ----------------------------
@app.route("/api/users", methods=["GET"])
@require_connection
def get_users():
    cur = _conn.cursor()
    cur.execute("SELECT id, username, email FROM users ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    return jsonify([
        {"id": r[0], "username": r[1], "email": r[2]}
        for r in rows
    ])


@app.route("/api/users", methods=["POST"])
@require_connection
def add_user():
    data = request.json
    if not data or not data.get("username") or not data.get("email"):
        return jsonify({"error": "username and email are required"}), 400

    cur = _conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = :1", [data["username"]])
    if cur.fetchone():
        cur.close()
        return jsonify({"error": f"Username '{data['username']}' already exists"}), 400

    cur.execute(
        "INSERT INTO users (username, email) VALUES (:1, :2)",
        [data["username"], data["email"]]
    )
    _conn.commit()

    cur.execute("SELECT MAX(id) FROM users")
    new_id = cur.fetchone()[0]
    cur.close()
    return jsonify({"message": "User created", "id": new_id}), 201


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
@require_connection
def delete_user(user_id):
    cur = _conn.cursor()
    cur.execute("SELECT id FROM users WHERE id = :1", [user_id])
    if not cur.fetchone():
        cur.close()
        return jsonify({"error": f"User {user_id} not found"}), 404

    cur.execute("DELETE FROM bookings WHERE user_id = :1", [user_id])
    cur.execute("DELETE FROM users WHERE id = :1", [user_id])
    _conn.commit()
    cur.close()
    return jsonify({"message": f"User {user_id} deleted successfully"})


# ----------------------------
# BOOKINGS API
# ----------------------------
@app.route("/api/bookings", methods=["GET"])
@require_connection
def get_bookings():
    cur = _conn.cursor()
    cur.execute("""
        SELECT b.id, b.room_id, r.name, b.user_id, u.username,
               b.start_time, b.end_time, b.purpose
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN users u ON b.user_id = u.id
        ORDER BY b.start_time
    """)
    rows = cur.fetchall()
    cur.close()
    return jsonify([
        {
            "id":         r[0],
            "room_id":    r[1],
            "room_name":  r[2],
            "user_id":    r[3],
            "username":   r[4],
            "start_time": r[5].isoformat(),
            "end_time":   r[6].isoformat(),
            "purpose":    r[7] or "",
        }
        for r in rows
    ])


@app.route("/api/bookings", methods=["POST"])
@require_connection
def add_booking():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    cur = _conn.cursor()

    cur.execute("SELECT id FROM rooms WHERE id = :1", [data.get("room_id")])
    if not cur.fetchone():
        cur.close()
        return jsonify({"error": f"Room ID {data.get('room_id')} does not exist"}), 400

    cur.execute("SELECT id FROM users WHERE id = :1", [data.get("user_id")])
    if not cur.fetchone():
        cur.close()
        return jsonify({"error": f"User ID {data.get('user_id')} does not exist"}), 400

    try:
        start_time = datetime.strptime(data["start_time"], "%Y-%m-%dT%H:%M")
        end_time   = datetime.strptime(data["end_time"],   "%Y-%m-%dT%H:%M")
    except (ValueError, KeyError):
        cur.close()
        return jsonify({"error": "Datetime must be in format YYYY-MM-DDTHH:MM"}), 400

    if end_time <= start_time:
        cur.close()
        return jsonify({"error": "end_time must be after start_time"}), 400

    cur.execute("""
        SELECT id, start_time, end_time FROM bookings
        WHERE room_id = :1
          AND start_time < :2
          AND end_time   > :3
    """, [data["room_id"], end_time, start_time])
    conflict = cur.fetchone()
    if conflict:
        cur.close()
        return jsonify({
            "error": f"Room already booked from {conflict[1].strftime('%Y-%m-%d %H:%M')} "
                     f"to {conflict[2].strftime('%Y-%m-%d %H:%M')}"
        }), 409

    cur.execute(
        "INSERT INTO bookings (room_id, user_id, start_time, end_time, purpose) VALUES (:1, :2, :3, :4, :5)",
        [data["room_id"], data["user_id"], start_time, end_time, data.get("purpose", "")]
    )
    _conn.commit()

    cur.execute("SELECT MAX(id) FROM bookings")
    new_id = cur.fetchone()[0]
    cur.close()
    print(f"✅ Booking saved: User {data['user_id']} → Room {data['room_id']}")
    return jsonify({"message": "Booking created", "id": new_id}), 201


@app.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
@require_connection
def delete_booking(booking_id):
    cur = _conn.cursor()
    cur.execute("SELECT id FROM bookings WHERE id = :1", [booking_id])
    if not cur.fetchone():
        cur.close()
        return jsonify({"error": f"Booking {booking_id} not found"}), 404

    cur.execute("DELETE FROM bookings WHERE id = :1", [booking_id])
    _conn.commit()
    cur.close()
    return jsonify({"message": f"Booking {booking_id} deleted successfully"})


# ----------------------------
# Dashboard
# ----------------------------
@app.route("/dashboard")
@require_connection
def dashboard():
    cur = _conn.cursor()

    cur.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = cur.fetchone()[0]

    now = datetime.now()
    cur.execute("""
        SELECT COUNT(*) FROM bookings
        WHERE start_time <= :1 AND end_time >= :2
    """, [now, now])
    active_bookings = cur.fetchone()[0]
    cur.close()

    return jsonify({
        "total_rooms":     total_rooms,
        "active_bookings": active_bookings,
        "available_rooms": total_rooms - active_bookings
    })


# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)