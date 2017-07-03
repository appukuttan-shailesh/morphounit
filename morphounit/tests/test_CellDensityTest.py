import sciunit
import sciunit.scores
import morphounit.capabilities as cap

import quantities
import os

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#===============================================================================

class CellDensityTest(sciunit.Test):
    """Tests the cell density"""
    score_type = sciunit.scores.ZScore
    id = "/tests/6?version=7"

    def __init__(self,
                 observation={},
                 name="Cell Density Test"):

        self.k_per_mm3 = quantities.UnitQuantity(
                    '1000/mm3', 1e3/quantities.mm**3, symbol='1000/mm3')
        units = self.k_per_mm3

        observation = self.format_data(observation)

        required_capabilities = (cap.ProvidesDensityInfo,)
        description = ("Tests the cell density within a single layer of model")

        self.figures = []
        sciunit.Test.__init__(self, observation, name)

        self.directory_output = './output/'

    #----------------------------------------------------------------------

    def format_data(self, data):
        """
        This accepts data input in the form:
        ***** (observation) *****
        {"density": {"mean": "XX 1000/mm3", "std": "YY 1000/mm3"}}
        ***** (prediction) *****
        {"density": {"value": "ZZ 1000/mm3"}}

        It splits the values of mean, std, value to numeric quantities
        and their units (via quantities package).
        """
        for key,val in data["density"].items():
            try:
                quantity_parts = val.split(" ")
                number = float(quantity_parts[0])
                units = " ".join(quantity_parts[1:])
                if units == "1000/mm3":
                    data["density"][key] = quantities.Quantity(number, self.k_per_mm3)
            except ValueError:
                raise sciunit.Error("Values not in appropriate format. Required units: 1000/mm3")
        return data

    #----------------------------------------------------------------------

    def validate_observation(self, observation):
        try:
            for key, val in observation["density"].items():
                assert type(observation["density"][key]) is quantities.Quantity
        except Exception as e:
            raise sciunit.ObservationError(
                ("Observation must return a dictionary of the form:"
                 "{'density': {'mean': 'XX 1000/mm3', 'std': 'YY 1000/mm3'}}"))

    #----------------------------------------------------------------------

    def generate_prediction(self, model, verbose=False):
        """Implementation of sciunit.Test.generate_prediction."""
        self.model_name = model.name
        prediction = model.get_density_info()
        prediction = self.format_data(prediction)
        return prediction

    #----------------------------------------------------------------------

    def compute_score(self, observation, prediction, verbose=False):
        """Implementation of sciunit.Test.score_prediction."""
        print "observation = ", observation
        print "prediction = ", prediction
        score = sciunit.scores.ZScore.compute(observation["density"], prediction["density"])
        score.description = "A simple Z-score"

        # create output directory
        path_test_output = self.directory_output + 'cell_density/' + self.model_name + '/'
        if not os.path.exists(path_test_output):
            os.makedirs(path_test_output)

        # save figure with mean, std, value for observation and prediction
        fig = plt.figure()
        x = range(len(observation)) ## = 1
        ix = 0
        for key0 in observation.keys():
            y_mean = observation["density"]["mean"]
            y_std = observation["density"]["std"]
            y_value = prediction["density"]["value"]
            ax_o = plt.errorbar(ix, y_mean, yerr=y_std, ecolor='black', elinewidth=2,
                            capsize=5, capthick=2, fmt='ob', markersize='5', mew=5)
            ax_p = plt.plot(ix, y_value, 'rx', markersize='8', mew=2)
            ix = ix + 1
        xlabels = 'layer' # observation.keys()
        plt.xticks(x, xlabels, rotation=20)
        plt.tick_params(labelsize=11)
        plt.figlegend((ax_o,ax_p[0]), ('Observation', 'Prediction',), 'upper right')
        plt.margins(0.1)
        plt.ylabel("Cell Density (# of cells/mm3)")
        fig = plt.gcf()
        fig.set_size_inches(8, 6)
        filename = path_test_output + 'data_plot' + '.pdf'
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
        o_mean = observation["density"]["mean"]
        o_std = observation["density"]["std"]
        p_value = prediction["density"]["value"]
        dataFile.write("%s\t%s\t%s\t%s\t%s\n" % (key0, o_mean, o_std, p_value, score))
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
