import math

import db

from forms import ReviewForm


def get_reviews(recipe_id: int, exclude_user_id: int | None, page: int, page_size: int):
    count_sql = """
        SELECT count(id) AS row_count
        FROM review
        WHERE review.recipe_id = ?
    """
    query_sql = """
        SELECT
            review.id,
            review.user_id,
            review.created_at,
            review.title,
            review.content,
            review.rating,
            user.username
        FROM review
        INNER JOIN user ON review.user_id = user.id
        WHERE review.recipe_id = ?
    """
    params = [recipe_id]

    if exclude_user_id:
        count_sql += "AND review.user_id <> ?"
        query_sql += "AND review.user_id <> ?"
        params.append(exclude_user_id)

    row_count = db.query(count_sql, params)[0]["row_count"]
    page_count = math.ceil(row_count / page_size)

    query_sql += "LIMIT ? OFFSET ?"
    params.append(page_size)
    params.append((page - 1) * page_size)

    result = db.query(query_sql, params)

    return {
        "page": page,
        "page_count": page_count,
        "page_size": page_size,
        "row_count": row_count,
        "items": result,
    }


def get_reviews_by_user(user_id: int, page: int, page_size: int):
    count_sql = """
        SELECT count(id) as row_count
        FROM review
        WHERE review.user_id = ?
    """
    query_sql = """
        SELECT
            review.created_at,
            review.title,
            review.content,
            review.rating,
            recipe.id as recipe_id,
            recipe.title as recipe_title
        FROM review
        INNER JOIN recipe ON review.recipe_id = recipe.id
        WHERE review.user_id = ?
        ORDER BY datetime(review.created_at) DESC
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


def get_review_by_user(recipe_id: int, user_id: int):
    sql = """
        SELECT
            review.id,
            review.user_id,
            review.created_at,
            review.title,
            review.content,
            review.rating,
            user.username
        FROM review
        INNER JOIN user ON review.user_id = user.id
        WHERE review.recipe_id = ?
        AND review.user_id = ?
    """
    result = db.query(sql, [recipe_id, user_id])
    return result[0] if result else None


def create_review(form: ReviewForm, user_id: int, recipe_id: int) -> int:
    sql = """
        INSERT INTO review (
            user_id,
            recipe_id,
            created_at,
            title,
            content,
            rating
        )
        VALUES (?, ?, datetime('now'), ?, ?, ?)
    """
    result = db.execute(
        sql, [user_id, recipe_id, form.title, form.content, form.rating]
    )
    return result.lastrowid


def update_review(form: ReviewForm, user_id: int, recipe_id: int) -> bool:
    sql = """
        UPDATE review SET
            title = ?,
            content = ?,
            rating = ?
        WHERE user_id = ?
        AND recipe_id = ?
    """
    result = db.execute(
        sql, [form.title, form.content, form.rating, user_id, recipe_id]
    )
    return bool(result.rowcount)
