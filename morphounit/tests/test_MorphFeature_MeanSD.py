import sciunit
import sciunit.scores as sci_scores
import morphounit.scores as mph_scores
import morphounit.capabilities as mph_cap

import numpy as np
import quantities
import os

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#==============================================================================

class morph_feature_Test(sciunit.Test):
    """Tests a set of neurite's morphological features"""
    score_type = sci_scores.ZScore
    id = "/tests/9?version=12"

    def __init__(self, observation={}, name="Cell's morpho-feature test"):

        description = "Tests a set of Cell's morpho-features in a digitally reconstructed neuron"
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
        dim_non = ['order', 'number'']
        for key0 in data.keys():  # Cell ID
            for key, val in data[key0].items():  # Dict. with cell's part-feature dictionary pairs for each cell
                try:
                    quantity_parts = val.split()
                    number, units_str = float(quantity_parts[0]), " ".join(quantity_parts[1:])
                    if any(sub_str in key for sub_str in dim_um):
                        assert (units_str==quantities.um), \
                            sciunit.Error("Values not in appropriate format. Required units: ", quantities.um)
                    elif any(sub_str in key for sub_str in dim_non):
                        assert(units_str==quantities.dimensionless), \
                            sciunit.Error("Values not in appropriate format. Required units: ", quantities.dimensionless)
                finally:
                    data[key0][key] = quantities.Quantity(number, units_str)

        return data

    # ----------------------------------------------------------------------

    def validate_observation(self, observation):
        for dict1 in observation.values():  # Dict. with cell's part-features dictionary pairs for each cell
            for dict2 in dict1.values():  # Dict. with feature name-value pairs for each cell part:
                                          # soma, apical_dendrite, basal_dendrite or axon
                for val in dict2.values():
                    assert type(val) is quantities.Quantity, \
                            sciunit.ObservationError(("Observation must be of the form "
                                                            "{'mean': 'XX units_str','std': 'YY units_str'}"))

    #----------------------------------------------------------------------

    def generate_prediction(self, model, verbose=False):
        """Implementation of sciunit.Test.generate_prediction"""
        self.model_name = model.name

        prediction = model.get_morph_feature_info()

        prediction = self.format_data(prediction)
        return prediction

    #----------------------------------------------------------------------

    def compute_score(self, observation, prediction, verbose=True):
        """Implementation of sciunit.Test.score_prediction"""
        score.description = "A simple Z-score"

        print "observation = ", observation
        print "prediction = ", prediction
        # Computing the scores
        scores_feature_dict = prediction.copy()

        for key0 in scores_feature_dict.keys():  # cell ID (in prediction) or cell_kind (in observation)
            for key1 in scores_feature_dict[key0].keys(): # Dict. with cell's part-feature dictionary pairs for each cell
                for key2 in scores_feature_dict.keys(): # Dict. with feature name-value pairs for each cell part:
                                                        # soma, axon, apical_dendrite or basal_dendrite
                    scores_feature_dict[key0][key1][key2] = sci_scores.ZScore.compute(observation[key0][key1][key2],

        print "scores_feature_dict = ", scores_feature_dict                                                                                      prediction[key0][key1][key2])
        # self.score = mph_scores.CombineZScores.compute(zscores.values())
        self.score = scores_feature_dict[key0][key1][key2]

        # create output directory
        path_test_output = self.directory_output + self.model_name + '/'
        if not os.path.exists(path_test_output):
            os.makedirs(path_test_output)

        # save figure with mean, std, value for observation and prediction
        fig = plt.figure()
        x = range(len(observation))
        ix = 0
        '''
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
        '''
        filename = path_test_output + 'data_plot' + '.pdf'
        plt.savefig(filename, dpi=600,)
        self.figures.append(filename)

        # save figure with Z-score data
        ind = len(observation) ## = 1
        width = 0.35
        score_lf = float(str(score).split()[2])

        plt.bar(ind, score_lf, width, color='blue')
        plt.xlim(0, 4)
        plt.figlegend(ax_score, ('Z-Score',), 'upper right')
        plt.ylabel("Score value")

        frame_bars = plt.gca()
        frame_bars.axes.get_xaxis().set_visible(False)

        fig_bars = plt.gcf()
        fig_bars.set_size_inches(8, 6)

        filename = path_test_output + 'score_plot' + '.pdf'
        plt.savefig(filename, dpi=600,)
        self.figures.append(filename)

        '''
        # save document with Z-score data
        filename = path_test_output + 'score_summary' + '.txt'
        dataFile = open(filename, 'w')
        dataFile.write("==============================================================================\n")
        dataFile.write("Test Name: %s\n" % self.name)
        dataFile.write("Model Name: %s\n" % self.model_name)
        dataFile.write("------------------------------------------------------------------------------\n")
        dataFile.write("Parameter #\tExpt. mean\tExpt. std\tModel value\tZ-score\n")
        dataFile.write("..............................................................................\n")
        o_mean = observation["NeuriteLength"]["mean"]
        o_std = observation["NeuriteLength"]["std"]
        p_value = prediction["NeuriteLength"]["value"]
        dataFile.write("%s\t%s\t%s\t%s\t%s\n" % ("NeuriteLength", o_mean, o_std, p_value, score))
        dataFile.write("------------------------------------------------------------------------------\n")
        dataFile.write("Final Score: %s\n" % score)
        dataFile.write("==============================================================================\n")
        dataFile.close()
        self.figures.append(filename)
        '''
        return score  # ----------------------------------------------------------------------

    def bind_score(self, score, model, observation, prediction):
        score.related_data["figures"] = self.figures
        return score
