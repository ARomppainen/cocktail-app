from dataclasses import dataclass
import sqlite3
from typing import TypedDict

import db


class LoggedInUser(TypedDict):
    id: int
    username: str


@dataclass(frozen=True)
class User:
    id: int
    username: str
    password_hash: str


@dataclass(frozen=True)
class LoginForm:
    username: str
    password: str

    @staticmethod
    def empty() -> "LoginForm":
        return LoginForm("", "")

    def validate(self) -> dict[str, str]:
        errors: dict[str, str] = {}

        if not self.username:
            errors["username"] = "Value is required"

        if not self.password:
            errors["password"] = "Value is required"

        return errors


@dataclass(frozen=True)
class CreateUserForm:
    username: str
    password1: str
    password2: str

    @staticmethod
    def empty() -> "CreateUserForm":
        return CreateUserForm("", "", "")

    def validate(self) -> dict[str, str]:
        errors: dict[str, str] = {}

        if not self.username:
            errors["username"] = "Value is required"

        if not self.password1:
            errors["password1"] = "Value is required"

        if not self.password2:
            errors["password2"] = "Value is required"
        elif self.password1 != self.password2:
            errors["password2"] = "The passwords did not match"

        return errors


class UsernameNotAvailableError(RuntimeError):
    pass


def get_user(user_id: int) -> User | None:
    sql = "SELECT id, username, password_hash FROM user WHERE id = ?"
    result = db.query(sql, [user_id])
    if not result:
        return None
    row = result[0]
    return User(
        id=row["id"], username=row["username"], password_hash=row["password_hash"]
    )


def get_user_by_name(username: str) -> User | None:
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
        result = db.execute(
            sql,
            [username, password_hash],
        )
        return User(id=result.lastrowid, username=username, password_hash=password_hash)
    except sqlite3.IntegrityError as err:
        raise UsernameNotAvailableError from err
