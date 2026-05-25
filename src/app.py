import os

from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from recipe.model import CreateRecipeForm
from recipe.queries import create_recipe
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


def log_in(user: User) -> None:
    session["user"] = LoggedInUser(id=user.id, username=user.username)


def logged_in() -> bool:
    return "user" in session


def log_out() -> None:
    del session["user"]


def get_logged_in_user() -> LoggedInUser | None:
    return session["user"] if "user" in session else None


@app.route("/", methods=["GET"])
def get_index():
    if not logged_in():
        return redirect("/login")

    return render_template("index.html")


@app.route("/login", methods=["GET"])
def get_login():
    return render_template("login.html", form=LoginForm.empty())


@app.route("/login", methods=["POST"])
def post_login():
    form = LoginForm(
        username=request.form["username"], password=request.form["password"]
    )

    if validation_errors := form.validate():
        return render_template(
            "login.html", form=form, validation_errors=validation_errors
        )

    user = get_user(form.username)

    if not user or not check_password_hash(user.password_hash, form.password):
        return render_template(
            "login.html", form=form, error="Incorrect username or password"
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
        return render_template(
            "register.html", form=form, validation_errors=validation_errors
        )

    try:
        user = create_user(form.username, generate_password_hash(form.password1))
    except UsernameNotAvailableError:
        return render_template(
            "register.html",
            form=form,
            validation_errors={"username": "Username not available"},
        )

    log_in(user)
    return redirect("/")


@app.route("/recipes/new", methods=["GET"])
def get_new_recipe():
    if not logged_in():
        return redirect("/login")
    return render_template("new_recipe.html", form=CreateRecipeForm.empty())


@app.route("/recipes/new", methods=["POST"])
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
        return render_template(
            "new_recipe.html", form=form, validation_errors=validation_errors
        )

    create_recipe(form, user["id"])

    return redirect("/")
