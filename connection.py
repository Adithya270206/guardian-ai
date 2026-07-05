import sqlite3
import json
import os

DB_PATH = "database/guardian_ai.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Logs table: captures every request trace, latency, decision details, etc.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        session_id TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        prompt TEXT,
        response TEXT,
        tool_called TEXT,
        blocked INTEGER DEFAULT 0,
        block_reason TEXT,
        risk_score INTEGER DEFAULT 0,
        latency_ms REAL,
        details TEXT
    )
    """)
    
    # 2. Baselines table: tracks cumulative request details to monitor for anomalies per agent/session
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS baselines (
        agent_id TEXT PRIMARY KEY,
        request_count INTEGER DEFAULT 0,
        mean_interval_sec REAL DEFAULT 0.0,
        std_interval_sec REAL DEFAULT 0.0,
        last_request_time REAL
    )
    """)
    
    # 3. Sessions table: tracks active session states and whether they have been killed
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        agent_id TEXT,
        is_killed INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

def add_log(session_id, agent_id, prompt, response, tool_called, blocked, block_reason, risk_score, latency_ms, details):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO logs (session_id, agent_id, prompt, response, tool_called, blocked, block_reason, risk_score, latency_ms, details)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (session_id, agent_id, prompt, response, tool_called, int(blocked), block_reason, risk_score, latency_ms, json.dumps(details)))
    conn.commit()
    conn.close()

def query_logs(limit=100):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    logs = [dict(row) for row in rows]
    for log in logs:
        if log['details']:
            try:
                log['details'] = json.loads(log['details'])
            except:
                pass
    conn.close()
    return logs

def is_session_killed(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_killed FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return bool(row[0])
    return False

def kill_session(session_id, agent_id=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO sessions (session_id, agent_id, is_killed)
    VALUES (?, ?, 1)
    ON CONFLICT(session_id) DO UPDATE SET is_killed=1
    """, (session_id, agent_id))
    conn.commit()
    conn.close()

def get_session_agent(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT agent_id FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def register_session(session_id, agent_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO sessions (session_id, agent_id, is_killed)
    VALUES (?, ?, 0)
    ON CONFLICT(session_id) DO UPDATE SET agent_id=?
    """, (session_id, agent_id, agent_id))
    conn.commit()
    conn.close()

def clear_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs")
    cursor.execute("DELETE FROM baselines")
    cursor.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()
