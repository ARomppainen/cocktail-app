import sqlite3
from flask import g


def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con


def execute(sql, params=None):
    con = get_connection()
    result = con.execute(sql, params or [])
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()


def last_insert_id():
    return g.last_insert_id


def query(sql, params=None):
    con = get_connection()
    result = con.execute(sql, params or []).fetchall()
    con.close()
    return result
