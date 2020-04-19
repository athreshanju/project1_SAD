import os
import sys
import time

from users import *
from flask import Flask, session, render_template, request,redirect
from sqlalchemy import create_engine,desc

app = Flask(__name__, static_url_path='/static')


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
    return redirect("/register")

@app.route("/register")
def register():
	return render_template("reg.html")


@app.route("/User",methods=["POST","GET"])
def User():
	Username = request.form.get("username")
	Password = request.form.get("pass")
	Email = request.form.get("email")
	print(Username,file=sys.stderr)
	obj = user.query.filter_by(username = Username).first()
	if obj is None:
		usr = user(username = Username, email = Email,password = Password , time = time.ctime(time.time()))

		db.session.add(usr)
		db.session.commit()
	else:
		print()
		return render_template("reg.html", message = "email already exists!")
	return render_template("pager.html",name = Username,email = Email)

@app.route("/admin")
def admin():
	adm = user.query.order_by(desc(user.time)).all()
	return render_template("admin.html",adm = adm)
