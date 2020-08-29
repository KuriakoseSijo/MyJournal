import os
import json
from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

dateTimeObj = datetime.now()
timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///journal.db")


@app.route("/")
@login_required
def index():
    if request.method == "GET":
        current_user_posts = db.execute("SELECT title, post FROM posts WHERE user_id =:user_id", user_id=session["user_id"])
        length = len(current_user_posts)
        if length==0:
            return render_template("index.html", length=length,current_user_posts=current_user_posts, current_posts= "No Posts")
        else:
            return render_template("index.html", length=length,current_user_posts=current_user_posts )
    else:
        return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return (render_template("register.html"))
    else:
        # gets the user name from the form
        username = request.form.get("username")
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        # error messages if user name or password not given
        if not username:
            return apology("You must provide a user name", 403)
        # checks if user name is taken
        if len(rows) >= 1:
            return apology("Sorry the user name is taken", 403)

        if not request.form.get("password1") or not request.form.get("password2"):
            return apology("You must provide a password", 403)

        # if both passwors match hash the pasword and save it to database
        if request.form.get("password1") == request.form.get("password2"):
            hash = generate_password_hash(request.form.get("password1"))
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=hash)
            flash("Registered!")
            return redirect("/")
        else:
            return apology("The Password must match", 403)


@app.route("/compose", methods=["GET", "POST"])
def compose():
    """Register user"""
    if request.method == "GET":
        return (render_template("compose.html"))

    if request.method == "POST":
        db.execute("INSERT INTO posts (user_id, title, post) VALUES (:user_id, :title, :post )",
               user_id=session["user_id"], title=request.form.get("postTitle"), post=request.form.get("postBody"))
        flash("Success! journal posted")
        return redirect("/")
    else:
        return redirect("/")

@app.route("/posts/<int:post_num>", methods=["GET", "POST"])
def posts(post_num):
    """post views"""
    current_user_posts = db.execute("SELECT title, post FROM posts WHERE user_id =:user_id", user_id=session["user_id"])
    if request.method == "GET":
        title = current_user_posts[(post_num)]['title']
        post = current_user_posts[(post_num)]['post']
        #print(title)
        #print(post_num)
        return render_template("posts.html", title=title,post=post,post_num=post_num )

    if request.method == "POST":
        title = current_user_posts[(post_num)]['title']
        db.execute("DELETE FROM posts WHERE title = :title AND user_id =:user_id", user_id=session["user_id"], title=title)
        print(title)
        flash("Post deleted!")
        return redirect("/")
    else:
        return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
