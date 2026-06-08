from dataclasses import dataclass
from typing import Any

from werkzeug.datastructures import ImmutableMultiDict

import db


@dataclass(frozen=True)
class Review:
    id: int
    user_id: int
    username: str
    created_at: str
    title: str
    content: str
    rating: int


@dataclass(frozen=True)
class UserReview:
    created_at: str
    title: str
    content: str
    rating: int
    recipe_id: int
    recipe_title: str


@dataclass(frozen=True)
class ReviewForm:
    title: str
    content: str
    rating: int

    @staticmethod
    def empty() -> "ReviewForm":
        return ReviewForm("", "", 0)

    @staticmethod
    def parse(
        form: ImmutableMultiDict[str, str],
    ) -> tuple["ReviewForm", dict[str, str]]:
        errors: dict[str, str] = {}

        title = form["title"]
        content = form["content"]
        rating = form.get("rating", type=int)

        # TODO: Add validation

        return ReviewForm(title=title, content=content, rating=rating), errors


def get_reviews(recipe_id: int, exclude_user_id: int | None) -> list[Review]:
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
    """
    params = [recipe_id]

    if exclude_user_id is not None:
        sql += " AND review.user_id <> ?"
        params.append(exclude_user_id)

    result = db.query(sql, params)
    return [_to_review(row) for row in result]


def get_reviews_by_user(user_id: int) -> list[UserReview]:
    sql = """
        SELECT
            review.created_at,
            review.title,
            review.content,
            review.rating,
            recipe.id as recipe_id,
            recipe.title as recipe_title
        FROM review
        INNER JOIN recipe ON review.recipe_id = recipe.id
        WHERE review.recipe_id = ?
        ORDER BY datetime(review.created_at) DESC
    """
    result = db.query(sql, [user_id])
    return [_to_user_review(row) for row in result]


def get_review_by_user(recipe_id: int, user_id: int) -> Review | None:
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
    return _to_review(result[0]) if result else None


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


def _to_review(row: Any) -> Review:
    return Review(
        id=row["id"],
        user_id=row["user_id"],
        username=row["username"],
        created_at=row["created_at"],
        title=row["title"],
        content=row["content"],
        rating=row["rating"],
    )


def _to_user_review(row: Any) -> UserReview:
    return UserReview(
        created_at=row["created_at"],
        title=row["title"],
        content=row["content"],
        rating=row["rating"],
        recipe_id=row["recipe_id"],
        recipe_title=row["recipe_title"],
    )
