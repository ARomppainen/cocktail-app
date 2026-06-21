import math

import db

from forms import RecipeForm


def get_recipe(recipe_id: int):
    sql = """
        SELECT
            recipe.id,
            recipe.user_id,
            recipe.created_at,
            recipe.title,
            recipe.ingredients,
            recipe.instructions,
            user.id as user_id,
            user.username,
            (
                SELECT group_concat(tag.name, ', ')
                FROM tag
                INNER JOIN recipe_tag ON tag.id = recipe_tag.tag_id
                WHERE recipe_tag.recipe_id = recipe.id
            ) tags,
            (
                SELECT avg(review.rating)
                FROM review
                WHERE review.recipe_id = recipe.id
            ) avg_rating
        FROM recipe
        INNER JOIN user ON recipe.user_id = user.id
        WHERE recipe.id = ?
    """
    result = db.query(sql, [recipe_id])
    return result[0] if result else None


def get_recipes_by_user(user_id: int, page: int, page_size: int):
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
            (
                SELECT group_concat(tag.name, ', ')
                FROM tag
                INNER JOIN recipe_tag ON tag.id = recipe_tag.tag_id
                WHERE recipe_tag.recipe_id = recipe.id
            ) tags,
            (
                SELECT avg(review.rating)
                FROM review
                WHERE review.recipe_id = recipe.id
            ) avg_rating
        FROM recipe
        WHERE recipe.user_id = ?
        ORDER BY datetime(recipe.created_at) DESC
        LIMIT ? OFFSET ?
    """
    row_count = db.query(count_sql, [user_id])[0]["row_count"]
    page_count = math.ceil(row_count / page_size)

    result = db.query(query_sql, [user_id, page_size, (page - 1) * page_size])

    return {
        "page": page,
        "page_count": page_count,
        "page_size": page_size,
        "row_count": row_count,
        "items": result,
    }


def get_latest_recipes(n: int):
    sql = """
        SELECT
            recipe.id,
            recipe.user_id,
            recipe.created_at,
            recipe.title,
            recipe.ingredients,
            recipe.instructions,
            user.id as user_id,
            user.username,
            (
                SELECT group_concat(tag.name, ', ')
                FROM tag
                INNER JOIN recipe_tag ON tag.id = recipe_tag.tag_id
                WHERE recipe_tag.recipe_id = recipe.id
            ) tags,
            (
                SELECT avg(review.rating)
                FROM review
                WHERE review.recipe_id = recipe.id
            ) avg_rating
        FROM recipe
        INNER JOIN user ON recipe.user_id = user.id
        ORDER BY datetime(recipe.created_at) DESC
        LIMIT ?
    """
    return db.query(sql, [n])


def search_recipes(query: str, page: int, page_size: int):
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
            (
                SELECT group_concat(tag.name, ', ')
                FROM tag
                INNER JOIN recipe_tag ON tag.id = recipe_tag.tag_id
                WHERE recipe_tag.recipe_id = recipe.id
            ) tags,
            (
                SELECT avg(review.rating)
                FROM review
                WHERE review.recipe_id = recipe.id
            ) avg_rating
        FROM recipe
        INNER JOIN user ON recipe.user_id = user.id
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
        ORDER BY recipe.title
        LIMIT ? OFFSET ?
    """
    params.append(page_size)
    params.append((page - 1) * page_size)

    result = db.query(search_sql, params)

    return {
        "page": page,
        "page_count": page_count,
        "page_size": page_size,
        "row_count": row_count,
        "items": result,
    }


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
