# 🏢 Conference Room Booking System

A web-based conference room booking system built with **Flask** and **Oracle Database**. Users can manage rooms, register participants, and schedule bookings — all through a clean dark-themed UI with a dynamic Oracle login.

---

## ✨ Features

- 🔌 **Dynamic Oracle login** — enter your own DB credentials at runtime, no hardcoded config
- 📅 **Bookings** — create, view and cancel room reservations with conflict detection
- 🏢 **Room management** — add and delete conference rooms
- 👤 **User management** — register and remove users
- 📊 **Live dashboard** — shows total rooms, active bookings and available rooms
- ⚡ **Raw oracledb cursors** — no ORM, direct SQL for reliable Oracle connectivity

---

## 🛠 Tech Stack

| Layer    | Technology        |
|----------|-------------------|
| Backend  | Python, Flask     |
| Database | Oracle DB         |
| Driver   | python-oracledb   |
| Frontend | HTML, CSS, JS     |

---

## 📁 Project Structure

```
conference-room-booking/
├── app.py                  # Flask backend + REST APIs
├── conference_app.sql      # Oracle schema + seed data
└── templates/
    └── index.html          # Frontend UI
```

---

## ⚙️ Setup & Run

### 1. Install dependencies
```bash
pip install flask oracledb
```

### 2. Set up the database
Run `conference_app.sql` in Oracle SQL Developer or SQL*Plus to create tables and seed data.

### 3. Run the app
```bash
python app.py
```

### 4. Open in browser
```
http://127.0.0.1:5000
```

Enter your Oracle credentials in the login screen and click **Connect**.

---

## 🔌 Oracle Login Fields

| Field        | Example       |
|--------------|---------------|
| Host / IP    | your_hostname |
| Port         | 1521/1522     |
| Service Name | orclNew       |
| Username     | your_username |
| Password     | your_password |

---

## 📡 API Endpoints

| Method | Endpoint                    | Description          |
|--------|-----------------------------|----------------------|
| POST   | `/api/connect`              | Connect to Oracle    |
| POST   | `/api/disconnect`           | Disconnect           |
| GET    | `/api/status`               | Connection status    |
| GET    | `/api/rooms`                | List all rooms       |
| POST   | `/api/rooms`                | Add a room           |
| DELETE | `/api/rooms/<id>`           | Delete a room        |
| GET    | `/api/users`                | List all users       |
| POST   | `/api/users`                | Add a user           |
| DELETE | `/api/users/<id>`           | Delete a user        |
| GET    | `/api/bookings`             | List all bookings    |
| POST   | `/api/bookings`             | Create a booking     |
| DELETE | `/api/bookings/<id>`        | Cancel a booking     |
| GET    | `/dashboard`                | Live stats           |

---

## 📌 Notes

- Oracle listener must be running on the DB server before connecting
- No credentials are stored in the code or committed to the repo
- Booking conflict detection prevents double-booking of rooms

