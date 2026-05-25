import sqlite3

import db
from user.model import User, UsernameNotAvailableError


def get_user(username: str) -> User | None:
    sql = "SELECT id, username, password_hash FROM user WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None
    row = result[0]
    return User(
        id=row["id"], username=row["username"], password_hash=row["password_hash"]
    )


def create_user(username: str, password_hash: str) -> User:
    sql = "INSERT INTO user (username, password_hash) VALUES (?, ?)"
    try:
        row_id = db.execute(
            sql,
            [username, password_hash],
        )
        return User(id=row_id, username=username, password_hash=password_hash)
    except sqlite3.IntegrityError as err:
        raise UsernameNotAvailableError from err
