import sciunit
import sciunit.scores
import morphounit.capabilities as mph_cap

import quantities
import os

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#==============================================================================

class morph_feature_Test(sciunit.Test):
    """Tests a set of neurite's morphological features"""
    score_type = sciunit.scores.ZScore
    id = "/tests/9?version=12"

    def __init__(self, observation={}, name="Neurite's morpho-feature test"):

        description = "Tests a set of neurite's morpho-features in a digitally reconstructed neuron"
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
        {"cell_kind": { "morph_feature_name_1": { "value": "X1_mean units_str", "std": "X1_std units_str" },
                        "morph_feature_name_2": { "value": "X2_mean units_str", "std": "X2_std units_str" },
                      ...
                      }
        }
        ***** (prediction) *****
        {'cell_name': { "morph_feature_name_1": {"value": ["X11_value units_str", "X12_value units_str", ...] },
                        "morph_feature_name_2": {"value": ["X21_value units_str", "X22_value units_str", ...] },
                        ...
                      }
        }

        It splits the values of mean, std and value to numeric quantities
        and their units (via quantities package)
        """

        for key0 in data.keys():
            for key, val in data[key0].items():
                try:
                    quantity_parts = val.split()
                    number, units_str = float(quantity_parts[0]), " ".join(quantity_parts[1:])
                    if key in ["soma diameter",
                               "dendritic X extent", "dendritic Y extent", "dendritic Z extent",
                               "dendritic field diameter", "total dendritic length",
                               "axonal X extent", "axonal Y extent", "axonal Z extent",
                               "axonal field diameter", "total axonal length"]:
                        assert (units_str==quantities.um), \
                            sciunit.Error("Values not in appropriate format. Required units: ", quantities.um)
                    elif key in ["number of primary dendrites", "number of axons", "max branch order"]:
                        assert(units_str==quantities.dimensionless), \
                            sciunit.Error("Values not in appropriate format. Required units: ", quantities.dimensionless)
                finally:
                    data[key0][key] = quantities.Quantity(number, units_str)

        return data

    # ----------------------------------------------------------------------

    def validate_observation(self, observation):
        for key0 in observation.keys():
            for val in observation[key0].values():
                assert type(val) is quantities.Quantity, \
                        raise sciunit.ObservationError(("Observation must be of the form "
                                                        "{'mean': 'XX units_str','std': 'YY units_str'}"))

    #----------------------------------------------------------------------

    def generate_prediction(self, model, verbose=False):
        """Implementation of sciunit.Test.generate_prediction"""
        self.model_name = model.name
        prediction = model.get_morph_feature_info()

        for key0 in prediction.morph_feature_info().keys():
            for key, val in prediction.morph_feature_info()[key0].items():
                if len(val)>1:
                    prediction.morph_feature_info()[key0][key] = mean(val)


        prediction = self.format_data(prediction)
        return prediction

    #----------------------------------------------------------------------

    def compute_score(self, observation, prediction, verbose=True):
        """Implementation of sciunit.Test.score_prediction"""
        print "observation = ", observation
        print "prediction = ", prediction
        score = sciunit.scores.ZScore.compute(observation["NeuriteLength"], prediction["NeuriteLength"])
        score.description = "A simple Z-score"

        # create output directory
        path_test_output = self.directory_output + 'neurite_length/' + self.model_name + '/'
        if not os.path.exists(path_test_output):
            os.makedirs(path_test_output)

        # save figure with mean, std, value for observation and prediction
        fig = plt.figure()
        x = range(len(observation)) ## = 1
        ix = 0

        y_mean = observation["NeuriteLength"]["mean"]
        y_std = observation["NeuriteLength"]["std"]
        y_value = prediction["NeuriteLength"]["value"]
        ax_o = plt.errorbar(ix, y_mean, yerr=y_std, ecolor='black', elinewidth=2,
                        capsize=5, capthick=2, fmt='ob', markersize='5', mew=5)
        ax_p = plt.plot(ix, y_value, 'rx', markersize='8', mew=2)

        ix = ix + 1
        xlabels = 'NeuriteLength' # observation.keys()
        plt.xticks(x, xlabels, rotation=20)
        plt.tick_params(labelsize=11)
        plt.figlegend((ax_o,ax_p[0]), ('Observation', 'Prediction',), 'upper right')
        plt.margins(0.1)
        plt.ylabel("Neurite Length (um)")
        fig = plt.gcf()
        fig.set_size_inches(8, 6)
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

        return score

    #----------------------------------------------------------------------

    def bind_score(self, score, model, observation, prediction):
        score.related_data["figures"] = self.figures
        return score

