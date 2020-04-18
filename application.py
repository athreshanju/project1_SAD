import os
import sys
import time

from users import *
from flask import Flask, session, render_template, request,redirect



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
	try:
		usr = user(username = Username, email = Email,password = Password , time = time.ctime(time.time()))

		db.session.add(usr)
		db.session.commit()
	except ValueError:
		return render_template("error.html")
	return render_template("pager.html",name = Username,email = Email)

@app.route("/admin")
def admin():
	adm = user.query.all()
	return render_template("admin.html",adm = adm)
