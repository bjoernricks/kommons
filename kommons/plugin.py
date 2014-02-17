# -*- coding: utf-8 -*-

# kommons - A library for common classes and functions
#
# Copyright (C) 2013, 2014 Björn Ricks <bjoern.ricks@gmail.com>
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

import imp
import inspect
import logging
import os
import sys

logger = logging.getLogger(__name__)

class Module(object):

    def __init__(self, module):
        self.module = module

    def get_classes(self, parentclass=None, all=False):
        """
        Returns all classes of the module

        :param parentclass Only returns classes that are child of parentclass
        :param all If False only classes from module are returned. Imported
                   classes are excluded in that case.
        """
        classes = []
        for key, value in self.module.__dict__.items():
            if inspect.isclass(value):
                if parentclass:
                    if not issubclass(value, parentclass):
                        continue
                # only load classes from module
                if not all and value.__module__ != module.__name__:
                    logger.debug("Skipping class '%s'" % value)
                    continue
                logger.debug("Found class '%s'" % value)
                classes.append(value)
        return classes

    def get_class(self, classname):
        """
        Returns the class from the module with name classname or None if not
        found.
        """
        classes = self.get_classes()
        if not classes:
            return None
        for cls in classes:
            if cls.__name__ == classname:
                return cls
        return None


class FileLoader(object):

    """
    A module loader class to load modules from "normal" .py files
    """

    def __init__(self, paths=None):
        self.paths = paths or []

    def add_path(self, path):
        """
        Adds a path to the module search path
        """
        self.paths.append(path)

    def add_paths(self, paths):
        """
        Adds a path list to the module search path
        """
        self.paths.extend(paths)

    def _load_module(self, module_name, paths, as_module=None):
        if not as_module:
            as_module = module_name
        file, pathname, description = imp.find_module(module_name, paths)
        try:
            return imp.load_module(as_module, file, pathname, description)
        finally:
            if file:
                file.close()

    def load_module(self, name, as_module=None):
        """
        Loads a python module by its name

        If found the module is stored as as_module if set or name otherwise.

        The module specified with name may be no valid python package e.g.
        mypackage/mymodule.py can be loaded via 'mypackage.mymodule' without
        having to add a mypackage/__init__.py file.
        """
        if not as_module:
            as_module = name
        if "." in name:
            paths = []
            index = name.rfind(".")
            package = name[:index]
            module_name = name[index+1:]
            module_path = package.replace(".", os.path.sep)
            for path in self.paths:
                paths.append(os.path.join(path, module_path))
        else:
            module_name = name
            paths = self.paths
        if not paths:
            paths = self.paths
        try:
            if as_module in sys.modules:
                logger.warn("Reloading '%s' module. This overwrites the " \
                            "previous loaded module with the same name." % \
                            as_module)
                del sys.modules[as_module]
            module = self._load_module(module_name, paths, as_module)
            logger.debug("Imported module '%s'" % module)
            return Module(module)
        except ImportError, error:
            logger.warn("Could not import module '%s'. %s" % (name, error))
            return None


class StringLoader(object):

    """
    Load a python module from a String
    """

    def __init__(self, code):
        self.code = code

    def get_code(self):
        return self.code

    def is_package(self, fullname):
        return False

    def load_module(self, fullname):
        code = self.get_code()
        ispkg = self.is_package(fullname)
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = "<%s>" % self.__class__.__name__
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = []
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        exec(code, mod.__dict__)
        return mod

# vim: et sw=4 ts=4 tw=80:
