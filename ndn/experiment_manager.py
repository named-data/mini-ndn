#!/usr/bin/python

import os

class _ExperimentManager:

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
        experimentModule = "ndn.experiments"

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
            raise _ExperimentManager.Error("Experiment '%s' has already been registered" % name)

    def create(self, name, args):
        if name in self.experiments:
            return self.experiments[name](args)
        else:
            return None

def __getInstance():
    if _ExperimentManager.instance is None:
        _ExperimentManager.instance = _ExperimentManager()
        _ExperimentManager.instance.loadModules()

    return _ExperimentManager.instance

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
