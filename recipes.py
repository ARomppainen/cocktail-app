from dataclasses import dataclass
from typing import Any

import db


@dataclass(frozen=True)
class Recipe:
    id: int
    user_id: int
    created_at: str
    title: str
    ingredients: str
    instructions: str


@dataclass(frozen=True)
class RecipeSearchItem:
    id: int
    user_id: int
    username: str
    created_at: str
    title: str


@dataclass(frozen=True)
class RecipeForm:
    title: str
    ingredients: str
    instructions: str

    @staticmethod
    def empty() -> "RecipeForm":
        return RecipeForm("", "", "")

    def validate(self) -> dict[str, str]:
        errors: dict[str, str] = {}

        if not self.title:
            errors["title"] = "Value is required"

        if not self.ingredients:
            errors["ingredients"] = "Value is required"

        if not self.instructions:
            errors["instructions"] = "Value is required"

        return errors


@dataclass(frozen=True)
class RecipeSearchForm:
    query: str | None


def get_recipe(recipe_id: int) -> Recipe | None:
    sql = "SELECT id, user_id, created_at, title, ingredients, instructions FROM recipe WHERE id = ?"
    result = db.query(sql, [recipe_id])
    return _to_recipe(result[0]) if len(result) else None


def search_recipes(query: str) -> list[RecipeSearchItem]:
    if not query:
        return _get_recipes()

    sql = """
        SELECT
          recipe.id,
          recipe.user_id,
          recipe.created_at,
          recipe.title,
          user.username
        FROM recipe
        INNER JOIN user ON recipe.user_id = user.id
        WHERE title LIKE ?
        OR ingredients LIKE ?
        OR instructions LIKE ?
    """
    q = f"%{query}%"
    result = db.query(sql, [q, q, q])
    return [_to_recipe_search_item(row) for row in result]


def _get_recipes() -> list[RecipeSearchItem]:
    sql = """
        SELECT
          recipe.id,
          recipe.user_id,
          recipe.created_at,
          recipe.title,
          user.username
        FROM recipe
        INNER JOIN user ON recipe.user_id = user.id
    """
    result = db.query(sql)
    return [_to_recipe_search_item(row) for row in result]


def create_recipe(form: RecipeForm, user_id: int) -> int:
    sql = "INSERT INTO recipe (user_id, created_at, title, ingredients, instructions) VALUES (?, datetime('now'), ?, ?, ?)"
    result = db.execute(sql, [user_id, form.title, form.ingredients, form.instructions])
    return result.lastrowid


def update_recipe(form: RecipeForm, user_id: int, recipe_id: int) -> bool:
    sql = "UPDATE recipe SET title = ?, ingredients = ?, instructions = ? WHERE id = ? AND user_id = ?"
    result = db.execute(
        sql,
        [
            form.title,
            form.ingredients,
            form.instructions,
            recipe_id,
            user_id,
        ],
    )
    return bool(result.rowcount)


def delete_recipe(user_id: int, recipe_id: int) -> None:
    sql = "DELETE FROM recipe WHERE id = ? AND user_id = ?"
    db.execute(sql, [recipe_id, user_id])


def _to_recipe(row: Any) -> Recipe:
    return Recipe(
        id=row["id"],
        user_id=row["user_id"],
        created_at=row["created_at"],
        title=row["title"],
        ingredients=row["ingredients"],
        instructions=row["instructions"],
    )


def _to_recipe_search_item(row: Any) -> RecipeSearchItem:
    return RecipeSearchItem(
        id=row["id"],
        user_id=row["user_id"],
        username=row["username"],
        created_at=row["created_at"],
        title=row["title"],
    )
