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


class CA1NeuritePathDistanceTest(sciunit.Test):
    """Tests a neurite path-distance across the layers of Hippocampus CA1"""
    score_type = sciunit.scores.ZScore
    id = "/tests/10?version=13"

    def __init__(self, observation={}, name="Neurite path-distance test"):

        description = ("Tests the neurite path-distance across Hippocampus CA1 layers of a digitally reconstructed neuron")
        require_capabilities = (cap.ProvidesCA1NeuritePathDistanceInfo,)
        units = quantities.um

        self.figures = []
        observation = self.format_data(observation)
        sciunit.Test.__init__(self, observation, name)
        self.directory_output = './output/'

    #----------------------------------------------------------------------

    def format_data(self, data):
        """
        This accepts data input in the form:
        ***** (observation) *****
	    {
             "SLM": {'PathDistance': {'mean':'X0 um', 'std': 'Y0 um'}},
              "SR": {'PathDistance': {'mean':'X1 um', 'std': 'Y1 um'}},
              "SP": {'PathDistance': {'mean':'X2 um', 'std': 'Y2 um'}},
              "SO": {'PathDistance': {'mean':'X3 um', 'std': 'Y3 um'}}
            }
        ***** (prediction) *****
	    {
             "SLM": {'PathDistance': {'value':'X0 um'}},
              "SR": {'PathDistance': {'value':'X1 um'}},
              "SP": {'PathDistance': {'value':'X2 um'}},
              "SO": {'PathDistance': {'value':'X3 um'}}
            }

        It splits the values of mean, std and value to numeric quantities
        and their units (via quantities package)
        """
        for key0 in data.keys():
	       for key, val in data[key0]["PathDistance"].items():
		  try:
		     quantity_parts = val.split()
		     number, units_str = float(quantity_parts[0]), " ".join(quantity_parts[1:])
		     assert (units_str == self.units.symbol)		     
		     data[key0]["PathDistance"][key] = quantities.Quantity(number, self.units)
                  except AssertionError:
                     raise sciunit.Error("Values not in appropriate format. Required units: ", self.units.symbol)
                  except:
                     raise sciunit.Error("Values not in appropriate format.")
        return data

    # ----------------------------------------------------------------------

    def validate_observation(self, observation):
        for key0 in data.keys():
	   for key1 in data[key0].keys():	
	       for val in data[key0][key1].values():
                  try:
                     assert type(val) is quantities.Quantity
                  except Exception as e:
                     raise sciunit.ObservationError(("Observation must be of the form "
                                                     "{'mean': XX um,'std': YY um}"))

    #----------------------------------------------------------------------

    def generate_prediction(self, model, verbose=False):
        """Implementation of sciunit.Test.generate_prediction"""

        self.model_name = model.name
        prediction = model.get_CA1LayersNeuritePathDistance_info()
        prediction = self.format_data(prediction)
        return prediction

    #----------------------------------------------------------------------

    def compute_score(self, observation, prediction, verbose=True):
        """Implementation of sciunit.Test.score_prediction"""
        try:
            assert len(observation) == len(prediction)
        except Exception:
            raise sciunit.InvalidScoreError(("Difference in # of layers."
                                    " Cannot continue test for neurite path-length across CA1 layers"))

        print "observation = ", observation
        print "prediction = ", prediction

        zscores = {}
        for key0 in observation.keys():
           zscores[key0] = sciunit.scores.ZScore.compute(observation[key0]["PathDistance"], prediction[key0]["PathDistance"])
        # self.score = morphounit.scores.CombineZScores.compute(zscores.values())

        # create output directory
        path_test_output = self.directory_output + 'neurite_PathDistance/' + self.model_name + '/'
        if not os.path.exists(path_test_output):
           os.makedirs(path_test_output)

        # save figure with Z-score data
        for key0 in observation.keys():
	   score_lf[key0] = float(str(zscores[key0]).split()[2])

	layers = range(len(observation))
	width = 0.35
	plt.bar(layers, score_lf, width, color='blue')
	plt.figlegend(ax_score, ('Z-Score',), 'upper right')
	plt.ylabel("Score value")

	frame_bars = plt.gca()
	frame_bars.axes.get_xaxis().set_visible(False)

	fig_bars = plt.gcf()
	fig_bars.set_size_inches(8, 6)

        filename = path_test_output + 'score_plot' + '.pdf'
        plt.savefig(filename, dpi=600,)
        self.figures.append(filename)


        return score

    #----------------------------------------------------------------------

    def bind_score(self, score, model, observation, prediction):
        score.related_data["figures"] = self.figures
        return score


