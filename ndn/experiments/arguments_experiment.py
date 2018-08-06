# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2018, The University of Memphis,
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

from ndn.experiments.experiment import Experiment

class ArgumentsExperiment(Experiment):
    def __init__(self, args):
        Experiment.__init__(self, args)
        self.ds = self.options.arguments.ds
        self.logging = self.options.arguments.logging

    def start(self):
        pass

    def setup(self):
        pass

    def run(self):
        print("Argument ds: {}".format(self.ds))
        print("Argument logging: {}".format(self.logging))

    @staticmethod
    def parseArguments(parser):
        parser.add_argument("--ds", dest="ds", default="1000",
                            help="[Arguments Experiment] Number of data streams")
        parser.add_argument("--logging", dest="logging", action="store_true",
                            help="[Arguments Experiment] Enable logging")

Experiment.register("args-exp", ArgumentsExperiment)