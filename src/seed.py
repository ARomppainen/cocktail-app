import itertools
import json
import random
from typing import TypedDict

from werkzeug.security import generate_password_hash

import db
from recipes import create_recipe, RecipeForm
from reviews import create_review, ReviewForm
from users import create_user
from tags import get_tags

USERS = ["Alice", "Bob", "Charlie", "Diane"]


class Recipe(TypedDict):
    title: str
    ingredients: list[str]
    instructions: list[str]


class Review(TypedDict):
    title: str
    content: list[str]
    rating: int


def _insert_users() -> list[int]:
    user_ids: list[int] = []
    for user in USERS:
        pw = generate_password_hash(user)
        user_id = create_user(user, pw)
        user_ids.append(user_id)
    return user_ids


def _read_recipes() -> list[Recipe]:
    with open("seed_recipes.json", encoding="utf-8") as recipes_json:
        return json.load(recipes_json)


def _insert_recipes(user_ids: list[int]) -> list[tuple[int, int]]:
    recipe_data = _read_recipes()
    tag_ids = [tag["id"] for tag in get_tags()]

    created_recipes: list[tuple[int, int]] = []
    for recipe in recipe_data:
        user_id = random.choice(user_ids)
        title = recipe["title"]
        ingredients = "\n".join(recipe["ingredients"])
        instructions = "\n".join(recipe["instructions"])
        tags = random.sample(
            tag_ids,
            k=random.randint(0, len(tag_ids)),
        )

        recipe_id = create_recipe(
            RecipeForm(title, ingredients, instructions, tags), user_id
        )
        created_recipes.append((recipe_id, user_id))

    return created_recipes


def _read_reviews_by_category() -> dict[str, list[Review]]:
    with open("seed_reviews.json", encoding="utf-8") as reviews_json:
        review_data: list[Review] = json.load(reviews_json)

    review_data.sort(key=lambda row: row["rating"])
    reviews_by_rating: dict[int, list[Review]] = {}

    for k, g in itertools.groupby(review_data, key=lambda row: row["rating"]):
        reviews_by_rating[k] = list(g)

    return {
        "good": reviews_by_rating[4] + reviews_by_rating[5],
        "average": reviews_by_rating[2] + reviews_by_rating[3] + reviews_by_rating[4],
        "bad": reviews_by_rating[1] + reviews_by_rating[2],
    }


def _insert_reviews(
    user_ids: list[int], created_recipes: list[tuple[int, int]]
) -> None:
    reviews_by_category = _read_reviews_by_category()

    for recipe_id, user_id in created_recipes:
        other_user_ids = [x for x in user_ids if x != user_id]
        category = random.choice(["good", "average", "bad"])
        for i, review in enumerate(
            random.sample(reviews_by_category[category], k=len(other_user_ids))
        ):
            title = review["title"]
            content = "\n".join(review["content"])
            rating = review["rating"]
            create_review(
                ReviewForm(title, content, rating), other_user_ids[i], recipe_id
            )


def main() -> None:
    print("Deleting existing data...")
    db.execute("DELETE FROM recipe")
    db.execute("DELETE FROM user")
    print("Done!")

    print("Inserting users...")
    user_ids = _insert_users()
    print("Done!")

    print("Inserting recipes...")
    created_recipes = _insert_recipes(user_ids)
    print("Done!")

    print("Inserting reviews...")
    _insert_reviews(user_ids, created_recipes)
    print("Done!")


if __name__ == "__main__":
    main()
