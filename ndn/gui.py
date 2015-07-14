# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015 The University of Memphis,
#                    Arizona Board of Regents,
#                    Regents of the University of California.
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

from Tkinter import *

LOG_LEVELS = [
    "NONE",
    "ERROR",
    "WARN",
    "INFO",
    "DEBUG",
    "TRACE",
    "ALL"
]

class GuiFrame(Frame):
    def __init__(self, notebook, prefValues, appId):
        Frame.__init__(self, notebook)

        self.prefValues = prefValues
        self.appId = appId

        self.row = 0
        self.column = 0

    def addEntryBox(self, label, variable, defaultValue=""):
        variable.set(defaultValue)

        Label(self, text=label).grid(row=self.row, sticky=E)
        entry = Entry(self, textvariable=variable)
        entry.grid(row=self.row, column=1)

        self.row += 1

    def addDropDown(self, label, variable, values, defaultValue=""):
        variable.set(defaultValue)

        Label(self, text=label).grid(row=self.row, sticky=E)

        self.entry = apply(OptionMenu, (self, variable) + tuple(values))
        self.entry.grid(row=self.row, column=1)

        self.row += 1

    def getPreferredOrDefaultValue(self, key, defaultValue):
        if self.appId in self.prefValues:
            return self.prefValues[self.appId][key]
        else:
            return defaultValue

class NfdFrame(GuiFrame):
    def __init__(self, notebook, prefValues):
        GuiFrame.__init__(self, notebook, prefValues, "nfd")

        self.frameLabel = "NFD"

        # log-level
        self.logLevel = StringVar(self)
        self.addDropDown("Log level:",
                         self.logLevel,
                         LOG_LEVELS,
                         self.getPreferredOrDefaultValue("log-level", LOG_LEVELS[3]))

    def getValues(self):
        return {
            "log-level": self.logLevel.get()
        }

class NlsrFrame(GuiFrame):

    HYPERBOLIC_STATES = [
        "off",
        "on",
        "dry-run"
    ]

    def __init__(self, notebook, prefValues):
        GuiFrame.__init__(self, notebook, prefValues, "nlsr")

        self.frameLabel = "NLSR"

        # general: network
        self.network = StringVar(self)
        self.addEntryBox("Network:",
                         self.network,
                         self.getPreferredOrDefaultValue("network", "/ndn"))

        # general: site
        self.site = StringVar(self)
        self.addEntryBox("Site:", self.site, self.getPreferredOrDefaultValue("site", "/edu/site"))

        # general: router
        self.router = StringVar(self)
        self.addEntryBox("Router:",
                         self.router,
                         self.getPreferredOrDefaultValue("router", "/%C1.Router/cs/host"))

        # general: log-level
        self.logLevel = StringVar(self)
        self.addDropDown("Log level:",
                         self.logLevel,
                         LOG_LEVELS,
                         self.getPreferredOrDefaultValue("log-level", LOG_LEVELS[3]))

        # hyperbolic: state
        self.hyperbolicState = StringVar(self)
        self.addDropDown("Hyperbolic routing:",
                         self.hyperbolicState,
                         self.HYPERBOLIC_STATES,
                         self.getPreferredOrDefaultValue("hyperbolic-state", self.HYPERBOLIC_STATES[0]))

        # hyperbolic: angle
        self.angle = StringVar(self)
        self.addEntryBox("Angle:", self.angle, self.getPreferredOrDefaultValue("angle", "0.0"))

        # hyperbolic: radius
        self.radius = StringVar(self)
        self.addEntryBox("Radius:", self.radius, self.getPreferredOrDefaultValue("radius", "0.0"))

        # fib: max-faces-per-prefix
        self.maxFaces = StringVar(self)
        self.addEntryBox("Max faces per prefix:",
                         self.maxFaces,
                         self.getPreferredOrDefaultValue("max-faces-per-prefix", "0"))

    def getValues(self):
        return {
            "network": self.network.get(),
            "site": self.site.get(),
            "router": self.router.get(),
            "log-level": self.logLevel.get(),
            "hyperbolic-state": self.hyperbolicState.get(),
            "angle": self.angle.get(),
            "radius": self.radius.get(),
            "max-faces-per-prefix": self.maxFaces.get()
        }

