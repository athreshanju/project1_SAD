import os
import sys
import time

from users import *
from booksdb import *

from flask import Flask, session, render_template, request,redirect,url_for
from sqlalchemy import create_engine,desc



app = Flask(__name__, static_url_path='/static')
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
    print("entered logout")
    session.pop(username, None)
    return redirect(url_for('index'))


@app.route("/bookpage/<username>/<id>")
def bookspage(id,username):
    if username in session.keys():
        print(session.keys())
        
                
        response=db.session.query(Books).filter(Books.isbn==id).all()
        return render_template('bookpage.html',book_details=response,username=username)
    else:
        return redirect(url_for('index'))



