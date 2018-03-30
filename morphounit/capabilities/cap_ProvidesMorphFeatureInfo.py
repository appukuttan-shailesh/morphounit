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
        {"cell1_ID": { 'cell_part_1': {'morph_feature_name_11': {'value': 'X11 units_str'},
                                       'morph_feature_name_12': {'value': 'X12 units_str'},
                                        ... },
                       'cell_part_2': {'morph_feature_name_21': {'value': 'X21 units_str'},
                                       'morph_feature_name_22': {'value': 'X22 units_str'},
                                        ... },
                       ... }
         "cell2_ID": { 'cell_part_1': {'morph_feature_name_11': {'value': 'Y11 units_str'},
                                       'morph_feature_name_12': {'value': 'Y12 units_str'},
                                        ... },
                       'cell_part_2': {'morph_feature_name_21': {'value': 'Y21 units_str'},
                                       'morph_feature_name_22': {'value': 'Y22 units_str'},
                                        ... },
                       ... }
        ... }
        """
        raise NotImplementedError()

    def get_morph_feature_value(self):
        """ returns the morphological feature in a model of a digitally reconstructed neuron """
        return self.get_morph_feature_info()
