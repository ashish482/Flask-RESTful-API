from flask import Flask, request, jsonify
import jwt
import datetime
from flask_sqlalchemy import SQLAlchemy
from db import User
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY']= 'password'                     #Setting the secret key for authentication
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
db = SQLAlchemy(app)

@app.route("/token")
def generate_token():           #generating tokens for authentication
    token = jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)}, app.config['SECRET_KEY'])
    return jsonify({'token':token.decode('utf-8')})


def check_for_token(func):   #Building a generator for checking token, provided before calling an API
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = None
        if 'token' in request.headers:
            token= request.headers['token']

        if not token:
            return jsonify({'message': 'Token is missing'}), 403
        try:
            data= jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Invalid Token'}), 403
        return func(*args, **kwargs)
    return wrapped


@app.route("/user", methods=["GET", "POST"])   #Getting all users and adding a new user using form data in Postman
@check_for_token
def add_user():

    if request.method == "GET":
        return jsonify({'users': list(map(lambda dev: dev.serialize(), User.query.all()))})

    if request.method == "POST":
        username = request.form['username']
        new_user= User(username)
        db.session.add(new_user)
        db.session.commit()
        return "User Added"

@app.route("/user/<int:id>", methods=["GET", "PUT", "DELETE"])  #Getting a single user using UserId, modifying a single user using UserId, deleting a single user using UserId
@check_for_token
def single_user(id):

    if request.method == "GET":
        return jsonify({'users': list(map(lambda user: user.serialize(), User.query.filter_by(id=id).all()))})

    if request.method == "PUT":
        user= User.query.get(id)

        username=request.form['username']
        user.username=username
        db.session.merge(user)
        db.session.commit()
        return jsonify({'user':user.serialize()})

    if request.method == "DELETE":
        user= User.query.get(id)
        merge= db.session.merge(user)
        db.session.delete(merge)
        db.session.commit()
        return jsonify('Deleted User !')

@app.route("/user/term=<search_term>", methods=["GET"])
@check_for_token
def get(search_term):
    #results = User.query.filter(User.username.like('%'+search_term+'%')).all()
    return jsonify({'users': list(map(lambda filter: filter.serialize(), User.query.filter(User.username.like('%'+search_term+'%')).all()))})


if __name__ == "__main__":
    app.run(debug=True)