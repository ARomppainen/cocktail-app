from dataclasses import dataclass
from typing import Any

import db


@dataclass(frozen=True)
class Tag:
    id: int
    name: str


def get_tags() -> list[Tag]:
    sql = "SELECT id, name FROM tag ORDER BY name"
    result = db.query(sql)
    return [_to_tag(row) for row in result]


def get_tags_by_recipe(recipe_id) -> list[int]:
    sql = """
        SELECT tag_id
        FROM recipe_tag
        WHERE recipe_id = ?
    """
    result = db.query(sql, [recipe_id])
    return [row["tag_id"] for row in result]


def _to_tag(row: Any) -> Tag:
    return Tag(row["id"], row["name"])
