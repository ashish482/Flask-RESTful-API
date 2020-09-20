from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) #Flask app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'  #specifying the path of database
db = SQLAlchemy(app)  #using SQLAlchemy Database


class User(db.Model):     #Building a User class
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def serialize(self):   #converting the class object into json format
        return {"id": self.id,
                "user": self.username}

    def __init__(self, username):
        self.username = username
