#! /usr/bin/env python3
__program__ = "run"
__version__ = "0.1.0"
__author__ = "Darcy Jones"
__date__ = "30 December 2014"
__author_email__ = "darcy.ab.jones@gmail.com"
__license__ = """
##############################################################################

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

##############################################################################
"""

from app import app
from app import posts
from app.app import base_path
from app.app import content_path
from app.app import posts_html
from app.app import posts_processed
from app.app import posts_raw

if __name__ == '__main__':
    app.app.run(debug=True)
