import sciunit
import sciunit.scores as sci_scores
import morphounit.scores as mph_scores
import morphounit.capabilities as mph_cap
import morphounit.plots as mph_plots

import numpy as np
import copy

import quantities
import os

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#==============================================================================

class morph_feature_Test(sciunit.Test):
    """Tests a set of cell's morphological features"""
    score_type = mph_scores.CombineZScores

    def __init__(self, observation={}, name="Cell's morpho-feature test"):

        self.description = "Tests a set of cell's morpho-features in a digitally reconstructed neuron"
        require_capabilities = (mph_cap.ProvidesMorphFeatureInfo,)

        self.figures = []
        observation = self.format_data(observation)
        sciunit.Test.__init__(self, observation, name)
        self.directory_output = './output/'

    #----------------------------------------------------------------------

    def format_data(self, data):
        """
        This accepts data input in the form:
        ***** (observation) *****
        {"cell_kind": { "cell_part_1": {'morph_feature_name_11': {'mean value': 'X11_mean units_str', 'std': 'X11_std units_str'},
                                        'morph_feature_name_12': {'mean value': 'X12_mean units_str', 'std': 'X12_std units_str'},
                                        ... },
                        "cell_part_2": {'morph_feature_name_21': {'mean value': 'X21_mean units_str', 'std': 'X21_std units_str'},
                                        'morph_feature_name_22': {'mean value': 'X22_mean units_str', 'std': 'X22_std units_str'},
                                        ... },
                        ... }
        }
        ***** (prediction) *****
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

        It splits the values of mean, std and value to numeric quantities
        and their units (via quantities package)
        """
        dim_um = ['radius', 'radii', 'diameter', 'length', 'distance', 'extent']
        dim_non = ['order', 'number']
        for dict1 in data.values():  # Dict. with cell's part-features dictionary pairs for each cell
            for dict2 in dict1.values():    # Dict. with feature name-value pairs for each cell part: soma,
                                            # apical_dendrite, basal_dendrite or axon
                for dict3 in dict2.values(): # Dict. with 'value', 'mean' and 'std' values
                    for key, val in dict3.items():
                        quantity_parts = val.split()
                        number, units_str = float(quantity_parts[0]), " ".join(quantity_parts[1:])
                        try:
                            if any(sub_str in key for sub_str in dim_um):
                                assert (units_str == quantities.um | units_str == quantities.mm), \
                                    sciunit.Error("Values not in appropriate format. Required units: mm or um")
                            elif any(sub_str in key for sub_str in dim_non):
                                assert(units_str == quantities.dimensionless), \
                                    sciunit.Error("Values not in appropriate format. Required units: ", quantities.dimensionless)
                        finally:
                            dict3[key] = quantities.Quantity(number, units_str)

        return data

    # ----------------------------------------------------------------------

    def validate_observation(self, observation):
        for dict1 in observation.values():  # Dict. with cell's part-features dictionary pairs for each cell
            for dict2 in dict1.values():    # Dict. with feature name-value pairs for each cell part: soma,
                                            # apical_dendrite, basal_dendrite or axon
                for dict3 in dict2.values():  # Dict. with 'value' or 'mean' and 'std' values
                    for val in dict3.values():
                        assert type(val) is quantities.Quantity, \
                                sciunit.ObservationError(("Observation must be of the form "
                                                          "{'mean': 'XX units_str','std': 'YY units_str'}"))

    #----------------------------------------------------------------------

    def generate_prediction(self, model, verbose=False):
        """Implementation of sciunit.Test.generate_prediction"""
        self.model_name = model.name

        mod_prediction = model.get_morph_feature_info()

        dim_um = ['radius', 'radii', 'diameter', 'length', 'distance', 'extent']
        for key1, dict1 in mod_prediction.items():  # Dict. with cell's ID-features dict. pairs for each cell

            # Correcting cell's ID, by omitting enclosing directory's name and file's extension
            key0 = (key1.split("/")[-1]).split(".")[-2]
            mod_prediction.update({key0: dict1})
            del mod_prediction[key1]

            # Eliminating NeuroM's output about 'max_section_branch_order' for 'axons',
            # as such experimental data is not provided
            try:
                del dict1["axon"]["max_section_branch_order"]
            except KeyError:
                pass
            # Adding the right units and converting feature values to strings
            for dict2 in dict1.values():  # Dict. with feature name-value pairs for each cell part:
                # soma, apical_dendrite, basal_dendrite or axon
                for key, val in dict2.items():
                    if any(sub_str in key for sub_str in ['radius', 'radii']):
                        del dict2[key]
                        val *= 2
                        key = key.replace("radius", "diameter")
                        key = key.replace("radii", "diameter")
                    if any(sub_str in key for sub_str in dim_um):
                        dict2[key] = dict(value=str(val) + ' um')
                    else:
                        dict2[key] = dict(value=str(val))

        prediction = self.format_data(mod_prediction)
        return prediction

    #----------------------------------------------------------------------

    def compute_score(self, observation, prediction, verbose=True):
        """Implementation of sciunit.Test.score_prediction"""

        self.observation = observation
        self.prediction = prediction


        # Computing the scores
        cell_t = observation.keys()[0]  # Cell type

        score_cell_dict = dict.fromkeys([key0 for key0 in prediction.keys()], [])
        scores_feature_dict = copy.deepcopy(prediction)
        for key0 in scores_feature_dict:  # cell_ID keys
            scores_cell_list = list()
            for key1 in scores_feature_dict[key0]:  # cell's part: soma, axon, apical_dendrite or basal_dendrite
                for key2 in scores_feature_dict[key0][key1]:  # features names
                    score_value = sci_scores.ZScore.compute(observation[cell_t][key1][key2],
                                                           prediction[key0][key1][key2]).score
                    scores_cell_list.extend([score_value])

                    del scores_feature_dict[key0][key1][key2]["value"]
                    scores_feature_dict[key0][key1][key2]["score"] = score_value

            score_cell_dict[key0] = {"Combined-ZScore": mph_scores.CombineZScores.compute(scores_cell_list)}

        self.score_dict = scores_feature_dict

        # Taking the maximum of the cell's scores as the overall score for the Test
        max_score = max([dict1["Combined-ZScore"].score for dict1 in score_cell_dict.values()])
        self.score = mph_scores.CombineZScores(max_score)
        self.score.description = "A simple Z-score"

        # create output directory
        self.path_test_output = self.directory_output + self.model_name + '/'
        if not os.path.exists(self.path_test_output):
            os.makedirs(path_test_output)

        # Saving table with results
        txt_table = mph_plots.TxtTable_MorphFeatures(self)
        table_file = txt_table.create()
        self.figures.append(table_file)

        # save figure with mean, std, value for observation and prediction
        '''
        fig = plt.figure()
        x = range(len(observation))
        ix = 0

        y_mean = observation["NeuriteLength"]["mean"]
        y_std = observation["NeuriteLength"]["std"]
        y_value = prediction["NeuriteLength"]["value"]
        ax_o = plt.errorbar(ix, y_mean, yerr=y_std, ecolor='black', elinewidth=2,
                        capsize=5, capthick=2, fmt='ob', markersize='5', mew=5)
        ax_p = plt.plot(ix, y_value, 'rx', markersize='8', mew=2)

        ix = ix + 1
        xlabels = 'Morpho feature' # observation.keys()
        plt.xticks(x, xlabels, rotation=20)
        plt.tick_params(labelsize=11)
        plt.figlegend((ax_o,ax_p[0]), ('Observation', 'Prediction',), 'upper right')
        plt.margins(0.1)
        plt.ylabel("Morpho-feature")
        fig = plt.gcf()
        fig.set_size_inches(8, 6)

        filename = self.path_test_output + 'data_plot' + '.pdf'
        plt.savefig(filename, dpi=600,)
        self.figures.append(filename)

        # save figure with Z-score data
        ind = len(observation) ## = 1
        width = 0.35
        # score_lf = float(str(score).split()[2])

        # plt.bar(ind, score_lf, width, color='blue')
        plt.xlim(0, 4)
        # plt.figlegend(ax_score, ('Z-Score',), 'upper right')
        plt.ylabel("Score value")

        frame_bars = plt.gca()
        frame_bars.axes.get_xaxis().set_visible(False)

        fig_bars = plt.gcf()
        fig_bars.set_size_inches(8, 6)
        '''

        return self.score

    def bind_score(self, score, model, observation, prediction):
        score.related_data["figures"] = self.figures
        return score
