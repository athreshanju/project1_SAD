import os
import sys
import time
from userReview import *

from test import bookreview
from users import *
import json
from flask import Flask, session, render_template, request,redirect,url_for
from sqlalchemy import create_engine,desc
import requests

# app = Flask(__name__, static_url_path='/static')
app = Flask(__name__)
app.secret_key = 'khammam'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
with app.app_context():
    db.create_all()


# Set up database
@app.route("/")
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for("register"))



@app.route("/register")
def register():
    return render_template("reg.html")


@app.route("/User",methods=["POST","GET"])
def User():

    if request.method == "POST":
        Username = request.form.get("username")
        Password = request.form.get("pass")
        Email = request.form.get("email")
        print(Username,file=sys.stderr)
        obj = user.query.filter_by(email = Email).first()
        if obj is None:
            usr = user(username = Username,email = Email,password = Password,time = time.ctime(time.time()))
            db.session.add(usr)
            db.session.commit()
            return render_template("pager.html",name = Username,email = Email)
        else:
            
            return render_template("reg.html", message = "email already exists!")
    if request.method == "GET":
        return "<h1> please register yourself </h1>"

@app.route("/admin")
def admin():
    adm = user.query.order_by(desc(user.time)).all()
    return render_template("admin.html",adm = adm)

@app.route("/auth",methods=["POST","GET"])
def auth():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("pass")

        userdata = user.query.filter_by(username=username).first()

        if userdata is not None:
            if userdata.username == username and userdata.password == password:
                session[username] = username
                return redirect(url_for('userhome',user=username))
            else:
                return render_template("reg.html", message = "username or password is incorrect")
        else:
            return redirect(url_for('index'))

    else:
        return "<h1> please login / register</h1>"

@app.route("/home/<user>")
def userhome(user):
    if user in session:
        return render_template("login.html",username = user,message="Sucessfully logged in : welcome!!")

    return redirect(url_for('index'))

@app.route("/logout/<username>")
def logout(username):
    print("Entered")
    session.pop(username, None)
    return redirect(url_for('index'))

@app.route("/bookpage",methods=["POST","GET"])
def bookspage():
    print("Entered in b")
    for key in session.keys():
        username = key
    if request.method == "POST":
        rating = request.form.get("rating")
        reviews = request.form.get("review")
        isbn = book.isbn
        timestamp = time.ctime(time.time())
        title = book.title
        user = review(isbn=isbn, review=reviews, rating=rating,
                      time_stamp=timestamp, title=title, username=username)
        db.session.add(user)
        db.session.commit()
        # Get all the reviews for the given book.
        allreviews = review.query.filter_by(isbn=bookisbn).all()
        return render_template("bookpage.html", res=res, book=book, review=allreviews, property="none", message="You reviewed this book!!")
    else:
        allreviews = review.query.filter_by(isbn=bookisbn).all()
        # database query to check if the user had given review to that paticular book.
        rev = review.query.filter(
            review.isbn == bookisbn, review.username == username).first()
        # if review was not given then dispaly the book page with review button
        if rev is None:
            return render_template("bookpage.html", book=book, review=allreviews, res=res,username=username)
        else:
            return render_template("bookpage.html", book=book, message="You reviewed this book!!", review=allreviews, res=res, property="none",username=username)


