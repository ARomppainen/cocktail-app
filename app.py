from datetime import datetime
import os
import secrets
from typing import Any

from flask import Flask
from flask import abort, redirect, render_template, request, session
import markupsafe
from werkzeug.security import check_password_hash, generate_password_hash

import forms
import recipes
import reviews
import users
import tags

app = Flask(__name__)

if not (SECRET_KEY := os.environ.get("SECRET_KEY")):
    print("Environment variable SECRET_KEY not set!")
    os.abort()

app.secret_key = SECRET_KEY

BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404


class Session:

    @staticmethod
    def log_in(user_id: int, username: str) -> None:
        session["user"] = {"id": user_id, "username": username}
        session["csrf_token"] = secrets.token_hex(16)

    @staticmethod
    def logged_in() -> bool:
        return "user" in session

    @staticmethod
    def log_out() -> None:
        del session["user"]

    @staticmethod
    def get_logged_in_user():
        return session["user"] if "user" in session else None

    @staticmethod
    def require_csrf_token() -> None:
        if "csrf_token" not in request.form:
            abort(FORBIDDEN)
        if request.form["csrf_token"] != session["csrf_token"]:
            abort(FORBIDDEN)


@app.template_filter()
def show_lines(content: str) -> markupsafe.Markup:
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)


@app.template_filter()
def format_datetime(value: str):
    parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    formatted = parsed.strftime("%B %d, %Y")
    return markupsafe.Markup(formatted)


@app.errorhandler(NOT_FOUND)
def not_found(error: Any):
    return render_template("not_found.html"), NOT_FOUND


@app.route("/", methods=["GET"])
def get_index_page():
    latest_recipes = recipes.get_latest_recipes(5)
    return render_template("index.html", recipes=latest_recipes)


@app.route("/login", methods=["GET"])
def get_login_page():
    return render_template("login.html", form=forms.LoginForm.empty())


@app.route("/login", methods=["POST"])
def log_in():
    form, validation_errors = forms.LoginForm.parse(request.form)

    if validation_errors:
        return (
            render_template(
                "login.html", form=form, validation_errors=validation_errors
            ),
            BAD_REQUEST,
        )

    user = users.get_user_by_name(form.username)

    if not user or not check_password_hash(user["password_hash"], form.password):
        return (
            render_template(
                "login.html", form=form, error="Incorrect username or password"
            ),
            BAD_REQUEST,
        )

    Session.log_in(user["id"], form.username)
    return redirect("/")


@app.route("/logout", methods=["POST"])
def log_out():
    if not Session.logged_in():
        return redirect("/login")
    Session.require_csrf_token()
    Session.log_out()
    return redirect("/")


@app.route("/register", methods=["GET"])
def get_register_page():
    return render_template("register.html", form=forms.CreateUserForm.empty())


@app.route("/register", methods=["POST"])
def register():
    form, validation_errors = forms.CreateUserForm.parse(request.form)

    if validation_errors:
        return (
            render_template(
                "register.html", form=form, validation_errors=validation_errors
            ),
            BAD_REQUEST,
        )

    try:
        user_id = users.create_user(
            form.username, generate_password_hash(form.password1)
        )
    except users.UsernameNotAvailableError:
        return (
            render_template(
                "register.html",
                form=form,
                validation_errors={"username": "Username not available"},
            ),
            BAD_REQUEST,
        )

    Session.log_in(user_id, form.username)
    return redirect("/")


@app.route("/recipes", methods=["GET"])
def get_recipes_page():
    form, validation_errors = forms.RecipeSearchForm.parse(request.args)
    page_size = 20

    if validation_errors:
        return (
            render_template(
                "recipes.html",
                form=form,
                recipes=[],
                page=form.page,
                page_count=0,
                page_size=page_size,
            ),
            BAD_REQUEST,
        )

    search_result = recipes.search_recipes(form.query, form.page, page_size)

    return render_template(
        "recipes.html",
        form=form,
        recipes=search_result["items"],
        page=search_result["page"],
        page_count=search_result["page_count"],
        page_size=search_result["page_size"],
    )


@app.route("/recipes/new", methods=["GET"])
def get_new_recipe_page():
    if not Session.logged_in():
        return redirect("/login")

    all_tags = tags.get_tags()

    return render_template(
        "recipe_new.html", form=forms.RecipeForm.empty(), tags=all_tags
    )


@app.route("/recipes/new", methods=["POST"])
def create_new_recipe():
    user = Session.get_logged_in_user()
    if not user:
        return redirect("/login")
    Session.require_csrf_token()

    all_tags = tags.get_tags()
    tag_ids = [tag["id"] for tag in all_tags]

    form, validation_errors = forms.RecipeForm.parse(request.form, tag_ids)

    if validation_errors:
        return (
            render_template(
                "recipe_new.html",
                form=form,
                validation_errors=validation_errors,
                tags=all_tags,
            ),
            BAD_REQUEST,
        )

    recipe_id = recipes.create_recipe(form, user["id"])

    return redirect(f"/recipes/{recipe_id}")


@app.route("/recipes/<int:recipe_id>", methods=["GET"])
def get_recipe_details_page(recipe_id: int):

    recipe = recipes.get_recipe(recipe_id)

    if not recipe:
        abort(NOT_FOUND)

    user = Session.get_logged_in_user()
    user_id = user["id"] if user else None

    page = max(1, request.args.get("page", default=1, type=int))

    found_reviews = reviews.get_reviews(recipe_id, user_id, page, 10)
    user_review = (
        reviews.get_review_by_user(recipe_id, user_id) if user_id is not None else None
    )

    return render_template(
        "recipe_details.html",
        recipe=recipe,
        reviews=found_reviews,
        user_review=user_review,
    )


@app.route("/recipes/<int:recipe_id>/update", methods=["GET"])
def get_recipe_update_page(recipe_id: int):
    user = Session.get_logged_in_user()
    if not user:
        return redirect("/login")

    recipe = recipes.get_recipe(recipe_id)

    if not recipe:
        abort(NOT_FOUND)

    if recipe["user_id"] != user["id"]:
        abort(NOT_FOUND)

    all_tags = tags.get_tags()
    recipe_tag_ids = tags.get_tag_ids_by_recipe(recipe_id)

    form = forms.RecipeForm(
        title=recipe["title"],
        ingredients=recipe["ingredients"],
        instructions=recipe["instructions"],
        tags=recipe_tag_ids,
    )

    return render_template(
        "recipe_update.html", recipe_id=recipe_id, form=form, tags=all_tags
    )


@app.route("/recipes/<int:recipe_id>/update", methods=["POST"])
def update_recipe(recipe_id: int):
    user = Session.get_logged_in_user()
    if not user:
        return redirect("/login")
    Session.require_csrf_token()

    all_tags = tags.get_tags()
    tag_ids = [tag["id"] for tag in all_tags]

    form, validation_errors = forms.RecipeForm.parse(request.form, tag_ids)

    if validation_errors:
        return (
            render_template(
                "recipe_update.html",
                recipe_id=recipe_id,
                form=form,
                validation_errors=validation_errors,
                tags=all_tags,
            ),
            BAD_REQUEST,
        )

    found = recipes.update_recipe(form, user["id"], recipe_id)

    if not found:
        abort(NOT_FOUND)

    return redirect(f"/recipes/{recipe_id}")


@app.route("/recipes/<int:recipe_id>/delete", methods=["POST"])
def delete_recipe(recipe_id: int):
    user = Session.get_logged_in_user()
    if not user:
        return redirect("/login")
    Session.require_csrf_token()

    recipes.delete_recipe(user["id"], recipe_id)

    return redirect("/recipes")


@app.route("/recipes/<int:recipe_id>/review/new", methods=["GET"])
def get_new_review_page(recipe_id: int):
    user = Session.get_logged_in_user()
    if not user:
        return redirect("/login")

    if reviews.get_review_by_user(recipe_id, user["id"]):
        abort(BAD_REQUEST)

    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(NOT_FOUND)

    if recipe["user_id"] == user["id"]:
        abort(BAD_REQUEST)

    return render_template(
        "review_new.html",
        recipe_id=recipe_id,
        recipe=recipe,
        form=forms.ReviewForm.empty(),
    )


@app.route("/recipes/<int:recipe_id>/review/new", methods=["POST"])
def create_new_review(recipe_id: int):
    user = Session.get_logged_in_user()
    if not user:
        return redirect("/login")
    Session.require_csrf_token()

    if reviews.get_review_by_user(recipe_id, user["id"]):
        abort(BAD_REQUEST)

    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(NOT_FOUND)

    if recipe["user_id"] == user["id"]:
        abort(BAD_REQUEST)

    form, validation_errors = forms.ReviewForm.parse(request.form)

    if validation_errors:
        return (
            render_template(
                "review_new.html",
                recipe_id=recipe_id,
                recipe=recipe,
                form=form,
                validation_errors=validation_errors,
            ),
            BAD_REQUEST,
        )

    reviews.create_review(form, user["id"], recipe_id)

    return redirect(f"/recipes/{recipe_id}")


@app.route("/recipes/<int:recipe_id>/review/update", methods=["GET"])
def get_review_update_page(recipe_id: int):
    user = Session.get_logged_in_user()
    if not user:
        return redirect("/login")

    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(NOT_FOUND)

    if recipe["user_id"] == user["id"]:
        abort(BAD_REQUEST)

    review = reviews.get_review_by_user(recipe_id, user["id"])
    if not review:
        abort(NOT_FOUND)

    form = forms.ReviewForm(
        title=review["title"], content=review["content"], rating=review["rating"]
    )

    return render_template(
        "review_update.html",
        recipe_id=recipe_id,
        recipe=recipe,
        form=form,
    )


@app.route("/recipes/<int:recipe_id>/review/update", methods=["POST"])
def update_review(recipe_id: int):
    user = Session.get_logged_in_user()
    if not user:
        return redirect("/login")
    Session.require_csrf_token()

    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(NOT_FOUND)

    if recipe["user_id"] == user["id"]:
        abort(BAD_REQUEST)

    form, validation_errors = forms.ReviewForm.parse(request.form)
    if validation_errors:
        return (
            render_template(
                "review_update.html",
                recipe_id=recipe_id,
                recipe=recipe,
                form=form,
                validation_errors=validation_errors,
            ),
            BAD_REQUEST,
        )

    found = reviews.update_review(form, user["id"], recipe_id)
    if not found:
        abort(NOT_FOUND)

    return redirect(f"/recipes/{recipe_id}")


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user_details_page(user_id: int):
    user = users.get_user(user_id)
    if not user:
        abort(NOT_FOUND)

    recipes_page = max(1, request.args.get("recipes_page", default=1, type=int))
    reviews_page = max(1, request.args.get("reviews_page", default=1, type=int))
    user_recipes = recipes.get_recipes_by_user(user_id, recipes_page, 20)
    user_reviews = reviews.get_reviews_by_user(user_id, reviews_page, 10)

    return render_template(
        "user_details.html", user=user, recipes=user_recipes, reviews=user_reviews
    )
