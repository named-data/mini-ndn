from ndn.experiments.experiment import Experiment

class ArgumentsExperiment(Experiment):
    def __init__(self, args):
        Experiment.__init__(self, args)
        self.ds = self.arguments.ds
        self.logging = self.arguments.logging

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