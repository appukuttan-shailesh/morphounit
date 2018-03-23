import sciunit

#==============================================================================

class ProvidesMorphFeatureInfo(sciunit.Capability):
    """
    Indicates that the model returns morphological information, namely:
    morphological features values of a digitally reconstructed cell
    """

    def get_morph_feature_info(self):
        """
        Must return a dictionary of the form:
            { 'cell_name': { 'morph_feature_name_1': {'value': 'XX um'} },
                           { 'morph_feature_name_2': {'value': 'XX um'} }
                           ...
            }
        """
        raise NotImplementedError()

    def get_morph_feature_value(self):
        """ returns the morphological feature in a model of a reconstructed neuron """
        return self.get_morph_feature_info()
