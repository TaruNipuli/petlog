"""Database (SQLite).

All SQL in this file. The rest of the app calls these functions directly.
Every function that reads or changes data takes an owner_id -> user can only reach their own pets.
"""

import json
import sqlite3
from contextlib import contextmanager # lets _db() be used in a "with" block

DB_PATH = "petlog.db"

COMMON_KEYS = ["mood", "appetite", "sleep_hours", "exercise_minutes", "notes"]

@contextmanager
def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON") # Turn on foreign key checks (off by default in SQLite)
    try:
        yield conn # This is where the code inside the "with" block runs
        conn.commit() # Save changes if nothing went wrong
    finally:
        conn.close() # Close connection

def init_db():
    """Create the tables if they do not exist yet."""
    with _db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS pets (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id   TEXT NOT NULL,
                name       TEXT NOT NULL,
                species    TEXT NOT NULL,
                breed      TEXT,
                birth_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS entries (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id           INTEGER NOT NULL
                                 REFERENCES pets(id) ON DELETE CASCADE,
                entry_date       TEXT NOT NULL,
                mood             INTEGER,
                appetite         INTEGER,
                sleep_hours      REAL,
                exercise_minutes REAL,
                notes            TEXT,
                extra            TEXT NOT NULL DEFAULT '{}',
                created_at       TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (pet_id, entry_date)
            );

            CREATE INDEX IF NOT EXISTS idx_pets_owner ON pets(owner_id);
            """
        )

# Pets

def add_pet(owner_id, name, species, breed=None, birth_date=None):
    """Add a new pet for the given owner."""
    with _db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO pets (owner_id, name, species, breed, birth_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (owner_id, name, species, breed, birth_date),
        )
        return cursor.lastrowid # Return the ID of the newly created pet

def get_pets(owner_id):
    """Return a list of pets for the given owner."""
    with _db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM pets
            WHERE owner_id = ?
            ORDER BY created_at DESC
            """,
            (owner_id,),
        )
        return [dict(row) for row in cursor.fetchall()] # Convert rows to dicts

def delete_pet(owner_id, pet_id):
    """Delete a pet and all its entries for the given owner."""
    with _db() as conn:
        conn.execute(
            """
            DELETE FROM pets
            WHERE id = ? AND owner_id = ?
            """,
            (pet_id, owner_id),
        )

# Entries

def save_entry(pet_id, owner_id, entry_date, values):
    """Save one day's entry for a pet.

    If an entry already exists for that pet and date, it is updated.
    `values` is a dict of field key -> value (common and species-specific).
    """
    common = {k: values.get(k) for k in COMMON_KEYS}
    extra = {k: v for k, v in values.items() if k not in COMMON_KEYS}

    with _db() as conn:
        owned = conn.execute(
            "SELECT 1 FROM pets WHERE id = ? AND owner_id = ?",
            (pet_id, owner_id),
        ).fetchone()
        if not owned:
            raise PermissionError("Pet not found for this user.")

        conn.execute(
            """
            INSERT INTO entries
                (pet_id, entry_date, mood, appetite, sleep_hours,
                 exercise_minutes, notes, extra)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (pet_id, entry_date) DO UPDATE SET
                mood = excluded.mood,
                appetite = excluded.appetite,
                sleep_hours = excluded.sleep_hours,
                exercise_minutes = excluded.exercise_minutes,
                notes = excluded.notes,
                extra = excluded.extra
            """,
            (pet_id, str(entry_date), common["mood"], common["appetite"],
             common["sleep_hours"], common["exercise_minutes"],
             common["notes"], json.dumps(extra)),
        )


def get_entries(pet_id, owner_id):
    """Return a pet's entries, newest first. Empty list if not the owner's pet."""
    with _db() as conn:
        rows = conn.execute(
            """
            SELECT e.* FROM entries e
            JOIN pets p ON p.id = e.pet_id
            WHERE e.pet_id = ? AND p.owner_id = ?
            ORDER BY e.entry_date DESC
            """,
            (pet_id, owner_id),
        ).fetchall()

    entries = []
    for row in rows:
        entry = dict(row)
        entry["extra"] = json.loads(entry["extra"])
        entries.append(entry)
    return entries


def delete_entry(entry_id, owner_id):
    """Delete one entry. Returns True if something was deleted."""
    with _db() as conn:
        cur = conn.execute(
            """
            DELETE FROM entries
            WHERE id = ?
              AND pet_id IN (SELECT id FROM pets WHERE owner_id = ?)
            """,
            (entry_id, owner_id),
        )
        return cur.rowcount > 0