# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2017, The University of Memphis,
#                          Arizona Board of Regents,
#                          Regents of the University of California.
#
# This file is part of Mini-NDN.
# See AUTHORS.md for a complete list of Mini-NDN authors and contributors.
#
# Mini-NDN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mini-NDN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mini-NDN, e.g., in COPYING.md file.
# If not, see <http://www.gnu.org/licenses/>.

import os
class _WifiExperimentManager:

    class Error(Exception):
        def __init__(self, what):
            self.what = what
        def __str__(self):
            return repr(self.what)

    instance = None

    def __init__(self):
        self.experiments = {}

    def loadModules(self):
        currentDir = os.path.dirname(__file__)
        experimentDir = "%s/%s" % (currentDir, "experiments")
        experimentModule = "ndnwifi.experiments"
        # Import and register experiments
        for root, dirs, files in os.walk(experimentDir):
            for filename in files:
                if filename.endswith(".py") and filename != "__init__.py":
                    module = filename.replace(".py", "")
                    __import__("%s.%s" % (experimentModule, module))

    def register(self, name, experimentClass):
        if name not in self.experiments:
            self.experiments[name] = experimentClass
        else:
            raise _WifiExperimentManager.Error("Experiment '%s' has already been registered" % name)

    def create(self, name, args):
        if name in self.experiments:
            return self.experiments[name](args)
        else:
            return None

def __getInstance():
    if _WifiExperimentManager.instance is None:
        _WifiExperimentManager.instance = _WifiExperimentManager()
        _WifiExperimentManager.instance.loadModules()
    return _WifiExperimentManager.instance

def register(name, experimentClass):
    manager = __getInstance()
    manager.register(name, experimentClass)

def create(name, args):
    manager = __getInstance()
    return manager.create(name, args)

def getExperimentNames():
    manager = __getInstance()

    experimentNames = []

    for key in manager.experiments:
        experimentNames.append(key)

    return experimentNames
