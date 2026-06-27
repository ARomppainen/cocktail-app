import sqlite3

import db


class UsernameNotAvailableError(RuntimeError):
    pass


def get_user(user_id: int):
    sql = "SELECT id, username, password_hash FROM user WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None


def get_user_by_name(username: str):
    sql = "SELECT id, username, password_hash FROM user WHERE username = ?"
    result = db.query(sql, [username])
    return result[0] if result else None


def create_user(username: str, password_hash: str) -> int:
    sql = "INSERT INTO user (username, password_hash) VALUES (?, ?)"
    try:
        result = db.execute(
            sql,
            [username, password_hash],
        )
        return result.lastrowid
    except sqlite3.IntegrityError as err:
        raise UsernameNotAvailableError from err
