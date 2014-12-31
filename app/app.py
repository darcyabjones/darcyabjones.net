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

from flask import Flask
from flask import url_for

app = Flask(__name__)

@app.route('/')
def index():
    return 'index page'

@app.route('/user/<username>')
def show_user_profile(username):
    return "User {}".format(username)

@app.route('/post/')
def blog():
    return "This is the blog,"

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return "Post {}".format(post_id)

@app.route('/projects/')
def projects():
    return 'The project page'

@app.route('/about')
def about():
    return 'The about page'

if __name__ == '__main__':
    app.run(debug=True) # host='0.0.0.0' # Ditch debug on production.
