import os
from typing import Any

from flask import Flask
from flask import abort, redirect, render_template, request, session
import markupsafe
from werkzeug.security import check_password_hash, generate_password_hash

import recipes
import reviews
import users

app = Flask(__name__)

if not (SECRET_KEY := os.environ.get("SECRET_KEY")):
    print("Environment variable SECRET_KEY not set!")
    os.abort()

app.secret_key = SECRET_KEY

BAD_REQUEST = 400
NOT_FOUND = 404


class Session:

    @staticmethod
    def log_in(user: users.User) -> None:
        session["user"] = users.LoggedInUser(id=user.id, username=user.username)

    @staticmethod
    def logged_in() -> bool:
        return "user" in session

    @staticmethod
    def log_out() -> None:
        del session["user"]

    @staticmethod
    def get_logged_in_user() -> users.LoggedInUser | None:
        return session["user"] if "user" in session else None


@app.template_filter()
def show_lines(content: str) -> markupsafe.Markup:
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)


@app.errorhandler(NOT_FOUND)
def not_found(error: Any):
    return render_template("not_found.html"), NOT_FOUND


@app.route("/", methods=["GET"])
def get_index_page():
    return render_template("index.html")


@app.route("/login", methods=["GET"])
def get_login_page():
    return render_template("login.html", form=users.LoginForm.empty())


@app.route("/login", methods=["POST"])
def log_in():
    form = users.LoginForm(
        username=request.form["username"], password=request.form["password"]
    )

    if validation_errors := form.validate():
        return (
            render_template(
                "login.html", form=form, validation_errors=validation_errors
            ),
            BAD_REQUEST,
        )

    user = users.get_user(form.username)

    if not user or not check_password_hash(user.password_hash, form.password):
        return (
            render_template(
                "login.html", form=form, error="Incorrect username or password"
            ),
            BAD_REQUEST,
        )

    Session.log_in(user)
    return redirect("/")


@app.route("/logout", methods=["POST"])
def log_out():
    if not Session.logged_in():
        return redirect("/login")
    Session.log_out()
    return redirect("/")


@app.route("/register", methods=["GET"])
def get_register_page():
    return render_template("register.html", form=users.CreateUserForm.empty())


@app.route("/register", methods=["POST"])
def register():
    form = users.CreateUserForm(
        username=request.form["username"],
        password1=request.form["password1"],
        password2=request.form["password2"],
    )

    if validation_errors := form.validate():
        return (
            render_template(
                "register.html", form=form, validation_errors=validation_errors
            ),
            BAD_REQUEST,
        )

    try:
        user = users.create_user(form.username, generate_password_hash(form.password1))
    except users.UsernameNotAvailableError:
        return (
            render_template(
                "register.html",
                form=form,
                validation_errors={"username": "Username not available"},
            ),
            BAD_REQUEST,
        )

    Session.log_in(user)
    return redirect("/")


@app.route("/recipes", methods=["GET"])
def get_recipes_page():
    form = recipes.RecipeSearchForm(query=request.args.get("query"))
    # TODO: validate query string

    search_result = recipes.search_recipes(form.query)

    return render_template("recipes.html", form=form, recipes=search_result)


@app.route("/recipes/new", methods=["GET"])
def get_new_recipe_page():
    if not Session.logged_in():
        return redirect("/login")
    return render_template("recipe_new.html", form=recipes.RecipeForm.empty())


@app.route("/recipes/new", methods=["POST"])
def create_new_recipe():
    user = Session.get_logged_in_user()
    if not user:
        return redirect("/login")

    form = recipes.RecipeForm(
        title=request.form["title"],
        ingredients=request.form["ingredients"],
        instructions=request.form["instructions"],
    )

    if validation_errors := form.validate():
        return (
            render_template(
                "recipe_new.html", form=form, validation_errors=validation_errors
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

    found_reviews = reviews.get_reviews(recipe_id, user_id)
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

    if user["id"] != recipe.user_id:
        abort(NOT_FOUND)

    form = recipes.RecipeForm(
        title=recipe.title,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
    )

    return render_template("recipe_update.html", recipe_id=recipe_id, form=form)


@app.route("/recipes/<int:recipe_id>/update", methods=["POST"])
def update_recipe(recipe_id: int):
    user = Session.get_logged_in_user()
    if not user:
        return redirect("/login")

    form = recipes.RecipeForm(
        title=request.form["title"],
        ingredients=request.form["ingredients"],
        instructions=request.form["instructions"],
    )

    if validation_errors := form.validate():
        return (
            render_template(
                "recipe_edit.html",
                recipe_id=recipe_id,
                form=form,
                validation_errors=validation_errors,
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

    if recipe.user_id == user["id"]:
        abort(BAD_REQUEST)

    return render_template(
        "review_new.html",
        recipe_id=recipe_id,
        recipe=recipe,
        form=reviews.ReviewForm.empty(),
    )


@app.route("/recipes/<int:recipe_id>/review/new", methods=["POST"])
def create_new_review(recipe_id: int):
    user = Session.get_logged_in_user()
    if not user:
        return redirect("/login")

    if reviews.get_review_by_user(recipe_id, user["id"]):
        abort(BAD_REQUEST)

    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(NOT_FOUND)

    if recipe.user_id == user["id"]:
        abort(BAD_REQUEST)

    form, validation_errors = reviews.ReviewForm.parse(request.form)

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

    if recipe.user_id == user["id"]:
        abort(BAD_REQUEST)

    review = reviews.get_review_by_user(recipe_id, user["id"])
    if not review:
        abort(NOT_FOUND)

    form = reviews.ReviewForm(
        title=review.title, content=review.content, rating=review.rating
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

    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(NOT_FOUND)

    if recipe.user_id == user["id"]:
        abort(BAD_REQUEST)

    form, validation_errors = reviews.ReviewForm.parse(request.form)
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
