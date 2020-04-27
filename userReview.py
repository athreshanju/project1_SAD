# import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# app = Flask(__name__, static_url_path='/static')
# # Check for environment variable
# if not os.getenv("DATABASE_URL"):
#     raise RuntimeError("DATABASE_URL is not set")

# # Configure session to use filesystem
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db.init_app(app)
# with app.app_context():
#     db.create_all()

class review(db.Model):
    __tablename__ = "reviews"
    isbn = db.Column(db.String, nullable=False, primary_key=True)
    title = db.Column(db.String, nullable=False)
    rating = db.Column(db.String, nullable=False)
    review = db.Column(db.String, nullable=False)
    time_stamp = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, primary_key=True)

