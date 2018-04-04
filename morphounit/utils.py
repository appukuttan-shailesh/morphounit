import sciunit
import neurom
import os


class neuroM_loader(sciunit.Model):
    def __init__(self, name="neuroM_loader", model_path=None):
        sciunit.Model.__init__(self, name=name)
        self.description = "Module for loading morphologies via NeuroM"
        if model_path == None:
            raise ValueError("Please specify the path to the morphology file!")
        if not os.path.isfile(model_path):
            raise ValueError("Specified path to the morphology file is invalid!")
        self.morph_path = model_path
        #self.model = neurom.load_neuron(self.morph_path)
