from dataclasses import dataclass
import math
from typing import Any, Generic, TypeVar

from werkzeug.datastructures import ImmutableMultiDict

import db
from tags import Tag

T = TypeVar("T")


@dataclass(frozen=True)
class Recipe:
    id: int
    user_id: int
    created_at: str
    title: str
    ingredients: str
    instructions: str
    tags: str


@dataclass(frozen=True)
class RecipeSearchItem:
    id: int
    user_id: int
    username: str
    created_at: str
    title: str
    tags: str


@dataclass(frozen=True)
class PaginatedResult(Generic[T]):
    page: int
    page_count: int
    page_size: int
    row_count: int
    items: list[T]


@dataclass(frozen=True)
class RecipeForm:
    title: str
    ingredients: str
    instructions: str
    tags: list[int]

    @staticmethod
    def empty() -> "RecipeForm":
        return RecipeForm("", "", "", [])

    @staticmethod
    def parse(
        form: ImmutableMultiDict[str, str], valid_tags: list[Tag]
    ) -> tuple["RecipeForm", dict[str, str]]:
        errors: dict[str, str] = {}

        title = form["title"]
        ingredients = form["ingredients"]
        instructions = form["instructions"]
        tags = set(form.getlist("tags", type=int))

        # TODO: validate maximum field length

        if not title:
            errors["title"] = "Value is required"

        if not ingredients:
            errors["ingredients"] = "Value is required"

        if not instructions:
            errors["instructions"] = "Value is required"

        valid_tag_ids = list(tag.id for tag in valid_tags)
        if not tags.issubset(valid_tag_ids):
            errors["tags"] = "Invalid tag detected"

        return (
            RecipeForm(
                title=title,
                ingredients=ingredients,
                instructions=instructions,
                tags=list(tags),
            ),
            errors,
        )


@dataclass(frozen=True)
class RecipeSearchForm:
    query: str | None


def get_recipe(recipe_id: int) -> Recipe | None:
    sql = """
        SELECT
            recipe.id,
            recipe.user_id,
            recipe.created_at,
            recipe.title,
            recipe.ingredients,
            recipe.instructions,
            group_concat(tag.name, ', ') as tags
        FROM recipe
        LEFT JOIN recipe_tag ON recipe.id = recipe_tag.recipe_id
        LEFT JOIN tag ON recipe_tag.tag_id = tag.id
        WHERE recipe.id = ?
        GROUP BY recipe.id
        ORDER BY tag.name
    """
    result = db.query(sql, [recipe_id])
    return _to_recipe(result[0]) if result else None


def get_recipes_by_user(
    user_id: int, page: int, page_size: int
) -> PaginatedResult[Recipe]:
    count_sql = """
        SELECT count(id) as row_count
        FROM recipe
        WHERE recipe.user_id = ?
    """
    query_sql = """
        SELECT
            recipe.id,
            recipe.user_id,
            recipe.created_at,
            recipe.title,
            recipe.ingredients,
            recipe.instructions,
            group_concat(tag.name, ', ') as tags
        FROM recipe
        LEFT JOIN recipe_tag ON recipe.id = recipe_tag.recipe_id
        LEFT JOIN tag ON recipe_tag.tag_id = tag.id
        WHERE recipe.user_id = ?
        GROUP BY recipe.id
        ORDER BY datetime(created_at) DESC, tag.name
        LIMIT ? OFFSET ?
    """
    row_count = db.query(count_sql, [user_id])[0]["row_count"]
    page_count = math.ceil(row_count / page_size)

    result = db.query(query_sql, [user_id, page_size, (page - 1) * page_size])
    items = [_to_recipe(row) for row in result]

    return PaginatedResult(
        page=page,
        page_count=page_count,
        page_size=page_size,
        row_count=row_count,
        items=items,
    )


def search_recipes(
    query: str, page: int, page_size: int
) -> PaginatedResult[RecipeSearchItem]:
    count_sql = """
        SELECT count(id) as row_count
        FROM recipe
    """
    search_sql = """
        SELECT
            recipe.id,
            recipe.user_id,
            recipe.created_at,
            recipe.title,
            user.username,
            group_concat(tag.name, ', ') as tags
        FROM recipe
        INNER JOIN user ON recipe.user_id = user.id
        LEFT JOIN recipe_tag ON recipe.id = recipe_tag.recipe_id
        LEFT JOIN tag ON recipe_tag.tag_id = tag.id
    """
    filter_sql = """
        WHERE title LIKE ?
        OR ingredients LIKE ?
        OR instructions LIKE ?
    """

    params = []
    if query:
        count_sql += filter_sql
        search_sql += filter_sql
        q = f"%{query}%"
        params = [q, q, q]

    row_count = db.query(count_sql, params)[0]["row_count"]
    page_count = math.ceil(row_count / page_size)

    search_sql += """
        GROUP BY recipe.id
        ORDER BY recipe.title
        LIMIT ? OFFSET ?
    """
    params.append(page_size)
    params.append((page - 1) * page_size)

    result = db.query(search_sql, params)
    items = [_to_recipe_search_item(row) for row in result]

    return PaginatedResult(
        page=page,
        page_count=page_count,
        page_size=page_size,
        row_count=row_count,
        items=items,
    )


def create_recipe(form: RecipeForm, user_id: int) -> int:
    connection = db.get_connection()
    recipe_insert_sql = """
        INSERT INTO recipe (
            user_id,
            created_at,
            title,
            ingredients,
            instructions
        )
        VALUES (?, datetime('now'), ?, ?, ?)
    """
    result = connection.execute(
        recipe_insert_sql, [user_id, form.title, form.ingredients, form.instructions]
    )
    recipe_id = result.lastrowid

    tag_insert_sql = """
        INSERT INTO recipe_tag (recipe_id, tag_id)
        VALUES (?, ?)
    """
    for tag_id in form.tags:
        connection.execute(tag_insert_sql, [recipe_id, tag_id])

    connection.commit()
    connection.close()
    return recipe_id


def update_recipe(form: RecipeForm, user_id: int, recipe_id: int) -> bool:
    connection = db.get_connection()
    recipe_update_sql = """
        UPDATE recipe
        SET
            title = ?,
            ingredients = ?,
            instructions = ?
        WHERE id = ?
        AND user_id = ?
    """
    result = connection.execute(
        recipe_update_sql,
        [
            form.title,
            form.ingredients,
            form.instructions,
            recipe_id,
            user_id,
        ],
    )
    if not bool(result.rowcount):
        connection.commit()
        connection.close()
        return False

    tag_delete_sql = "DELETE FROM recipe_tag WHERE recipe_id = ?"
    connection.execute(tag_delete_sql, [recipe_id])

    tag_insert_sql = """
        INSERT INTO recipe_tag (recipe_id, tag_id)
        VALUES (?, ?)
    """
    for tag_id in form.tags:
        connection.execute(tag_insert_sql, [recipe_id, tag_id])

    connection.commit()
    connection.close()
    return True


def delete_recipe(user_id: int, recipe_id: int) -> None:
    sql = """
        DELETE FROM recipe
        WHERE id = ?
        AND user_id = ?
    """
    db.execute(sql, [recipe_id, user_id])


def _to_recipe(row: Any) -> Recipe:
    return Recipe(
        id=row["id"],
        user_id=row["user_id"],
        created_at=row["created_at"],
        title=row["title"],
        ingredients=row["ingredients"],
        instructions=row["instructions"],
        tags=row["tags"],
    )


def _to_recipe_search_item(row: Any) -> RecipeSearchItem:
    return RecipeSearchItem(
        id=row["id"],
        user_id=row["user_id"],
        username=row["username"],
        created_at=row["created_at"],
        title=row["title"],
        tags=row["tags"],
    )
