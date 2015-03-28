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
from flask import redirect
from flask import request
from flask import render_template
from flask import abort
from collections import defaultdict
from datetime import datetime
import json
import yaml
import os
from os import listdir
from os.path import splitext
from os.path import join
from os.path import isfile


base_path = os.path.dirname(app.__file__)
content_path = os.path.join(base_path, 'content')
posts_html = os.path.join(content_path, 'posts')
posts_processed = os.path.join(content_path, 'posts_processed')
posts_raw = os.path.join(content_path, 'posts_raw')
projects_html = os.path.join(content_path, "projects")

################################ Define Classes ################################


############################### Define Functions ###############################

app = Flask(__name__)


def update(path):
    """ Load JSON content for the page.

    Keyword arguments:
    path -- The path to the JSON file (type str).

    Returns:
    A dictionary containing the JSON information (type dict).
    """
    try:
        json_handle = open(path, 'r')
        json_content = json.load(json_handle, object_hook=json_date_parser)
    except ValueError:
        print("The JSON has a formatting error.")
        raise
    finally:
        json_handle.close()
    return json_content


def json_date_parser(dct):
    """ A dirty workaround for parsing dates from JSON files.

    Loops (non-recursively) through the dictionary from the parsed JSON file.
    If the value is a string we try to convert the string using several
    'datetime.strptime()' patterns. If the pattern matches the string, the
    string is replaced with the corresponding datetime object. If the pattern
    doesn't match the string we handle the exception, no biggie.

    Keyword arguments:
    dct -- A dictionary from the parsed JSON (type dict).

    Returns:
    A dictionary with string dates replaced with datetime objects (type dict).
    """
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


def format_date(value):
    return value.strftime("%d %B %Y")
app.jinja_env.filters['date'] = format_date


def format_time(value):
    return value.strftime("%H:%M")
app.jinja_env.filters['time'] = format_time


def get_projects(path=projects_html):
    """ . """
    projects = list()
    for file_ in listdir(path):
        if isfile(join(path, file_)):
            name = file_.split('.')[0]
            type_ = splitext(file_)[1].strip('.')
            file_path = join(path, file_)
            if type_ == "html":
                with open(file_path) as handle:
                    projects.append((name, handle.read()))
    projects.sort(key=lambda t: t[0])
    projects = [t[1] for t in projects]
    return projects



def get_posts(path, which=None, verbose=True):
    """ Prepare a list of posts taken from a directory.

    Keyword arguments:
    path -- Path to the directory containing blog posts (type str).
    which -- Specifies which posts to include in the output. 'None' includes all
        posts, a string will return only the post with an id that matches the
        string, and a list (or tuple, or set) of strings will include all posts
        with id's in the list (type:None|str|list, default None).
    verbose -- Print information as the function runs (type bool, default True).

    Returns:
    A list of dict objects (type list).
    """
    """ Here we conditionally define include_test depending on what type of
    object 'which' is."""

    class_ = type(which)
    if class_ == str:
        def include_test(name):
            if name == which:
                return True
            else:
                return False
    elif class_ in {list, tuple, set}:
        def include_test(name):
            if name in which:
                return True
            else:
                return False
    else:
        def include_test(name):
            return True

    """ Loop through all files in the posts directory and add each file format
    e.g. 'json', 'html', etc as keys for a subdictionary. The base dictionary
    is keyed by the file name (excluding the extension).

    example:
    >>> output = {
    ...    'myfile':{
    ...        'html':'/path/to/posts/myfile.html',
    ...        'json':'/path/to/posts/myfile.json'
    ...    }
    ...}
    """
    all_files = defaultdict(dict)
    for file_ in listdir(path):
        if isfile(join(path, file_)):
            name = file_.split('.')[0]
            type_ = splitext(file_)[1].strip('.')
            file_path = join(path, file_)
            all_files[name][type_] = file_path

    posts = list()
    required_keys = {'html', 'title', 'date'}
    for key, value in all_files.items():
        """ If include_test says that we don't need this file, we skip the rest
        of the current iteration and continue with the next key, value pair. """
        if not include_test(key):
            continue
        value['id_'] = key.split("-")[-1]
        if 'json' in value:
            with open(value['json'], "rU") as json_handle:
                value.update(json.load(json_handle, object_hook=json_date_parser))
        elif 'yaml' in value:
            with open(value['yaml'], 'rU') as yaml_handle:
                value.update(yaml.load(yaml_handle))
        elif 'yml' in value:
            with open(value['yml'], 'rU') as yaml_handle:
                value.update(yaml.load(yaml_handle))

        """ If some required keys are missing then we skip the rest of the
        current iteration and continue with the next key, value pair.
        If verbose is True we print which keys were missing."""
        if required_keys.intersection(value) != required_keys:
            if verbose:
                d = required_keys.difference(required_keys.intersection(value))
                print(
                    "Excluded '{}' from posts because it did not ".format(key) +
                    "have all of the required information. The field(s) " +
                    "'{}' was/were missing.".format("', '".join(list(d)))
                )
            continue

        """ Everything is cool, add the post to the list."""
        posts.append(value)

    """ We could run into problems here when dates aren't parsed as datetime
    objects. I might need to figure out a better way of ordering posts by date
    in the future."""
    posts.sort(key=lambda d: d['date'])
    return posts


def side_nav_dates(posts):
    posts.sort(key=lambda d: d['date'])
    dates = list()
    new_posts = list()
    current_year = None
    current_month = None
    first_post = True
    for post in posts:
        year = post['date'].year
        month = post['date'].month
        str_year = post['date'].strftime("%Y")
        str_month = post['date'].strftime("%B")
        str_ym = post['date'].strftime("%Y-%B")
        if first_post:
            first_post = False
            current_year = year
            current_month = month
            new_posts.append({"id_": str_year, "type": "date"})
            new_posts.append({"id_": str_ym, "type": "date"})
            new_posts.append(post)
            dates.append({"target": str_year, "children": [{"value": str_month, "target": str_ym}]})
        elif year != current_year:
            current_year = year
            current_month = month
            new_posts.append({"id_": str_year, "type": "date"})
            new_posts.append({"id_": str_ym, "type": "date"})
            new_posts.append(post)
            dates.append({"target": str_year, "children": [{"value": str_month, "target": str_ym}]})
        elif month != current_month:
            current_month = month
            new_posts.append({"id_": str_ym, "type": "date"})
            new_posts.append(post)
            dates[-1]["children"].append({"value": str_month, "target": str_ym})
        else:
            new_posts.append(post)
    return new_posts, dates


def nav(current):
    """ Create a dictionary to construct the current navigation bar from.

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
            "name": "Home",
            "path": url_for('index'),
            "current": (current.lower() in {"home", "index"})
        },
        {
            "name": "Blog",
            "path" :url_for('blog'),
            "current": (current.lower() in {"blog", "archive", "post"})
        },
        {
            "name": "Projects",
            "path": url_for('projects'),
            "current": (current.lower() == "projects")
        },
        {
            "name": "About",
            "path": url_for('about'),
            "current": (current.lower() == "about")
        }
    ]
    return nav_list


@app.route('/')
def index():
    content = update(path=os.path.join(content_path, "index.json"))
    content['blurb'] = " ".join(content['blurb'])
    return render_template('index.html', nav=nav("Home"), page=content)

@app.route('/blog/')
@app.route('/blog/<post_year>/')
@app.route('/blog/<post_year>/<post_month>/')
@app.route('/blog/<post_year>/<post_month>/<post_day>/')
def blog(post_year=None, post_month=None, post_day=None):
    filter_dates = {"post_year": post_year, "post_month": post_month, "post_day": post_day}
    content = update(path=os.path.join(content_path, "blog.json"))
    posts = get_posts(posts_html)
    current_tags = request.args.getlist("tags")
    current_tags = [tag for tag in current_tags if current_tags.count(tag) % 2 == 1]
    current_tags = list(set(current_tags))
    if current_tags != request.args.getlist("tags"):
        return redirect(url_for('blog', tags=current_tags, **filter_dates))
    tags = list()
    for post in posts:
        if "tags" in post:
            tags.extend(post["tags"])
        if len(current_tags) > 0 and len(set(post["tags"]).intersection(set(current_tags))) == 0:
            posts.remove(post)
            continue
        if post_year != None:
            if str(post["date"].year) != post_year:
                posts.remove(post)
                continue
            if post_month != None:
                if str(post["date"].month) != post_month:
                    posts.remove(post)
                    continue
                if post_day != None:
                    if str(post["date"].day) != post_day:
                        posts.remove(post)
                        continue
        if "blurb" in post:
            post['content'] = post['blurb']
        else:
            with open(post['html'], 'rU') as html_handle:
                post['content'] = html_handle.read()
        post["type"] = "post"
    tags = list(set(tags))

    posts, dates = side_nav_dates(posts)

    return render_template(
        'blog.html',
        nav=nav("Blog"),
        page=content,
        posts=posts,
        current_tags=current_tags,
        tags=tags,
        filter_dates=filter_dates,
        side_nav_dates=dates)


@app.route('/blog/<post_year>/<post_month>/<post_day>/<post_id>')
def show_post(post_year, post_month, post_day, post_id):
    post_name = "-".join([post_year, post_month, post_day, post_id])
    content = update(path=os.path.join(content_path, "archive.json"))
    try:
        post = get_posts(posts_html, post_name)[0]
    except IndexError:
        abort(404)
    with open(post['html'], 'rU') as html_handle:
        post['content'] = html_handle.read()
    return render_template('post.html', nav=nav("Post"), page=content, post=post)


@app.route('/projects/')
def projects():
    content = update(path=os.path.join(content_path, "projects.json"))
    projects = get_projects(projects_html)
    return render_template('projects.html', nav=nav("Projects"), page=content, projects=projects)


@app.route('/about')
def about():
    content = update(path=os.path.join(content_path, "about.json"))
    content['blurb'] = " ".join(content['blurb'])
    return render_template('about.html', nav=nav("About"), page=content)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", nav=nav("None")), 404


@app.route('/termsofuse')
def termsofuse():
    terms = {
        "title": "Terms of use",
        "terms": (
            "All content provided on this blog is for informational purposes "
            "only. The owner of this blog makes no representations as to the "
            "accuracy or completeness of any information on this site or found"
            " by following any link on this site. The owner will not be liable"
            " for any errors or omissions in this information nor for the "
            "availability of this information. The owner will not be liable "
            "for any losses, injuries, or damages from the display or use of "
            "this information. These terms and conditions of use are subject "
            "to change at anytime and without notice.")
        }
    return render_template("termsofuse.html", nav=nav("None"), page=terms)

#################################### Code ####################################

if __name__ == '__main__':
    app.run(debug=True)  # host='0.0.0.0' # Ditch debug on production.
