import sciunit
import sciunit.scores
import morphounit.capabilities as cap

import quantities
import os

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#==============================================================================

class NeuroM_SomaDiamTest_MeanSD(sciunit.Test):
    """
    Tests the soma diameter for morphologies loaded via NeuroM
    Compares against Mean, SD; evaluates Z-Score
    """
    score_type = sciunit.scores.ZScore
    id = "/tests/8?version=10"

    def __init__(self,
                 observation={},
                 name="NeuroM soma diameter - mean, sd"):
        observation = self.format_data(observation)

        required_capabilities = (cap.HandlesNeuroM,)
        description = ("Tests the soma diameter for morphologies loaded via NeuroM")
        units = quantities.um

        self.figures = []
        sciunit.Test.__init__(self, observation, name)

        self.directory_output = './output/'

    #----------------------------------------------------------------------

    def format_data(self, data):
        """
        This accepts data input in the form:
        ***** (observation) *****
        {"diameter": {"mean": "X0 um", "std": "2.5 um"}}
        ***** (prediction) *****
        {"diameter": {"value" : "X0 um"}}
        and splits the values of mean and std to numeric quantities
        and their units (via quantities package).
        """
        for key,val in data["diameter"].items():
            try:
                quantity_parts = val.split(" ")
                number = float(quantity_parts[0])
                units = " ".join(quantity_parts[1:])
                data["diameter"][key] = quantities.Quantity(number, units)
            except ValueError:
                raise sciunit.Error("Values not in appropriate format. Required format: X0 um")
        return data

    #----------------------------------------------------------------------

    def validate_observation(self, observation):
        try:
            for key0 in observation.keys():
                for key, val in observation["diameter"].items():
                    assert type(observation["diameter"][key]) is quantities.Quantity
        except Exception as e:
            raise sciunit.ObservationError(
                ("Observation must return a dictionary of the form:"
                 "{'diameter': {'mean': 'XX um', 'std': 'YY um'}}"))

    #----------------------------------------------------------------------

    def generate_prediction(self, model, verbose=False):
        """Implementation of sciunit.Test.generate_prediction."""
        self.model_name = model.name
        prediction = model.get_soma_diameter_info()
        prediction = self.format_data(prediction)
        return prediction

    #----------------------------------------------------------------------

    def compute_score(self, observation, prediction, verbose=False):
        """Implementation of sciunit.Test.score_prediction."""
        print "observation = ", observation
        print "prediction = ", prediction
        score = sciunit.scores.ZScore.compute(observation["diameter"], prediction["diameter"])
        score.description = "A simple Z-score"

        # create output directory
        path_test_output = self.directory_output + 'soma_diameter_mean_sd/' + self.model_name + '/'
        if not os.path.exists(path_test_output):
            os.makedirs(path_test_output)

        # save figure with mean, std, value for observation and prediction
        fig = plt.figure()
        x = range(len(observation)) ## = 1
        ix = 0
        for key0 in observation.keys():
            y_mean = observation["diameter"]["mean"]
            y_std = observation["diameter"]["std"]
            y_value = prediction["diameter"]["value"]
            ax_o = plt.errorbar(ix, y_mean, yerr=y_std, ecolor='black', elinewidth=2,
                            capsize=5, capthick=2, fmt='ob', markersize='5', mew=5)
            ax_p = plt.plot(ix, y_value, 'rx', markersize='8', mew=2)
            ix = ix + 1
        xlabels = 'Soma' # observation.keys()
        plt.xticks(x, xlabels, rotation=20)
        plt.tick_params(labelsize=11)
        plt.figlegend((ax_o,ax_p[0]), ('Observation', 'Prediction',), 'upper right')
        plt.margins(0.1)
        plt.ylabel("Diameter (um)")
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
        dataFile.write("Parameter\tExpt. mean\tExpt. std\tModel value\tZ-score\n")
        dataFile.write("..............................................................................\n")
        o_mean = observation["diameter"]["mean"]
        o_std = observation["diameter"]["std"]
        p_value = prediction["diameter"]["value"]
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

