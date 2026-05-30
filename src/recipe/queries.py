import db
from typing import Any

from recipe.model import CreateRecipeForm, Recipe


def get_recipe(recipe_id: int) -> Recipe | None:
    sql = "SELECT id, user_id, created_at, title, ingredients, glass, instructions FROM recipe WHERE id = ?"
    result = db.query(sql, [recipe_id])
    return _to_recipe(result[0]) if len(result) else None


def get_recipes() -> list[Recipe]:
    sql = "SELECT id, user_id, created_at, title, ingredients, glass, instructions FROM recipe"
    result = db.query(sql)
    return [_to_recipe(row) for row in result]


def create_recipe(form: CreateRecipeForm, user_id: str) -> None:
    sql = "INSERT INTO recipe (user_id, created_at, title, ingredients, glass, instructions) VALUES (?, datetime('now'), ?, ?, ?, ?)"
    db.execute(
        sql, [user_id, form.title, form.ingredients, form.glass, form.instructions]
    )


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
