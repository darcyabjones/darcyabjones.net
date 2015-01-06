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
from app import posts
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
    """    """
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
    """    """
    from flask import url_for
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

def get_posts(path, which=None):
    """    """

    from os.path import splitext
    from os.path import join
    from os.path import isfile
    from os import listdir
    from collections import defaultdict
    import json
    import yaml
    from sys import stderr
    from datetime import datetime

    def required(dict_):
        if 'html' in dict_ \
            and ('json' in dict_ \
            or 'yaml' in dict_ \
            or 'yml' in dict_):
            return True
        else:
            stderr.write(
                "{} Did not have all required files".format(dict_)
            )
            return False

    raw_files = [f for f in listdir(path) if isfile(join(path, f))]
    print(raw_files)
    output = defaultdict(dict)
    for file_ in raw_files:
        name = file_.split('.')[0]
        type_ = splitext(file_)[1].strip('.')
        file_path = join(path, file_)
        output[name][type_] = file_path

    if isinstance(which, str):
        output = dict([(k, v) for k, v in output.items() if k == which and required(v)])
    elif isinstance(which, list) or isinstance(which, set) \
            or isinstance(which, tuple):
        output = dict([(k, v) for k, v in output.items() if k in which and required(v)])
    else:
        output = dict([(k, v) for k, v in output.items() if required(v)])

    for key, value in output.items():
        value['id_'] = key
        if 'json' in value:
            with open(value['json'], "rU") as json_handle:
                value.update(json.load(json_handle, object_hook=json_date_parser))
        elif 'yaml' in value:
            with open(value['yaml'], 'rU') as yaml_handle:
                value.update(yaml.load(yaml_handle))
        elif 'yml' in value:
            with open(value['yml'], 'rU') as yaml_handle:
                value.update(yaml.load(yaml_handle))
        if 'date' in value:
            if isinstance(value['date'], datetime):
                value['date_str'] = value['date'].strftime("%d %B %Y")
                time_str = value['date'].strftime("%H:%M")
                print(type(time_str))
                if time_str != "00:00":
                    value['time_str'] = time_str
    output = sorted(output.values(), key=lambda d: d['date'])
    return output # list of dictionaries

def json_date_parser(dct):
    from datetime import datetime
    date = "%Y-%m-%d"
    date_time = "%Y-%m-%dT%H:%M:%S"
    date_time2 = "%Y-%m-%dT%H:%M"
    date_time3 = "%Y-%m-%d %H:%M"
    date_time_offset = "%Y-%m-%dT%H:%M:%S%z"
    time = "%H:%M:%S"
    formats = [date, date_time, date_time2, date_time3, date_time_offset, time]
    for k, v in dct.items():
        if isinstance(v, str):
            for fmt in formats:
                try:
                    dct[k] = datetime.strptime(v, fmt)
                except ValueError:
                    pass
    return dct

@app.route('/')
def index():
    content = update(path=os.path.join(content_path, "index.json"))
    return render_template('index.html', nav=nav("Home"), page=content)

@app.route('/blog/')
def blog():
    content = update(path=os.path.join(content_path, "blog.json"))
    posts = get_posts(posts_html)
    print(posts)
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
