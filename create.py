import os

from flask import Flask, request, render_template,url_for,flash,jsonify
# from models import *
from booksdb import Books
from books import *
from flask import Flask, session, redirect
from flask_session import Session
from sqlalchemy import create_engine, desc , or_
from sqlalchemy.orm import scoped_session, sessionmaker
# from Review import *


import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

engine = create_engine(os.getenv("DATABASE_URL"))

Session(app)
db.init_app(app)
@app.route('/')
def hello_world():
    return redirect('/register')
@app.route('/register', methods = ['POST','GET'])
def register():

    if request.method == 'POST':
        userdata = USERS(request.form['email'],request.form['psw'])
        user = USERS.query.filter_by(emailid=request.form['email']).first()
        if user is not None:
            print("User is already existing. Please try to register with a new")
            var1 = "Error: User is already existing. Please try to register with a new one"
            return render_template("reg.html", var1 = var1)
        db.session.add(userdata)
        db.session.commit()
        print("Registration Success")
        var1 ='Registration Success'
        return render_template("reg.html", var1 = var1)
    else:
        return render_template("reg.html")
    

@app.route('/admin')
def admin():
    data = USERS.query.order_by(desc(USERS.timestamp)).all()
    return render_template("admin.html",admin = data)

@app.route('/auth', methods=['POST'])
def login():
    print(request.form)
    user = USERS.query.filter_by(emailid=request.form['email']).first()

    if user is not None:
        if bcrypt.verify(request.form['psw'], user.password):
            session['email'] = request.form['email']
            print(session)
            return redirect('/search')
        else:
            var1 = "Wrong Credentials"
            return render_template("reg.html", var1 = var1)
    else:
        print("You are not a registered user. Please first register to login")
        var1 = "Error: You are not a registered user. Please first register to login"
        return render_template("reg.html", var1 = var1)
@app.route('/search', methods=['POST','GET'])
def search():
    try:
        user=session['email']

        if request.method == 'POST':
            req  = request.form['search']
            reqs = str(req)
            bookss = dbscope.query(Books.isbn, Books.title, Books.author, Books.year).filter(or_(Books.title.like("%"+reqs+"%"), Books.author.like("%"+reqs+"%"), Books.isbn.like("%"+reqs+"%"))).all()
            if bookss.__len__()==0:
                var1 = "No search found"
                return render_template("login.html", var1 = var1, user = user)
            return render_template("login.html",bookss = bookss,formaction = '/search', user = user)
        return render_template("login.html", user = user)
    except Exception as e:
        print(e)
        var1 = "You must log in to view the homepage"
        return render_template("reg.html",var1 = var1)

@app.route('/logout')
def logout():
    try:
        session.clear()
        var1 = "Logged Out"
        return redirect('/register')
    except:
        var1 = "You must first log in to logout"
        return render_template("reg.html",var1 = var1)

@app.route('/books/<id>',methods=['POST','GET'])
def books(id):

    try:
        user = session["email"]
        result = db.session.query(Books).filter(Books.isbn == id).first()
        data=Review.query.all()
        r=Review.query.filter_by(isbn=id).all()
        if request.method=='POST':
            reviewdata=Review(id,user,request.form['comment'],request.form['rating'])
            user = Review.query.filter_by(email=user,isbn=id).first()
            data=Review.query.all()
            if user is not None:
                print("User had already given rating.")
                var1 = "Error: User had already given rating."
                return render_template("Book_Page.html", user = user,Book_details=result,var1 = var1,comments=r, allreviewdata = data )
            db.session.add(reviewdata)
            db.session.commit()
            var1="Review submitted"
            flash(var1)
            
            return redirect(url_for('books', id = id))

        else:   
            return render_template("Book_Page.html", user = user,Book_details=result,comments=r, allreviewdata = data )
  
    except Exception as e:
        print(e)
        var1 = "You must log in to view the homepage"
        return render_template("reg.html",var1 = var1)
       
# First api route, search
#('0553297260', 'Darkness', 'John Saul', 1991)
@app.route('/api/search', methods = ["POST"])
def apisearch():
    print(request)
    print(request.is_json)
    if not request.is_json:
        message = "Invalid request format"
        return jsonify(message),400
    reqs = request.get_json()['query']
    try:
        bookss = dbscope.query(Books.isbn, Books.title, Books.author, Books.year).filter(or_(Books.title.like("%"+reqs+"%"), Books.author.like("%"+reqs+"%"), Books.isbn.like("%"+reqs+"%"))).all()
    except:
        message = "Please Try again Later"
        return jsonify(message), 500
    print(bookss)
    if bookss.__len__()==0:
        message = "No search results found"
        return jsonify(message),404
    response = []
    for book in bookss:
        dictionary = {}
        dictionary["isbn"] = book[0]
        dictionary['title'] = book[1]
        dictionary['author'] = book[2]
        dictionary['year'] = book[3]
        response.append(dictionary)
    return jsonify(response) , 200

#Second api route - Book page
@app.route('/api/book')
def apibook():
    query = request.args.get('isbn')
    try:
        result = db.session.query(Books).filter(Books.isbn == query).first()
        r=Review.query.filter_by(isbn=query).all()
    except:
        message = "Please Try again Later"
        return jsonify(message),500
    print(result)
    if result is None:
        message = "No book found"
        return jsonify(message), 404
    response = {}
    reviews = []
    for review in r:
        eachreview = {}
        eachreview["email"] = review.email
        eachreview["rating"] = review.rating
        eachreview["comment"] = review.comment
        reviews.append(eachreview)
    response['isbn'] = result.isbn
    response['title'] = result.title
    response['author'] = result.author
    response['year'] = result.year
    response['reviews'] = reviews
    return jsonify(response), 200

# Third route -- Review submission
@app.route('/api/submitReview', methods  =['POST'])
def submitreview():
    if not request.is_json:
        message = "Invalid request format"
        return jsonify(message),400
    isbn = request.args.get('isbn')
    try:
        result = db.session.query(Books).filter(Books.isbn == isbn).first()
    except:
        message = "Please Try again Later"
        return jsonify(message),500
    if result is None:
        message = "Please enter valid ISBN"
        return jsonify(message), 404
    rating = request.get_json()['rating']
    comment = request.get_json()['comment']
    email = request.get_json()['email']
    user = Review.query.filter_by(email=email,isbn=isbn).first()
    if user is not None:
        message = "Sorry you can't review this book again"
        return jsonify(message), 409
    reviewdata=Review(isbn,email,comment,rating)
    try:
        db.session.add(reviewdata)
        db.session.commit()
    except:
        message = "Please Try Again "
        return jsonify(message), 500
    # print(isbn,rating,comment)
    message = "Review submitted successfully"
    return jsonify(message), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()


