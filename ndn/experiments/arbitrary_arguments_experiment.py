from ndn.experiments.experiment import Experiment

class AbitraryArgumentsExperiment(Experiment):
    def __init__(self, args):
        Experiment.__init__(self, args)
        if "ds" in self.arbArgs:
            self.ds = int(self.arbArgs["ds"])
        else:
            self.ds = 1000

        if "logging" in self.arbArgs:
            self.logging = self.arbArgs["logging"]
            if self.logging == "true":
                self.logging = True
            else:
                self.logging = False
        else:
            self.logging = False

    def setup(self):
        pass

    def run(self):
        print("Argument ds: {}".format(self.ds))
        print("Argument logging: {}".format(self.logging))

    @staticmethod
    def arguments():
        ''' This will be printed in sudo minindn --list-experiments'''
        return "--ds <num-data-streams> --logging <true/false>"

Experiment.register("arbitrary-arguments", AbitraryArgumentsExperiment)