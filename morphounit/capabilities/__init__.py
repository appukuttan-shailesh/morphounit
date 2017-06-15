"""MorphoUnit capabilities classes for NeuronUnit"""

import numpy as np
import sciunit

#==============================================================================

class ProvidesLayerInfo(sciunit.Capability):
    """
    Indicates that the model returns morphological information, namely:
    1) # of layers in the model
    2) height of each layer (in um)
    3) name of each layer
    """

    def get_layer_info(self):
        """
        Must return a dictionary of the form:
            { 'Layer 1': {'height': {'value': 'X0 um'}},
              'Layer 2/3': {'height': {'value': 'X1 um'}},
              ...                                        }
        """
        raise NotImplementedError()

    def get_num_layers(self):
        """ returns the # of layers in model """
        layer_info = self.get_layer_info()
        return len(layer_info)

    def get_layer_height(self, layer_name):
        """ should return the height of specified layer """
        layer_info = self.get_layer_info()
        if layer_name not in layer_info.keys():
            raise KeyError()
        else:
            return layer_info[layer_name]["height"]["value"]

#==============================================================================

class ProvidesDensityInfo(sciunit.Capability):
    """
    Indicates that the model returns morphological information, namely:
    1) density of cells in a specfic layer of the model (1000/mm3)
    """

    def get_density_info(self):
        """
        Must return a dictionary of the form:
            {"density": {"value": "XX 1000/mm3"}}
        """
        raise NotImplementedError()

    def get_cell_density(self):
        """ returns the cell density in model """
        density_info = self.get_density_info()
        return density_info["density"]["value"]

#==============================================================================
