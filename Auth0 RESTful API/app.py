from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode


from flask import request
from db import User
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime

import constants

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = 'http://127.0.0.1:5000/callback'
AUTH0_CLIENT_ID = 'dbVNh5IMyW24iMSrip4CtbFICdTtK8R1'
AUTH0_CLIENT_SECRET = '9oiebNEOn22kr7C4nTpH42LMB4v2dnCXIUMFkal1KS8YZqIdpMoGNTHTz7GoDRQm'
AUTH0_DOMAIN = 'dev-rp56n1lv.us.auth0.com'
AUTH0_BASE_URL = 'https://dev-rp56n1lv.us.auth0.com'
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)

app = Flask(__name__, static_url_path='/public', static_folder='./public')
app.secret_key = '7hBGvDFYZpVygt4BGKQYz1R1viuT197PTG05xEULCswxEtDhh-HLG4eLNHljzDLX'
app.debug = True


@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,                      #####Auth0 configuration
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
db = SQLAlchemy(app)


def requires_auth(f):                           #Building a generator for checking Auth0 token, provided before calling an API
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


# Controllers API
@app.route('/')
def home():
    return render_template('home.html')              #rendering home page


@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    print(userinfo)
    session[constants.JWT_PAYLOAD] = userinfo
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/user')                                   #redirecting to Api


@app.route('/login')       #login function
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@app.route('/logout')       #logging out
def logout():
    session.clear()
    params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@app.route('/dashboard')    #rendering dashboard page for user
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))


@app.route("/user", methods=["GET", "POST"])        #Getting all users and adding a new user using form data
@requires_auth
def add_user():

    if request.method == "GET":
        print("HI")
        return jsonify({'users': list(map(lambda dev: dev.serialize(), User.query.all()))})

    if request.method == "POST":
        username = request.form['username']
        new_user= User(username)
        db.session.add(new_user)
        db.session.commit()
        return "Added"

@app.route("/user/<int:id>", methods=["GET", "PUT", "DELETE"])  #Getting a single user using UserId, modifying a single user using UserId, deleting a single user using UserId
@requires_auth
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

@app.route("/user/term=<search_term>", methods=["GET"])         #Searching for a user containing particular characters.
@requires_auth
def get(search_term):
    return jsonify({'users': list(map(lambda filter: filter.serialize(), User.query.filter(User.username.like('%'+search_term+'%')).all()))})


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=env.get('PORT', 5000))