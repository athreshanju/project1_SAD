import os
import sys
import time
from users import *
from flask import Flask, session, render_template, request,redirect,url_for,jsonify
from sqlalchemy import create_engine,desc,or_
from booksdb import *
import requests
from userReview import *
from books import *
from test import bookreview
import json
from flask import jsonify
from flask import Flask, session, render_template, request,redirect,url_for

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
    try:
        user = session['username']
        return redirect(url_for('home'))
    except:
        return redirect(url_for("register"))

@app.route("/register",methods=["POST","GET"])
def register():
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
            return render_template("reg.html",message = "Successfully registered !! please login")
        else:
            
            return render_template("reg.html", message = "email already exists!")
    if request.method == "GET":
        return render_template("reg.html")

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
                session["username"] = username
                return redirect(url_for('userhome'))
            else:
                return render_template("reg.html", message = "username or password is incorrect")
        else:
            return redirect(url_for('index'))

    else:
        return redirect(url_for('index'))

@app.route("/home")
def userhome():
    try:
        user = session['username']
        return render_template("login.html",username = user,message="Sucessfully logged in : welcome!!")
    except Exception as e:
        print (e)    
        return redirect(url_for('index'))

@app.route("/logout")
def logout():
    try:
        session.clear()
        return redirect(url_for('index'))
    except:
        return redirect(url_for('index'))

@app.route("/search",methods=["POST","GET"])
def search():
    try:
        username = session['username']
        if request.method=="POST":
            if not request.form.get("book"):
                return render_template("login.html",msg = "please search a book by its title or isbn or author or year",username=username)
            book = request.form.get("book")
            bookreq = str(book)
            booksdata = db.session.query(Books.isbn,Books.title,Books.author,Books.year).filter(or_(Books.title.like("%"+bookreq+"%"),Books.author.like("%"+bookreq+"%"),Books.isbn.like("%"+bookreq+"%"),Books.year.like("%"+bookreq+"%"))).all()
            if booksdata.__len__()==0:
                return render_template("login.html",msg = "we could not find books with your search!",username = username)
            else:
                return render_template("login.html",books=booksdata,username=username)
    except:
        return redirect(url_for('index'))

@app.route("/bookpage/<isbn>",methods=["POST","GET"])
def bookspage(isbn):
    try:
        
        username = session['username']
        book = db.session.query(Books).filter(Books.isbn==isbn).first()
        allreviews = review.query.filter_by(isbn=isbn).all()
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "2VIV9mRWiAq0OuKcOPiA", "isbns": book.isbn})
        data = res.text
        parsed = json.loads(data)
        print(parsed)
        res = {}
        for i in parsed:
            for j in (parsed[i]):
                res = j
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
            allreviews = review.query.filter_by(isbn=isbn).all()
            return render_template("bookpage.html", book=book, review=allreviews, property="none", res=res,message="You reviewed this book!!")
        else:
            # database query to check if the user had given review to that paticular book.
            rev = review.query.filter(
                review.isbn == book.isbn, review.username == username).first()
            # if review was not given then dispaly the book page with review button
            if rev is None:
                return render_template("bookpage.html", book=book, review=allreviews,res=res, username=username)
            else:
                return render_template("bookpage.html", book=book, message="You reviewed this book!!", review=allreviews,res=res,property="none",username=username)
    except Exception as e:
        print(e)
        return redirect(url_for('index'))


@app.route('/api/book')
def apibook():
    bookrequest = request.args.get('isbn')
    
    try:
        result = db.session.query(Books).filter(Books.isbn == bookrequest).first()
        
        r=review.query.filter_by(isbn=bookrequest).all()
        
    except Exception as e:
        print(e)
        message = "Please Try again Later"
        return jsonify(message),500
    
    if result is None:
        message = "No book found"
        return jsonify(message), 404
    response = {}
    reviews = []
    for reviewes in r:
        eachreview = {}
        eachreview["email"] = reviewes.username
        eachreview["rating"] = reviewes.rating
        eachreview["comment"] = reviewes.review
        reviews.append(eachreview)
    response['isbn'] = result.isbn
    response['title'] = result.title
    response['author'] = result.author
    response['year'] = result.year
    response['reviews'] = reviews
    print(response)
    return jsonify(response), 200



@app.route('/api/submit_review', methods=['POST'])
def review_api():
    print("entered route")
    if not request.is_json:
        message = "Invalid request format"
        return jsonify(message),400
    isbn=request.args.get('isbn')
    print(isbn)
    try:
        result = db.session.query(Books).filter(Books.isbn == isbn).first()
    except:
        message = "Please Try again Later"
        return jsonify(message),500
    if result is None:
        message = "Please enter valid ISBN"
        return jsonify(message), 404
    rating = request.get_json()['rating']
    rev= request.get_json()['review']
    username = request.get_json()['username']
    timestamp = time.ctime(time.time())
    title = result.title
    user = review.query.filter_by(username=username,isbn=isbn).first()
    if user is not None:
        message = "Sorry you can't review this book again"
        return jsonify(message), 409
    reviewdata=review(isbn=isbn, review=rev, rating=rating,
                        time_stamp=timestamp, title=title, username=username)
    try:
        db.session.add(reviewdata)
        db.session.commit()
    except:
        message = "Please Try Again "
        return jsonify(message), 500
    try:
        result = db.session.query(Books).filter(Books.isbn == isbn).first()
        r=review.query.filter_by(isbn=isbn).all()
    except:
        message = "Please Try again Later"
        return jsonify(message),500
    print(result)
    if result is None:
        message = "No book found"
        return jsonify(message), 404
    response = {}
    reviews = []
    for revieww in r:
        eachreview = {}
        eachreview["email"] = revieww.username
        eachreview["rating"] = revieww.rating
        eachreview["comment"] = revieww.review
        reviews.append(eachreview)
    response['isbn'] = result.isbn
    response['title'] = result.title
    response['author'] = result.author
    response['year'] = result.year
    response['reviews'] = reviews
    # message = "Review submitted successfully"
    print(response)
    return jsonify(response), 200
  
@app.route('/api/search', methods = ["POST"])
def apisearch():
    # print(request)
    # print(request.is_json)
    if not request.is_json:
        message = "Invalid request format"
        return jsonify(message),400
    reqs = request.get_json()['query']
    try:
        booksdata = db.session.query(Books.isbn,Books.title,Books.author,Books.year).filter(or_(Books.title.like("%"+reqs+"%"),Books.author.like("%"+reqs+"%"),Books.isbn.like("%"+reqs+"%"),Books.year.like("%"+reqs+"%"))).all()
    except:
        message = "Please Try again Later"
        return jsonify(message), 500
    # print(booksdata)
    if booksdata.__len__()==0:
        message = "No search results found"
        return jsonify(message),404
    response = []
    for book in booksdata:
        dictionary = {}
        dictionary["isbn"] = book[0]
        dictionary['title'] = book[1]
        dictionary['author'] = book[2]
        dictionary['year'] = book[3]
        response.append(dictionary)
    return jsonify(response) , 200
