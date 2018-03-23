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
        {'cell_name': { 'morph_feature_name_1': {'value': ['X0_1 um', 'X0_2 um', ...] }},
                      { 'morph_feature_name_2': {'value': ['X1_1 um', 'X1_2 um', ...] }}
                      ...
        }
        """
        raise NotImplementedError()

    def get_morph_feature_value(self):
        """ returns the morphological feature in a model of a digitally reconstructed neuron """
        return self.get_morph_feature_info()
