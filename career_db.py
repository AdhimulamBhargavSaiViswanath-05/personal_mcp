"""SQLite helpers for the personal job-application tracker (links + status only)."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

APPLICATION_SOURCES = frozenset({"github", "linkedin", "naukri", "other"})
APPLICATION_STATUSES = frozenset(
    {"wishlist", "applied", "interview", "offer", "rejected", "withdrawn"}
)


def _connect(db_path: Path) -> sqlite3.Connection:
    """Open a connection to the career database with row dict-like access."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_career_db(db_path: Path) -> None:
    """Create the applications table if it does not exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                source TEXT NOT NULL,
                url TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'applied',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def add_application(
    db_path: Path,
    company: str,
    role: str,
    source: str,
    url: str = "",
    status: str = "applied",
    notes: str = "",
) -> dict:
    """Insert one job application row and return the stored record."""
    source = source.lower().strip()
    status = status.lower().strip()
    if source not in APPLICATION_SOURCES:
        raise ValueError(f"source must be one of: {sorted(APPLICATION_SOURCES)}")
    if status not in APPLICATION_STATUSES:
        raise ValueError(f"status must be one of: {sorted(APPLICATION_STATUSES)}")
    now = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO applications
                (company, role, source, url, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (company.strip(), role.strip(), source, url.strip(), status, notes.strip(), now, now),
        )
        conn.commit()
        row_id = cur.lastrowid
        row = conn.execute(
            "SELECT * FROM applications WHERE id = ?", (row_id,)
        ).fetchone()
    return dict(row)


def list_applications(
    db_path: Path,
    source: str = "",
    status: str = "",
    limit: int = 50,
) -> list[dict]:
    """Return recent applications, optionally filtered by source and status."""
    limit = max(1, min(limit, 200))
    clauses: list[str] = []
    params: list[object] = []
    if source.strip():
        clauses.append("source = ?")
        params.append(source.lower().strip())
    if status.strip():
        clauses.append("status = ?")
        params.append(status.lower().strip())
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT * FROM applications {where} ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with _connect(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def update_application_status(
    db_path: Path,
    application_id: int,
    status: str,
    notes: str = "",
) -> dict:
    """Update status (and optional notes) for one application by id."""
    status = status.lower().strip()
    if status not in APPLICATION_STATUSES:
        raise ValueError(f"status must be one of: {sorted(APPLICATION_STATUSES)}")
    now = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        existing = conn.execute(
            "SELECT id FROM applications WHERE id = ?", (application_id,)
        ).fetchone()
        if not existing:
            raise ValueError(f"no application with id {application_id}")
        if notes.strip():
            conn.execute(
                """
                UPDATE applications
                SET status = ?, notes = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, notes.strip(), now, application_id),
            )
        else:
            conn.execute(
                """
                UPDATE applications SET status = ?, updated_at = ? WHERE id = ?
                """,
                (status, now, application_id),
            )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM applications WHERE id = ?", (application_id,)
        ).fetchone()
    return dict(row)
