import sqlite3
from datetime import datetime

DB_NAME = "football.db"


def init_db():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            played_at TEXT NOT NULL,
            team_a TEXT NOT NULL,
            team_b TEXT NOT NULL,
            score_a INTEGER NOT NULL,
            score_b INTEGER NOT NULL
        )
        """
    )
    con.commit()
    con.close()


def save_match(team_a, team_b, score_a, score_b):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO matches (played_at, team_a, team_b, score_a, score_b)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            team_a,
            team_b,
            score_a,
            score_b,
        ),
    )
    con.commit()
    con.close()


def get_recent_matches(limit=10):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute(
        """
        SELECT played_at, team_a, team_b, score_a, score_b
        FROM matches
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    con.close()
    return rows
