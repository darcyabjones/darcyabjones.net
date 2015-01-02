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
from flask import Flask
from flask import url_for
from flask import render_template
import json
import os

base_path = os.path.dirname(app.__file__)
content_path = os.path.join(base_path, 'content')


################################ Define Classes ################################


############################### Define Functions ###############################

app = Flask(__name__)

def update(path):
    """
    """
    import json
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
    """
    """
    from flask import url_for
    nav_list = [
        {
            "name":"Home",
            "path":url_for('index'),
            "current":(current.lower() in {"home", "index"})
        },
        {
            "name":"Archive",
            "path":url_for('archive'),
            "current":("archive" == current.lower())
        },

        {
            "name":"Projects",
            "path":url_for('projects'),
            "current":("projects" == current.lower())
        },
        {
            "name":"About",
            "path":url_for('about'),
            "current":("about" == current.lower())
        }
    ]
    return nav_list

@app.route('/')
def index():
    content = update(path=os.path.join(content_path, "index.json"))
    return render_template('index.html', nav=nav("Home"), content=content)

@app.route('/archive/')
def archive():
    content = update(path=os.path.join(content_path, "archive.json"))
    return render_template('archive.html', nav=nav("Archive"), content=content)

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return "Post {}".format(post_id)

@app.route('/projects/')
def projects():
    content = update(path=os.path.join(content_path, "projects.json"))
    return render_template('projects.html', nav=nav("Projects"), content=content)

@app.route('/about')
def about():
    content = update(path=os.path.join(content_path, "about.json"))
    return render_template('about.html', nav=nav("About"), content=content)


##################################### Code #####################################

if __name__ == '__main__':
    app.run(debug=True) # host='0.0.0.0' # Ditch debug on production.
