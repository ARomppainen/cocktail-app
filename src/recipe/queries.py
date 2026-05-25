import db

from recipe.model import CreateRecipeForm


def create_recipe(form: CreateRecipeForm, user_id: str) -> None:
    sql = "INSERT INTO recipe (user_id, created_at, title, ingredients, glass, instructions) VALUES (?, datetime('now'), ?, ?, ?, ?)"
    db.execute(
        sql, [user_id, form.title, form.ingredients, form.glass, form.instructions]
    )
