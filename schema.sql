-- schema.sql: Database schema initialization for ReservationAPI
-- This file creates the necessary tables and populates initial data

-- Create rooms table
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    capacity INTEGER NOT NULL,
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create reservations table
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_reservations_room_id ON reservations(room_id);
CREATE INDEX IF NOT EXISTS idx_reservations_start_time ON reservations(start_time);
CREATE INDEX IF NOT EXISTS idx_reservations_end_time ON reservations(end_time);

-- Insert sample rooms
INSERT OR IGNORE INTO rooms (id, name, capacity, location) VALUES
    (1, 'Conference Room A', 10, 'Floor 1, Wing A'),
    (2, 'Meeting Room B', 6, 'Floor 2, Wing B'),
    (3, 'Board Room', 20, 'Floor 3, Executive Suite');
