#! /usr/bin/env python3

__program__ = "posts"
__version__ = "0.1.0"
__author__ = "Darcy Jones"
__date__ = "5 January 2015"
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

from os.path import splitext
from os.path import join
from os.path import isfile
from os import listdir
from collections import defaultdict
import json
import yaml
from datetime import datetime


################################################################################


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


def json_date_writer(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def process_md(md_path):
    import re

    # Boundary is three or more '.' or '-'.
    yaml_boundary = re.compile("(-{3,}|\.{3,})")
    blankline = True
    yaml_block = False
    yaml = list()
    current_yaml = list()
    with open(md_path, 'rU') as md_handle:
        for line in md_handle:
            if yaml_boundary.match(line.strip()) != None and blankline:
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
    with open(md_path, 'rU') as md_handle:
        markdown = md_handle.read()
    return markdown, process_yaml(yaml)


def process_yaml(yaml_list):
    import yaml

    yaml_dict = dict()
    for yaml_item in reversed(yaml_list):
        yaml_dict.update(yaml.load(yaml_item))
    return yaml_dict


def next_md_path(current_path):
    from os.path import splitext

    current_path = splitext(current_path)[0]
    next_ext = splitext(current_path)[1]
    if next_ext.lower() == '' or next_ext.lower() == '.md':
        next_path = '{}.md'.format(splitext(current_path)[0])
    else:
        next_path = splitext(current_path)
    return next_path


def generate_dir_path(path, suffix):
    import os
    id_ = path.split('.')[0]
    dir_path = "{}-{}".format(id_, suffix)
    # if not os.path.isdir(dir_path):
    #     os.makedirs(dir_path)
    return dir_path
