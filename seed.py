import json
import random
import sqlite3
from typing import TypedDict

from werkzeug.security import generate_password_hash

USERS = ["Alice", "Bob", "Charlie", "Diane"]

INSERT_USER_SQL = "INSERT INTO user (username, password_hash) VALUES (?, ?)"

INSERT_RECIPE_SQL = """
    INSERT INTO recipe (user_id, created_at, title, ingredients, instructions)
    VALUES (?, datetime('now'), ?, ?, ?)
"""


class Recipe(TypedDict):
    title: str
    ingredients: list[str]
    instructions: list[str]


def main() -> None:
    db = sqlite3.connect("database.db")
    db.execute("PRAGMA foreign_keys = ON")
    db.row_factory = sqlite3.Row

    db.execute("DELETE FROM recipe")
    db.execute("DELETE FROM user")

    user_ids: list[int] = []

    for user in USERS:
        pw = generate_password_hash(user)
        print(f"insert user: '{user}'")
        insert_user_result = db.execute(INSERT_USER_SQL, [user, pw])
        user_ids.append(insert_user_result.lastrowid)

    with open("recipes.json", encoding="utf-8") as recipes_json:
        recipe_data: list[Recipe] = json.load(recipes_json)

    for recipe in recipe_data:
        user_id = random.choice(user_ids)
        title = recipe["title"]
        ingredients = "\n".join(recipe["ingredients"])
        instructions = "\n".join(recipe["instructions"])
        print(f"insert recipe: '{title}'")
        db.execute(
            INSERT_RECIPE_SQL,
            [user_id, title, ingredients, instructions],
        )

    db.commit()
    db.close()


if __name__ == "__main__":
    main()
