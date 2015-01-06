#! /usr/bin/env python3

__program__ = "app"
__version__ = "0.1.0"
__author__ = "Darcy Jones"
__date__ = "30 December 2014"
__author_email__ = "darcy.ab.jones@gmail.com"
__license__ = """
################################################################################

    Copyright (C) 2014  Darcy Jones

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

################################################################################
"""

################################ Import Modules ################################

import app
from app.posts import get_posts
from flask import Flask
from flask import url_for
from flask import redirect
from flask import render_template
import json
import os

base_path = os.path.dirname(app.__file__)
content_path = os.path.join(base_path, 'content')
posts_html = os.path.join(content_path, 'posts')
posts_processed = os.path.join(content_path, 'posts_processed')
posts_raw = os.path.join(content_path, 'posts_raw')

################################ Define Classes ################################


############################### Define Functions ###############################

app = Flask(__name__)

def update(path):
    """ Loads JSON content for the page.

    Keyword arguments:
    path -- The path to the JSON file (type int).

    Returns:
    A dictionary containing the JSON information (type dict).
    """
    try:
        json_handle = open(path, 'r')
        json_content = json.load(json_handle)
    except ValueError:
        print("The JSON has a formatting error.")
        raise
    finally:
        json_handle.close()
    return json_content

def nav(current):
    """ Creates a dictionary to construct the current navigation bar from.

    This function is pretty straight-forward. To have the navigation button for
    the currently active page highlighted we convert 'current' to a boolean
    value so that we can conditionally add an extra class to the Jinja2 template.

    Keyword arguments:
    current -- The page that is currently active (type str).

    Returns:
    A dictionary containing link names, link hrefs and whether the page is
        currently active (type dict).
    """
    nav_list = [
        {
            "name":"Home",
            "path":url_for('index'),
            "current":(current.lower() in {"home", "index"})
        },
        {
            "name":"Blog",
            "path":url_for('blog'),
            "current":(current.lower() in {"blog", "archive", "post"})
        },
        {
            "name":"Projects",
            "path":url_for('projects'),
            "current":(current.lower() == "projects")
        },
        {
            "name":"About",
            "path":url_for('about'),
            "current":(current.lower() == "about")
        }
    ]
    return nav_list

@app.route('/')
def index():
    content = update(path=os.path.join(content_path, "index.json"))
    return render_template('index.html', nav=nav("Home"), page=content)

@app.route('/blog/')
def blog():
    content = update(path=os.path.join(content_path, "blog.json"))
    posts = get_posts(posts_html)
    for post in posts:
        with open(post['html'], 'rU') as html_handle:
            post['content'] = html_handle.read()
    return render_template('blog.html', nav=nav("Blog"), page=content, posts=posts)

@app.route('/archive/')
def archive_redirect():
    return redirect(url_for('archive'))

@app.route('/posts/')
def archive():
    content = update(path=os.path.join(content_path, "archive.json"))
    return render_template('archive.html', nav=nav("Archive"), page=content)

@app.route('/posts/<post_id>')
def show_post(post_id):
    content = update(path=os.path.join(content_path, "archive.json"))
    post = get_posts(posts_html, post_id)[0]
    with open(post['html'], 'rU') as html_handle:
        post['content'] = html_handle.read()
    return render_template('post.html', nav=nav("Post"), page=content, post=post)

@app.route('/projects/')
def projects():
    content = update(path=os.path.join(content_path, "projects.json"))
    return render_template('projects.html', nav=nav("Projects"), page=content)

@app.route('/about')
def about():
    content = update(path=os.path.join(content_path, "about.json"))
    return render_template('about.html', nav=nav("About"), page=content)


##################################### Code #####################################

if __name__ == '__main__':
    app.run(debug=True) # host='0.0.0.0' # Ditch debug on production.
