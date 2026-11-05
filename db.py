import mysql.connector

# Change the password to the one you use in MySQL Workbench
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "uni_market",
}


def get_connection():
    """Open a new connection to the database."""
    return mysql.connector.connect(**DB_CONFIG)


def fetch_all(sql, params=None):
    """Run a SELECT and return all rows as a list of dicts."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        return cursor.fetchall()
    finally:
        conn.close()


def fetch_one(sql, params=None):
    """Run a SELECT and return one row (or None)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        return cursor.fetchone()
    finally:
        conn.close()


def execute(sql, params=None):
    """Run INSERT / UPDATE / DELETE. Returns the new row id (for INSERT)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()