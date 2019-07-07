from flask import Flask, request, g, session, redirect, url_for, render_template
from flask import render_template_string, jsonify
from flask_github import GitHub

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from lib.models.users import User
from lib.models.searched_results import SearchResults
from lib.models.db import db_session

import requests
import json

DATABASE_URI = 'sqlite:////tmp/github-flask.db'
SECRET_KEY = 'development key'
DEBUG = True

# Set Github specifc values
GITHUB_CLIENT_ID = '149c79bff7a73b8d8456'
GITHUB_CLIENT_SECRET = '9144e244779a5047c7e22ff978821dc1a08639cd'

# setup flask
app = Flask(__name__)
app.config.from_object(__name__)

# setup github-flask
github = GitHub(app)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.after_request
def after_request(response):
    db_session.remove()
    return response


@app.route('/')
def index():
    if g.user:
        previously_searched_rows = previously_searched()
        return render_template('home.html', user_details=g.user, 
                                previously_searched_rows=previously_searched_rows)
    else:
        return render_template('login.html')

# Retrieves token from database
@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token


@app.route('/callback')
@github.authorized_handler
def authorized(access_token):
    next_url = request.args.get('next') or url_for('index')
    if access_token is None:
        return redirect(next_url)

    user = User.query.filter_by(github_access_token=access_token).first()
    if user is None:
        user = User(access_token)
        db_session.add(user)

    user.github_access_token = access_token

    # Not necessary to get these details here
    # but it helps humans to identify users easily.
    g.user = user
    github_user = github.get('/user')
    user.github_id = github_user['id']
    user.github_login = github_user['login']

    db_session.commit()

    session['user_id'] = user.id
    return redirect(next_url)


@app.route('/login')
def login():
    if session.get('user_id', None) is None:
        return github.authorize()
    else:
        return 'Already logged in'


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/user')
def user():
    return jsonify(github.get('/user'))


@app.route('/search', methods=['GET'])
def search():
    username = request.args.get('search_term')
    if username:
        url = 'https://api.github.com/search/users?q=' + username + '&page=1&per_page=100'
        r = requests.get(url)
        result = r.json()['items']

        searcher_github_id = github.get('/user')['id']
        searched_ids = (SearchResults.query.with_entities(SearchResults.github_id)
                        .filter(SearchResults.searcher_github_id == searcher_github_id)
                        .all())
        previously_searched_ids = [i[0] for i in searched_ids]
        result_github_ids = [profile['id'] for profile in result]

        new_profiles = list(set(result_github_ids) - set(previously_searched_ids))

        for profile in result:
            if profile['id'] in new_profiles:
                insert_row = SearchResults(searcher_github_id, profile['avatar_url'],
                                profile['login'], profile['html_url'], profile['id'])
                db_session.add(insert_row)
                db_session.commit()

        return render_template('results.html', result=json.dumps(r.json()['items']))
    else:
        return redirect(url_for('index'))


@app.route('/previously_searched', methods=['GET'])
def previously_searched():
    searcher_github_id = github.get('/user')['id']
    rows = (db_session.query
                (SearchResults.username,
                 SearchResults.avatar_url,
                 SearchResults.html_url,
                 SearchResults.github_id)
                .filter(SearchResults.searcher_github_id == searcher_github_id)
                .all())
    keys = ['login', 'avatar_url', 'html_url', 'github_id']
    searched_rows = [dict(zip(keys, result)) for result in rows]
    return searched_rows


@app.route('/delete_records', methods=['POST'])
def delete_records():
    ids = request.get_json()['selected_rows_github_ids']
    searcher_github_id = github.get('/user')['id']
    if ids:
        (db_session.query(SearchResults)
            .filter(SearchResults.github_id.in_(ids))
            .filter(SearchResults.searcher_github_id == searcher_github_id)
            .delete(synchronize_session=False))
        db_session.commit()


    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)
