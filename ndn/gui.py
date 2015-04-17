#!/usr/bin/env python

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
    def __init__(self, notebook):
        Frame.__init__(self, notebook)

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

class NfdFrame(GuiFrame):
    def __init__(self, notebook):
        GuiFrame.__init__(self, notebook)

        self.frameLabel = "NFD"

        # log-level
        self.logLevel = StringVar(self)
        self.addDropDown("Log level:", self.logLevel, LOG_LEVELS, LOG_LEVELS[3])

class NlsrFrame(GuiFrame):

    HYPERBOLIC_STATES = [
        "off",
        "on",
        "dry-run"
    ]

    def __init__(self, notebook):
        GuiFrame.__init__(self, notebook)

        self.frameLabel = "NLSR"

        # general: network
        self.network = StringVar(self)
        self.addEntryBox("Network:", self.network, "/ndn/")

        # general: site
        self.site = StringVar(self)
        self.addEntryBox("Site:", self.site, "/edu/site")

        # general: router
        self.router = StringVar(self)
        self.addEntryBox("Router:", self.router, "/%C1.Router/cs/host")

        # general: log-level
        self.logLevel = StringVar(self)
        self.addDropDown("Log level:", self.logLevel, LOG_LEVELS, LOG_LEVELS[3])

        # hyperbolic: state
        self.hyperbolicState = StringVar(self)
        self.addDropDown("Hyperbolic routing:", self.hyperbolicState,
                         self.HYPERBOLIC_STATES, self.HYPERBOLIC_STATES[0])

        # hyperbolic: angle
        self.angle = StringVar(self)
        self.addEntryBox("Angle:", self.angle, "0.0")

        # hyperbolic: radius
        self.radius = StringVar(self)
        self.addEntryBox("Radius:", self.radius, "0.0")

        # fib: max-faces-per-prefix
        self.maxFaces = StringVar(self)
        self.addEntryBox("Max faces per prefix:", self.maxFaces, "0")


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

