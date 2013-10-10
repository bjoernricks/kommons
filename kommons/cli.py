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

"""
This module contains classes to parse arguments from a command line
interface
"""

import argparse
import copy


class ArgumentsCollectorMetaClass(type):

    """ MetaClass to collect defined arguments and groups """

    @classmethod
    def get_declared_arguments(cls, bases, attrs):
        """
        Collects all defined Argument instances as a name instance
        key/value pair returned in a dict.

        @return key/value pair of name and instance of all Argument classes
        """

        arguments = {}
        for name, obj in attrs.items():
            if isinstance(obj, Argument):
                arguments[name] = attrs.pop(name)

        for base in bases[::-1]:
            if hasattr(base, "base_arguments"):
                arguments.update(base.base_arguments)
        return arguments

    @classmethod
    def get_declared_groups(cls, bases, attrs):
        """
        Collects all defined Group instances in a sorted list.
        The list is sorted by the creation counter of each Group instance.

        @return Returns a list of name, instance tuples sorted by the creation
        counter of the instance.
        """
        groups = [(name, attrs.pop(name)) for name, obj in attrs.items() if
                  isinstance(obj, ArgumentGroup)]
        groups.sort(key=lambda x: x[1].creation_counter)

        for base in bases[::-1]:
            if hasattr(base, "base_groups"):
                groups = base.base_groups + groups
        return groups

    def __new__(cls, name, bases, attrs):
        """
        Collects all Argument and Group instances and sets them as
        base_arguments respectively base_groups in the new created class.
        Arguments mentioned in the Group instances will be not added to
        base_arguments.
        """
        arguments = cls.get_declared_arguments(bases, attrs)
        groups = cls.get_declared_groups(bases, attrs)
        new_class = super(ArgumentsCollectorMetaClass, cls).__new__(
            cls, name, bases, attrs)

        if groups:
            for name, group in groups:
                group.set_name(name)
                for arg_name in group.argument_names:
                    arg = arguments.pop(arg_name)
                    arg.set_name(arg_name)
                    group.add_argument(arg)
        new_class.base_groups = groups

        args = []
        if arguments:
            for name, arg in arguments.items():
                arg.set_name(name)
                args.append((name, arg))

        args.sort(key=lambda x: x[1].creation_counter)
        new_class.base_arguments = args

        return new_class


class ArgumentGroup(object):

    """
    A class to declarative define argument groups at a class

    Usage:
        class MyParser(Parser):
            cmd1 = OptionalArgument()
            cmd2 = OptionalArgument()

            group = ArgumentGroup(title="group of possible commands",
                                  argument_names=["cmd1", "cmd2"])
    """

    creation_counter = 0

    def __init__(self, title=None, description=None, argument_names=None):
        """
        Constructs a ArgumentGroup instance

        @param title The title of the group displayed as headline
        @param description A detailed description of the argument group
        @param argument_names A list of strings containing the Arguments to be
                              grouped
        """
        self.title = title
        self.description = description
        self.argument_names = argument_names or []
        self.arguments = []
        self.creation_counter = ArgumentGroup.creation_counter
        ArgumentGroup.creation_counter += 1

    def add_to_parser(self, parser):
        """
        Adds the group and its arguments to a argparse.ArgumentParser instance

        @param parser A argparse.ArgumentParser instance
        """
        self.group = parser.add_argument_group(self.title, self.description)
        for arg in self.arguments:
            arg.add_to_parser(self.group)

    def set_name(self, name):
        """
        Sets the name of this group. Normally this method should not be called
        directly. It is used by the ArgumentsCollectorMetaClass.

        @param name A string for a name
        """
        self.name = name

    def add_argument(self, arg):
        """
        Adds a Argument to this group.
        Normally this method should not be called directly.
        It is used by the ArgumentsCollectorMetaClass.

        @parma arg An Argument instance to be added to this group.
        """
        self.arguments.append(arg)


class Argument(object):

    """
    A class to declarative define positional arguments at a class

    Usage:
        class MyParser(Parser):

            arg1 = Argument(help="A first string argument")
            arg2 = Argument(type=int)
            arg3 = Argument(nargs=2)
    """

    creation_counter = 0

    def __init__(self, *args, **kwargs):
        """
        Constructs an Argument instance

        args and kwargs are passed directly to
        argparse.ArgumentParser.add_argument
        """
        self.args = args
        self.kwargs = kwargs
        self.creation_counter = Argument.creation_counter
        Argument.creation_counter += 1

    def _get_kwargs(self):
        if self.args:
            return self.kwargs

        kwargs = {"dest": self.name}
        kwargs.update(self.kwargs)
        return kwargs

    def _get_args(self):
        return self.args

    def add_to_parser(self, parser):
        """
        Adds the argument to an argparse.ArgumentParser instance

        @param parser An argparse.ArgumentParser instance
        """
        kwargs = self._get_kwargs()
        args = self._get_args()
        parser.add_argument(*args, **kwargs)

    def set_name(self, name):
        """
        Sets the name of this Argument.
        Normally this method should not be called directly.
        It is used by the ArgumentsCollectorMetaClass.

        @param name A string for a name
        """
        self.name = name


class OptionArgument(Argument):

    """
    A class to declarative define (optional) arguments at a class

    Usage:
        class MyParser(Parser):

            arg1 = OptionalArgument(help="A first string argument")
            arg2 = OptionalArgument(type=int)
            arg3 = OptionalArgument(nargs=2)
            arg4 = OptionalArgument(required=True)
    """

    prefix_chars = "--"

    def _get_args(self):
        args = self.args
        if not args:
            args = (self.prefix_chars + self.name,)
        return args


class SubparsersMixin(object):

    """
    A mixin class intended to add subparsers to parser
    """

    default_subparsers_kwargs = {
        "title": "list of commands",
    }

    default_subparsers_args = []

    def __init__(self, *args, **kwargs):
        self.subparsers = []
        self.subparsers_args = []
        self.subparsers_kwargs = {}
        self.default_subparsers_kwargs = copy.copy(
            self.default_subparsers_kwargs)
        self.default_subparsers_args = copy.copy(
            self.default_subparsers_args)
        super(SubparsersMixin, self).__init__(*args, **kwargs)

    def set_subparsers_args(self, *args, **kwargs):
        """
        Sets args and kwargs that are passed when creating a subparsers group in
        a argparse.ArgumentParser i.e. when calling
        argparser.ArgumentParser.add_subparsers
        """
        self.subparsers_args = args
        self.subparsers_kwargs = kwargs

    def add_subparser(self, parser):
        """
        Adds a Subparser instance to the list of subparsers

        @param parser A Subparser instance
        """
        self.subparsers.append(parser)

    def get_default_subparsers_kwargs(self):
        """
        Returns the default kwargs to be passed to
        argparse.ArgumentParser.add_subparsers
        """
        return self.default_subparsers_kwargs

    def get_default_subparsers_args(self):
        """
        Returns the default args to be passed to
        argparse.ArgumentParser.add_subparsers
        """
        return self.default_subparsers_args

    def add_subparsers(self, parser):
        """
        Adds the subparsers to an argparse.ArgumentParser

        @param parser An argparse.ArgumentParser instance
        """
        if not self.subparsers:
            return

        args = self.subparsers_args or self.get_default_subparsers_args()
        kwargs = self.subparsers_kwargs or self.get_default_subparsers_kwargs()
        subs = parser.add_subparsers(*args, **kwargs)

        for subparser in self.subparsers:
            subparser.add_to_parser(subs)


class Parser(SubparsersMixin):

    """
    Main class to create cli parser

    Most of the times your parser should be directly be derived from this class.
    """

    __metaclass__ = ArgumentsCollectorMetaClass

    def __init__(self, *args, **kwargs):
        super(Parser, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def create_argparser(self):
        """
        Method to create and initalize an argparser.ArgumentParser
        """
        parser = argparse.ArgumentParser(*self.args, **self.kwargs)
        for name, group in self.base_groups:
            group.add_to_parser(parser)
        for name, arg in self.base_arguments:
            arg.add_to_parser(parser)
        self.add_subparsers(parser)
        self.parser = parser

    def parse_args(self, *args, **kwargs):
        self.create_argparser()
        return self.parser.parse_args(*args, **kwargs)

    def parse_known_args(self, *args, **kwargs):
        self.create_argparser()
        return self.parser.parse_known_args(*args, **kwargs)

    def print_usage(self, *args, **kwargs):
        self.create_argparser()
        self.parser.print_usage(*args, **kwargs)

    def print_version(self, *args, **kwargs):
        self.create_argparser()
        self.parser.print_version(*args, **kwargs)

    def print_help(self, *args, **kwargs):
        self.create_argparser()
        self.parser.print_help(*args, **kwargs)


class Subparser(SubparsersMixin):

    """
    A subparser class

    Usage:
        Cmd1Parser(Subparser):
            optarg1 = OptionalArgument()

        MyParser(Parser):
            arg1 = Argument("name")

        parser = MyParser()
        parser.add_subparser(Cmd1Parser("cmd1", help="my cmd1"))
    """

    __metaclass__ = ArgumentsCollectorMetaClass

    def __init__(self, *args, **kwargs):
        super(Subparser, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def add_to_parser(self, subparsers):
        """
        Adds this Subparser to the subparsers created by
        argparse.ArgumentParser.add_subparsers method.

        @param subparsers Normally a _SubParsersAction instance created by
        argparse.ArgumentParser.add_subparsers method
        """
        parser = subparsers.add_parser(*self.args, **self.kwargs)
        for name, group in self.base_groups:
            group.add_to_parser(parser)
        for name, arg in self.base_arguments:
            arg.add_to_parser(parser)
        self.add_subparsers(parser)


if __name__ == "__main__":
    class MySubParser(Subparser):
        all = OptionArgument()
        none = OptionArgument()

        group = ArgumentGroup(title="TGroup", argument_names=["none", "all"])

    class MySubSubParser(Subparser):
        new = OptionArgument()

    class MyParser(Parser):

        group1 = ArgumentGroup(title="MyGroup", argument_names=["abc"])

        abc = OptionArgument(type=int)
        hij = OptionArgument("--old")

    mysubparser = MySubParser("cmd1", help="my cmd1")
    mysubsubparser = MySubSubParser("sub1", help="subsub1")
    mysubparser.add_subparser(mysubsubparser)
    myparser = MyParser()
    myparser.add_subparser(mysubparser)
    print myparser.parse_args()
