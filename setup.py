# -*- coding: utf-8 -*-

# kommons - A library for common classes and functions
#
# Copyright (C) 2013  Björn Ricks <bjoern.ricks@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

from distutils.core import setup

import kommons

with open("README") as readme:
    setup(name="kommons",
          description=kommons.__description__,
          version=kommons.__version__,
          author=kommons.__author__,
          author_email=kommons.__author_email__,
          license=kommons.__license__,
          packages=["kommons"],
          classifiers=["Development Status :: 3 - Alpha",
              "Environment :: Console",
              "Intended Audience :: Developers",
              "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              "Topic :: Utilities",
              ],
          long_description=readme.read(),
          )


