import sciunit

#==============================================================================

class ProvidesCA1NeuritePathDistanceInfo(sciunit.Capability):
    """
    Indicates that the model returns morphological information, namely:
    the neurite path distance of a digitally reconstructed cell
    across the four layers of CA1 subregion of Hippocampus: SLM, SR, SP and SO 
    """

    def get_CA1LayersNeuritePathDistance_info(self):
        """ Must return a dictionary of the form:
	    {
             "SLM": {'PathDistance': {'value':'X0 um'}},
              "SR": {'PathDistance': {'value':'X1 um'}},
              "SP": {'PathDistance': {'value':'X2 um'}},
              "SO": {'PathDistance': {'value':'X3 um'}}
            }
        """
        raise NotImplementedError()

    def get_CA1LayersNeuritePathDistance(self):
        """ Returns a list with the neurite path distance of a reconstructed neuron 
	    across the four layers of CA1 subregion of Hippocampus: SLM, SR, SP and SO	        
	"""
        CA1LayersNeuritePathDistance_info = self.get_CA1LayersNeuritePathDistance_info()
        return [ CA1LayersNeuritePathDistance_info["SLM"]['value'],
		  CA1LayersNeuritePathDistance_info["SR"]['value'],
		  CA1LayersNeuritePathDistance_info["SP"]['value'],
		  CA1LayersNeuritePathDistance_info["SO"]['value'] ]

