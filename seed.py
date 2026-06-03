import json
import random
from typing import TypedDict

from werkzeug.security import generate_password_hash

import db
from recipes import create_recipe, RecipeForm
from users import create_user

USERS = ["Alice", "Bob", "Charlie", "Diane"]


class Recipe(TypedDict):
    title: str
    ingredients: list[str]
    instructions: list[str]


def main() -> None:
    db.execute("DELETE FROM recipe")
    db.execute("DELETE FROM user")

    user_ids: list[int] = []

    for user in USERS:
        pw = generate_password_hash(user)
        print(f"insert user: '{user}'")
        user = create_user(user, pw)
        user_ids.append(user.id)

    with open("recipes.json", encoding="utf-8") as recipes_json:
        recipe_data: list[Recipe] = json.load(recipes_json)

    for recipe in recipe_data:
        user_id = random.choice(user_ids)
        title = recipe["title"]
        ingredients = "\n".join(recipe["ingredients"])
        instructions = "\n".join(recipe["instructions"])
        print(f"insert recipe: '{title}'")
        create_recipe(RecipeForm(title, ingredients, instructions), user_id)


if __name__ == "__main__":
    main()
