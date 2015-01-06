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

################################################################################

def process_raw_posts(path, completed_path, html_path, verbose=True):
    """    """

    from os import listdir
    from os import remove
    from os.path import isfile
    from os.path import join
    from os.path import splitext
    from os.path import split
    from os.path import isdir
    from shutil import move
    from datetime import datetime
    import pypandoc
    import json

    if verbose:
        print("### Processing markdown files ###\n")

    knitr_extensions = {".rmd", ".rnw"}
    pweave_extensions = {".pmd", ".pnw"}
    pandoc_extensions = {".md",}
    extensions = knitr_extensions | pweave_extensions | pandoc_extensions

    raw_files = [f for f in listdir(path)
        if isfile(join(path, f))
        and splitext(f)[1].lower() in extensions
    ]

    if verbose:
        print("Processing files.")
        print("Files to process: {}.".format(", ".join(raw_files)))

    while len(raw_files) > 0:
        current_name = raw_files.pop(0)
        current_file = join(path, current_name)
        processed_file = join(completed_path, current_name)
        current_ext = splitext(current_file)[1]
        next_file = next_md_path(current_file)

        if current_ext.lower() in knitr_extensions:
            if verbose:
                print("Running {} through KnitR.".format(current_file))
            output = call_knitr(
                input_file=current_file,
                output_file=next_file,
                figure_path=generate_dir_path(current_file, 'figures'),
                cache_path=generate_dir_path(current_file, 'cache')
            )
            if verbose:
                print(output[0].decode())
                print(output[1].decode())
            raw_files.append(next_file)
            move(src=current_file, dst=processed_file)
            if verbose:
                print("Finished running {} through KnitR.".format(current_file))
                print("Moved {} to {}".format(current_file, processed_file))
        elif current_ext.lower() in pweave_extensions:
            if verbose:
                print("Running {} through Pweave.".format(current_file))
            output = call_pweave(
                input_file=current_file,
                output_file=next_file,
                figure_path=generate_dir_path(current_file, 'figures'),
                cache_path=generate_dir_path(current_file, 'cache')
            )
            raw_files.append(next_file)
            move(src=current_file, dst=processed_file)
            if verbose:
                print("Finished running {} through Pweave.".format(current_file))
                print("Moved {} to {}.".format(current_name, processed_file))
        elif current_ext.lower() in pandoc_extensions:
            if verbose:
                print("Running {} through Pandoc.".format(current_file))
            markdown, yaml = process_md(current_file)
            output = pypandoc.convert(
                source=markdown,
                to='html5',
                format='markdown'
            )
            new_html_path = join(
                html_path,
                splitext(split(current_file)[1])[0]
            )
            html_file = new_html_path + ".html"
            with open(html_file, 'w') as html_handle:
                html_handle.write(output)
            if yaml != {}:
                json_file = new_html_path + ".json"
                with open(json_file, 'w') as json_handle:
                    json.dump(yaml, json_handle, default=json_date_writer)
            if isdir(generate_dir_path(current_file, 'figures')):
                move(
                    src=generate_dir_path(current_file, 'figures'),
                    dst=new_html_path + "-figures"
                )
            if isdir(generate_dir_path(current_file, 'cache')):
                move(
                    src=generate_dir_path(current_file, 'cache'),
                    dst=new_html_path + "-cache"
                )
            move(src=current_file, dst=processed_file)
            if verbose:
                print("Finished running {} through Pandoc.".format(current_file))
                print("Moved {} to {}.".format(current_file, processed_file))
    if verbose:
        print("Finished processing markdown files.")
    return

def json_date_writer(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

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

def process_md(md_path):
    """    """

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
    #if not os.path.isdir(dir_path):
    #    os.makedirs(dir_path)
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
        "require(knitr)",
        r"opts_chunk\$set(fig.path = '{f}', cache.path = '{c}')".format(
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
    stdout, stderr = subps.communicate()
    return stdout, stderr
