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

""" This module contains classes to execute system processes """

import os
import subprocess

from kommons.errors import KommonRuntimeError


class SubprocessError(KommonRuntimeError):

    def __init__(self, command, returncode, output=None):
        self.command = command
        self.returncode = returncode
        self.output = output

    def get_returncode(self):
        return self.returncode

    def __str__(self):
        retval = "Command %s finished with return code %d" % (self.command,
                     self.returncode)
        if self.output:
            retval += "Output was: '%s'" % self.output
        return retval


class Process(object):

    def __init__(self, cmd):
        self.cmd = cmd

    def run(self, suppress_output=False, inputdata=None, extra_env=None, **kw):
        """Run command as a subprocess and wait until it is finished.

        The command should be given as a list of strings to avoid problems
        with shell quoting.  If the command exits with a return code other
        than 0, a SubprocessError is raised.
        """
        if inputdata is not None:
            kw["stdin"] = subprocess.PIPE
        if suppress_output:
            kw["stdout"] = open(os.devnull, "w")
            kw["stderr"] = open(os.devnull, "w")
        if extra_env:
            env = kw.get("env", os.environ).copy()
            env.update(extra_env)
            kw["env"] = env
        try:
            process = subprocess.Popen(self.cmd, **kw)
        except OSError, e:
            raise SubprocessError(self.cmd, e.errno, e.strerror)

        if inputdata is not None:
            process.stdin.write(inputdata)
            process.stdin.close()
        ret = process.wait()
        if ret != 0:
            raise SubprocessError(self.cmd, ret)

# vim: et sw=4 ts=4 tw=80:
