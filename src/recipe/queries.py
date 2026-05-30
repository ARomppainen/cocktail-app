import db
import sqlite3
from typing import Any

from recipe.model import RecipeForm, Recipe


def get_recipe(recipe_id: int) -> Recipe | None:
    sql = "SELECT id, user_id, created_at, title, ingredients, glass, instructions FROM recipe WHERE id = ?"
    result = db.query(sql, [recipe_id])
    return _to_recipe(result[0]) if len(result) else None


def get_recipes() -> list[Recipe]:
    sql = "SELECT id, user_id, created_at, title, ingredients, glass, instructions FROM recipe"
    result = db.query(sql)
    return [_to_recipe(row) for row in result]


def create_recipe(form: RecipeForm, user_id: int) -> None:
    sql = "INSERT INTO recipe (user_id, created_at, title, ingredients, glass, instructions) VALUES (?, datetime('now'), ?, ?, ?, ?)"
    db.execute(
        sql, [user_id, form.title, form.ingredients, form.glass, form.instructions]
    )


def update_recipe(form: RecipeForm, user_id: int, recipe_id: int) -> bool:
    sql = "UPDATE recipe SET title = ?, ingredients = ?, glass = ?, instructions = ? WHERE id = ? AND user_id = ?"
    result = db.execute(
        sql,
        [
            form.title,
            form.ingredients,
            form.glass,
            form.instructions,
            recipe_id,
            user_id,
        ],
    )
    return bool(result.rowcount)


def _to_recipe(row: Any) -> Recipe:
    return Recipe(
        id=row["id"],
        user_id=row["user_id"],
        created_at=row["created_at"],
        title=row["title"],
        ingredients=row["ingredients"],
        glass=row["glass"],
        instructions=row["instructions"],
    )
