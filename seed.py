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


def main() -> None:
    print("Deleting existing data...")
    db.execute("DELETE FROM recipe")
    db.execute("DELETE FROM user")
    print("Done!")

    user_ids: list[int] = []

    print("Inserting users...")
    for user in USERS:
        pw = generate_password_hash(user)
        user = create_user(user, pw)
        user_ids.append(user.id)
    print("Done!")

    with open("seed_recipes.json", encoding="utf-8") as recipes_json:
        recipe_data: list[Recipe] = json.load(recipes_json)

    tag_ids = [tag.id for tag in get_tags()]

    created_recipes: list[tuple[int, int]] = []
    print("Inserting recipes...")
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
    print("Done!")

    with open("seed_reviews.json", encoding="utf-8") as reviews_json:
        review_data: list[Review] = json.load(reviews_json)

    review_data.sort(key=lambda row: row["rating"])
    reviews_by_rating: dict[int, list[Review]] = {}

    for k, g in itertools.groupby(review_data, key=lambda row: row["rating"]):
        reviews_by_rating[k] = list(g)

    reviews_by_category = {
        "good": reviews_by_rating[4] + reviews_by_rating[5],
        "average": reviews_by_rating[2] + reviews_by_rating[3] + reviews_by_rating[4],
        "bad": reviews_by_rating[1] + reviews_by_rating[2],
    }

    print("Inserting reviews...")
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
    print("Done!")


if __name__ == "__main__":
    main()
