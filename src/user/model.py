from dataclasses import dataclass
from typing import TypedDict


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
