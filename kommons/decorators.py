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

import warnings

from functools import wraps


def deprecated(message):
    """
    A decorator to raise a warning message when using the decorated function or
    method.

    Usage:
        @depracted("myfunc will be dropped with version 3.2. Please use"
                   "myfunc2 instead")
        def myfunc(...):
            ...
    """
    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            warnings.warn(message, category=DeprecationWarning,  stacklevel=2)
            return f(*args, **kwargs)
        return inner
    return wrapper
