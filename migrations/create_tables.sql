-- Migration: create_tables.sql
-- Creates the main tables used by Student Stress Tracker

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS stress_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    academic_pressure INTEGER NOT NULL,
    sleep_hours REAL NOT NULL,
    physical_activity INTEGER NOT NULL,
    social_support INTEGER NOT NULL,
    workload_hours INTEGER NOT NULL,
    stress_level INTEGER NOT NULL,
    stress_score REAL NOT NULL,
    recommendations TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chart_cache (
    id INTEGER PRIMARY KEY,
    data TEXT,
    last_updated DATETIME
);

COMMIT;
