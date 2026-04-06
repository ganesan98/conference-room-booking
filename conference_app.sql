-- Drop if re-running
DROP TABLE bookings CASCADE CONSTRAINTS PURGE;
DROP TABLE users    CASCADE CONSTRAINTS PURGE;
DROP TABLE rooms    CASCADE CONSTRAINTS PURGE;

-- ROOMS
CREATE TABLE rooms (
    id       NUMBER GENERATED AS IDENTITY PRIMARY KEY,
    name     VARCHAR2(100) NOT NULL,
    capacity NUMBER        NOT NULL,
    location VARCHAR2(100)
);

-- USERS
CREATE TABLE users (
    id       NUMBER GENERATED AS IDENTITY PRIMARY KEY,
    username VARCHAR2(50)  UNIQUE NOT NULL,
    email    VARCHAR2(100) NOT NULL
);

-- BOOKINGS
CREATE TABLE bookings (
    id         NUMBER GENERATED AS IDENTITY PRIMARY KEY,
    room_id    NUMBER NOT NULL,
    user_id    NUMBER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time   TIMESTAMP NOT NULL,
    purpose    VARCHAR2(200),
    CONSTRAINT fk_room FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- SEED DATA
INSERT INTO users (username, email) VALUES ('alice',   'alice@example.com');
INSERT INTO users (username, email) VALUES ('bob',     'bob@example.com');
INSERT INTO users (username, email) VALUES ('charlie', 'charlie@example.com');

INSERT INTO rooms (name, capacity, location) VALUES ('Meeting Room A',    10, 'Floor 1');
INSERT INTO rooms (name, capacity, location) VALUES ('Conference Room B', 20, 'Floor 2');
INSERT INTO rooms (name, capacity, location) VALUES ('Board Room',        30, 'Floor 3');

COMMIT;

-- Verify
SELECT * FROM users;
SELECT * FROM rooms;
SELECT * FROM bookings;