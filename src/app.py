import os
from typing import Any

from flask import Flask
from flask import abort, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from recipe.model import CreateRecipeForm
import recipe.queries as recipe_queries
from user.model import (
    CreateUserForm,
    LoggedInUser,
    LoginForm,
    User,
    UsernameNotAvailableError,
)
from user.queries import create_user, get_user

app = Flask(__name__)

if not (SECRET_KEY := os.environ.get("SECRET_KEY")):
    print("Environment variable SECRET_KEY not set!")
    os.abort()

app.secret_key = SECRET_KEY

BAD_REQUEST = 400
NOT_FOUND = 404


def log_in(user: User) -> None:
    session["user"] = LoggedInUser(id=user.id, username=user.username)


def logged_in() -> bool:
    return "user" in session


def log_out() -> None:
    del session["user"]


def get_logged_in_user() -> LoggedInUser | None:
    return session["user"] if "user" in session else None


@app.errorhandler(NOT_FOUND)
def not_found(error: Any):
    return render_template("not_found.html"), NOT_FOUND


@app.route("/", methods=["GET"])
def get_index():
    if not logged_in():
        return redirect("/login")
    recipes = recipe_queries.get_recipes()
    return render_template("index.html", recipes=recipes)


@app.route("/login", methods=["GET"])
def get_login():
    return render_template("login.html", form=LoginForm.empty())


@app.route("/login", methods=["POST"])
def post_login():
    form = LoginForm(
        username=request.form["username"], password=request.form["password"]
    )

    if validation_errors := form.validate():
        return (
            render_template(
                "login.html", form=form, validation_errors=validation_errors
            ),
            BAD_REQUEST,
        )

    user = get_user(form.username)

    if not user or not check_password_hash(user.password_hash, form.password):
        return (
            render_template(
                "login.html", form=form, error="Incorrect username or password"
            ),
            BAD_REQUEST,
        )

    log_in(user)
    return redirect("/")


@app.route("/logout", methods=["POST"])
def post_logout():
    if not logged_in():
        return redirect("/login")
    log_out()
    return redirect("/")


@app.route("/register", methods=["GET"])
def get_register():
    return render_template("register.html", form=CreateUserForm.empty())


@app.route("/register", methods=["POST"])
def post_register():
    form = CreateUserForm(
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
        user = create_user(form.username, generate_password_hash(form.password1))
    except UsernameNotAvailableError:
        return (
            render_template(
                "register.html",
                form=form,
                validation_errors={"username": "Username not available"},
            ),
            BAD_REQUEST,
        )

    log_in(user)
    return redirect("/")


@app.route("/recipe", methods=["GET"])
def get_new_recipe():
    if not logged_in():
        return redirect("/login")
    return render_template("new_recipe.html", form=CreateRecipeForm.empty())


@app.route("/recipe", methods=["POST"])
def post_recipe():
    user = get_logged_in_user()
    if not user:
        return redirect("/login")

    form = CreateRecipeForm(
        title=request.form["title"],
        ingredients=request.form["ingredients"],
        glass=request.form["glass"],
        instructions=request.form["instructions"],
    )

    if validation_errors := form.validate():
        return (
            render_template(
                "new_recipe.html", form=form, validation_errors=validation_errors
            ),
            BAD_REQUEST,
        )

    recipe_queries.create_recipe(form, user["id"])

    return redirect("/")


@app.route("/recipe/<int:recipe_id>", methods=["GET"])
def get_recipe(recipe_id: int):
    if not logged_in():
        return redirect("/login")

    recipe = recipe_queries.get_recipe(recipe_id)

    if not recipe:
        abort(NOT_FOUND)

    return render_template("recipe_details.html", recipe=recipe)
