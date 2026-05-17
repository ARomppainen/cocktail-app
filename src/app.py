import os
import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import db

app = Flask(__name__)

if not (SECRET_KEY := os.environ.get("SECRET_KEY")):
    print("Environment variable SECRET_KEY not set!")
    os.abort()

app.secret_key = SECRET_KEY


@app.route("/", methods=["GET"])
def get_index():
    if "username" not in session:
        return redirect("/login")

    return render_template("index.html")


@app.route("/login", methods=["GET"])
def get_login():
    return render_template(
        "login.html",
    )


@app.route("/logout", methods=["POST"])
def post_logout():
    del session["username"]
    return redirect("/")


@app.route("/login", methods=["POST"])
def post_login():
    username = request.form["username"]
    password = request.form["password"]

    sql = "SELECT password_hash FROM user WHERE username = ?"
    password_hash = db.query(sql, [username])[0][0]

    if not check_password_hash(password_hash, password):
        return "ERROR: Incorrect username or password"

    session["username"] = username
    return redirect("/")


@app.route("/recipes", methods=["GET"])
def get_recipes():
    return render_template(
        "recipes.html",
    )


@app.route("/register", methods=["GET"])
def get_register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def post_register():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        return "ERROR: the passwords did not match"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO user (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "ERROR: the given account is already in use"

    session["username"] = username
    return redirect("/")
