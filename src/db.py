import sqlite3


def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con


def execute(sql, params=None) -> int:
    con = get_connection()
    result = con.execute(sql, params or [])
    con.commit()
    con.close()
    return result.lastrowid


def query(sql, params=None):
    con = get_connection()
    result = con.execute(sql, params or []).fetchall()
    con.close()
    return result
