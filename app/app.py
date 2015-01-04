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
from flask import render_template
import json
import os
import pypandoc

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

def process_raw_posts(path, completed_path, html_path):
    """    """
    from os import listdir
    from os import remove
    from os.path import isfile
    from os.path import join
    from os.path import splitext
    from os.path import split
    from shutil import copy2
    from shutil import move
    import pypandoc
    import json

    knitr_extensions = {".rmd", ".rnw"}
    pweave_extensions = {".pmd", ".pnw"}
    pandoc_extensions = {".md",}
    extensions = knitr_extensions + pweave_extensions + pandoc_extensions

    raw_files__ = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
    raw_files_ = [f for f in raw_files__ if splitext(f)[1] in extensions]
    raw_files = [join(path, f) for f in raw_files_ ]

    for raw_file, completed_file in zip(raw_files, raw_files_):
        copy2(src=raw_file, dst=join(completed_path, completed_file))

    while len(raw_files) > 0:
        current_file = raw_files.pop(0)
        current_ext = splitext(current_file)[1]
        next_file = next_md_path(current_file)
        if current_ext.lower() in knitr_extensions:
            output = call_knitr(
                input_file=current_file,
                output_file=next_file,
                figure_path=generate_dir_path(current_file, 'figures'),
                cache_path=generate_dir_path(current_file, 'cache')
            )
            raw_files.append(next_file)
            remove(current_file)
        elif current_ext.lower() in pweave_extensions:
            output = call_pweave(
                input_file=current_file,
                output_file=next_file,
                figure_path=generate_dir_path(current_file, 'figures'),
                cache_path=generate_dir_path(current_file, 'cache')
            )
            raw_files.append(next_file)
            remove(current_file)
        elif current_ext.lower() in pandoc_extensions:
            yaml, markdown = process_md(current_file)
            output = pypandoc.convert(
                source=markdown,
                to='html5',
                format='markdown',
                extra_args=[]
            )
            new_html_path = join(
                html_path,
                splitext(split(current_file)[1])[0]
            )
            html_file = new_html_path + ".html"
            with open(html_file, 'w') as html_handle:
                html_handle.write(output)
            json_file = new_html_path + ".json"
            with open(json_file, 'w') as json_handle:
                json.dump(yaml, json_handle)
            move(
                src=generate_dir_path(current_file, 'figures'),
                dst=next_path + "-figures"
            )
            move(
                src=generate_dir_path(current_file, 'cache'),
                dst=next_path + "-cache"
            )
    return

def process_md(md_path):
    """    """
    import re
    # Boundary is three or more '.' or '-'.
    yaml_boundary = re.compile("(-{3,}|\.{3,})")
    blankline = True
    yaml_block = False
    markdown = list()
    yaml = list()
    current_yaml = list()
    with open(md_path, 'rU') as md_handle:
        for line in md_handle:
            if yaml_boundary.match(line.strip()) != None:
                if yaml_block:
                    yaml_block = False
                    yaml.append("\n".join(current_yaml))
                    current_yaml = list()
                else:
                    yaml_block = True
            elif line.strip == '':
                blankline = True
            elif yaml_block:
                current_yaml.append(line)
            else:
                markdown.append(line)
    return "\n".join(markdown), process_yaml(yaml)

def process_yaml(yaml_list):
    """    """
    import yaml
    yaml_dict = dict()
    for yaml_item in reversed(yaml_list):
        yaml_dict.update(yaml.load(yaml_item))
    return yaml_dict

def next_md_path(current_path):
    """    """
    from os.path import splitext
    current_path = splitext(current_path)[0]
    next_ext = splitext(current_path)[1]
    if next_ext.lower() == '' or next_ext.lower() == '.md':
        next_path = '{}.md'.format(splitext(current_path)[0])
    else:
        next_path = splitext(current_path)
    return next_path

def generate_dir_path(path, suffix):
    """    """
    import os
    id_ = path.split('.')[0]
    dir_path = "{}-{}".format(id_, suffix)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    return dir_path

def call_pweave(
        input_file,
        output_file,
        figure_path="images",
        cache_path="cache",
        cache=False,
        plot=True,
        figformat=None,
        doctype='pandoc'
    ):
    """    """
    from pweave import Pweb
    from pweave.config import rcParams

    doc = Pweb(file=input_file, format=doctype)
    rcParams["usematplotlib"] = plot

    rcParams["figdir"] = figure_path
    rcParams["cachedir"] = cache_path
    doc.storeresults = cache
    doc.sink = output_file
    if figformat is not None:
        doc.updateformat({'figfmt' : figformat, 'savedformats' : [figformat]})

    doc.parse()
    doc.run()
    doc.format()
    doc.sink = output_file
    doc.write()
    return

def call_knitr(
        input_file,
        output_file,
        rscript="Rscript",
        figure_path="images",
        cache_path="cache"
    ):
    """    """
    import subprocess

    r_command = ";".join([
        "library(knitr)",
        "opts_chunk$set(fig.path = {f}, cache.path = {c})".format(
            f=figure_path,
            c=cache_path
        ),
        "knit('{input_}', output = '{output}')".format(
            input_=input_file,
            output=output_file
        )
    ])

    command = ' '.join([
        rscript,
        '-e',
        '"{}"'.format(r_command)
    ])

    subps = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return subps.communicate()

@app.route('/')
def index():
    content = update(path=os.path.join(content_path, "index.json"))
    return render_template('index.html', nav=nav("Home"), page=content)

@app.route('/blog/')
def blog():
    content = update(path=os.path.join(content_path, "blog.json"))
    return render_template('blog.html', nav=nav("Blog"), page=content)

@app.route('/archive/')
def archive_redirect():
    return redirect(url_for('archive'))

@app.route('/posts/')
def archive():
    content = update(path=os.path.join(content_path, "archive.json"))
    return render_template('archive.html', nav=nav("Archive"), page=content)

@app.route('/posts/<int:post_id>')
def show_post(post_id):
    content = update(path=os.path.join(content_path, "archive.json"))
    return render_template('post.html', nav=nav("Post"), page=content)

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
