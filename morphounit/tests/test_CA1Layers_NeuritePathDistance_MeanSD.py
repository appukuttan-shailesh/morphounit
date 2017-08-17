import sciunit
import sciunit.scores
import morphounit.capabilities as cap

import quantities
import os

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#==============================================================================


class CA1NeuritePathDistanceTest(sciunit.Test):
    """Tests a neurite path-distance across the layers of Hippocampus CA1"""
    score_type = sciunit.scores.ZScore
    id = "/tests/9?version=12"

    def __init__(self, observation={}, name="Neurite path-distance test"):

        description = ("Tests the neurite path-distance across Hippocampus CA1 layers of a digitally reconstructed neuron")
        require_capabilities = (cap.ProvidesCA1NeuritePathDistanceInfo,)
        units = quantities.um

        self.figures = []
        observation = self.format_data(observation)
        sciunit.Test.__init__(self, observation, name)
        self.directory_output = './output/'

    #----------------------------------------------------------------------


