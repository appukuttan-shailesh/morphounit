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
        {'cell_name': { 'morph_feature_name_1': {'value': ['X0_1 some_unit', 'X0_2 some_unit', ...] },
                        'morph_feature_name_2': {'value': ['X1_1 some_unit', 'X1_2 some_unit', ...] },
                        ...
                      }
        }
        """
        raise NotImplementedError()

    def get_morph_feature_value(self):
        """ returns the morphological feature in a model of a digitally reconstructed neuron """
        return self.get_morph_feature_info()
