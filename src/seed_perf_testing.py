import random
from typing import TypedDict

import db
from tags import get_tags

USER_COUNT = 1_000_000
RECIPE_COUNT = 1_000_000

LOREM = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Vestibulum ac mattis sapien.",
    "Aliquam sit amet semper lorem.",
    "Fusce vitae quam pretium, mattis sem nec, congue felis.",
    "Duis et est tincidunt, mattis odio luctus, semper arcu.",
    "Praesent nisi erat, molestie sit amet arcu vel, laoreet ullamcorper ante.",
    "Quisque hendrerit vel est quis gravida.",
    "Interdum et malesuada fames ac ante ipsum primis in faucibus.",
    "Suspendisse et lobortis nisi, dictum congue eros. Nulla et malesuada lacus.",
    "Suspendisse dictum viverra dui et auctor.",
    "Mauris cursus mauris in augue feugiat sagittis sed ut sapien.",
    "Duis sit amet purus vestibulum, faucibus lorem ut, consectetur odio.",
    "Mauris vestibulum turpis laoreet gravida accumsan.",
    "Ut risus augue, pharetra id justo eu, auctor dignissim lectus.",
    "Mauris eu blandit nunc.",
    "Nulla bibendum dui urna, sed blandit lorem luctus ut.",
    "Curabitur ac interdum lacus. ",
    "Nulla eu purus non mi venenatis tempor a eu nisi.",
    "Morbi sem nulla, tristique eget est eu, tristique congue ligula.",
    "Vestibulum ut eros et lorem tempor faucibus vel in nibh.",
    "Sed convallis ante quis posuere vestibulum.",
    "Duis luctus sit amet ligula a dignissim.",
    "Aliquam vitae convallis dolor.",
    "Sed finibus purus nisi, eget rhoncus dui eleifend ut.",
    "Etiam tempus mi vitae laoreet venenatis.",
    "Praesent sed venenatis quam.",
    "Sed turpis ligula, porta id nibh a, tincidunt pharetra urna.",
    "Integer quis egestas nulla.",
    "Etiam rutrum at felis vitae finibus.",
    "Maecenas consequat vehicula tincidunt.",
    "Sed sit amet tempor nulla, tincidunt consectetur velit.",
    "Aenean tempus posuere arcu ut venenatis.",
    "Duis id purus leo.",
    "In condimentum laoreet scelerisque.",
    "Suspendisse mauris diam, dictum ac lobortis at, dignissim vel mi.",
    "Sed facilisis blandit quam non rhoncus.",
]


class Recipe(TypedDict):
    id: str
    user_id: str


def _insert_users() -> None:
    connection = db.get_connection()
    for i in range(1, USER_COUNT + 1):
        user = str(i)
        pw = str(i)
        connection.execute(
            "INSERT INTO user (username, password_hash) VALUES (?, ?)", [user, pw]
        )
    connection.commit()
    connection.close()

    return [row["id"] for row in db.query("SELECT id FROM user")]


def _insert_recipes(user_ids: list[int]) -> list[Recipe]:
    connection = db.get_connection()
    for i in range(1, RECIPE_COUNT + 1):
        user_id = random.choice(user_ids)
        title = str(i)
        ingredients = "\n".join(random.sample(LOREM, k=2))
        instructions = "\n".join(random.sample(LOREM, k=2))
        connection.execute(
            """
            INSERT INTO recipe (
                user_id,
                created_at,
                title,
                ingredients,
                instructions
            )
            VALUES (?, datetime('now'), ?, ?, ?)
            """,
            [user_id, title, ingredients, instructions],
        )
    connection.commit()
    connection.close()

    return db.query("SELECT id, user_id FROM recipe")


def _insert_tags(recipes: list[Recipe]) -> None:
    tag_ids = [tag["id"] for tag in get_tags()]

    connection = db.get_connection()
    for recipe in recipes:
        tags = random.sample(
            tag_ids,
            k=random.randint(0, len(tag_ids)),
        )
        for tag_id in tags:
            connection.execute(
                """
                INSERT INTO recipe_tag (recipe_id, tag_id)
                VALUES (?, ?)
                """,
                [recipe["id"], tag_id],
            )
    connection.commit()
    connection.close()


def _insert_reviews(user_ids: int, recipes: list[Recipe]) -> None:
    connection = db.get_connection()

    recipe = recipes[0]

    for user_id in user_ids:
        if user_id == recipe["user_id"]:
            continue
        title = str(user_id)
        content = "\n".join(random.sample(LOREM, k=2))
        rating = random.choice([1, 2, 3, 4, 5])
        connection.execute(
            """
            INSERT INTO review (
                user_id,
                recipe_id,
                created_at,
                title,
                content,
                rating
            )
            VALUES (?, ?, datetime('now'), ?, ?, ?)
            """,
            [user_id, recipe["id"], title, content, rating],
        )
    connection.commit()
    connection.close()


def main() -> None:
    print("Deleting existing data...")
    db.execute("DELETE FROM recipe")
    db.execute("DELETE FROM user")
    print("Done!")

    print("Inserting users...")
    user_ids = _insert_users()
    print("Done!")

    print("Inserting recipes...")
    recipes = _insert_recipes(user_ids)
    print("Done!")

    print("Inserting tags...")
    _insert_tags(recipes)
    print("Done!")

    print("Inserting reviews...")
    _insert_reviews(user_ids, recipes)
    print("Done!")


if __name__ == "__main__":
    main()
