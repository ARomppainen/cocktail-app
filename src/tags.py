import db


def get_tags():
    sql = """
        SELECT id, name
        FROM tag
        ORDER BY name
    """
    return db.query(sql)


def get_tag_ids_by_recipe(recipe_id) -> list[int]:
    sql = """
        SELECT tag_id
        FROM recipe_tag
        WHERE recipe_id = ?
    """
    result = db.query(sql, [recipe_id])
    return [row["tag_id"] for row in result]
