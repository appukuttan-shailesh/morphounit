import sciunit
import sciunit.scores
import morphounit.scores
import morphounit.capabilities as cap
import morphounit.plots as plots

import quantities
import os

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import OrderedDict

#===============================================================================

class LayerHeightTest(sciunit.Test):
    """Tests the height of model layers"""
    score_type = morphounit.scores.CombineZScores
    id = "/tests/3?version=8"

    def __init__(self,
                 observation={},
                 name="Layer Height Test"):
        description = ("Tests the heights of all layers in model")
        self.units = quantities.um
        required_capabilities = (cap.ProvidesLayerInfo,)

        observation = self.format_data(observation)
        self.figures = []
        sciunit.Test.__init__(self, observation, name)

        self.directory_output = './output/'

    #----------------------------------------------------------------------

    def format_data(self, data):
        """
        This accepts data input in the form:
        ***** (observation) *****
        {'Layer 1': {'height': {'mean': 'X0 um', 'std': 'Y0 um'}},
         'Layer 2/3': {'height': {'mean': 'X1 um', 'std': 'Y1 um'}},
         ...                                                       }
        ***** (prediction) *****
        { 'Layer 1': {'height': {'value': 'X0 um'}},
          'Layer 2/3': {'height': {'value': 'X1 um'}},
          ...                                        }
        and splits the values of mean and std to numeric quantities
        and their units (via quantities package).
        """
        for key0 in data.keys():
            for key, val in data[key0]["height"].items():
                try:
                    quantity_parts = val.split(" ")
                    number = float(quantity_parts[0])
                    units_str = " ".join(quantity_parts[1:])
                    assert (units_str == self.units.symbol)
                    data[key0]["height"][key] = quantities.Quantity(number, self.units)
                except AssertionError:
                    raise sciunit.Error("Values not in appropriate format. Required units: ", self.units.symbol)
                except:
                    raise sciunit.Error("Values not in appropriate format.")
        return data

    #----------------------------------------------------------------------

    def validate_observation(self, observation):
        try:
            for key0 in observation.keys():
                for key, val in observation[key0]["height"].items():
                    assert type(observation[key0]["height"][key]) is quantities.Quantity
        except Exception:
            raise sciunit.ObservationError(
                ("Observation must return a dictionary of the form:"
                "{'Layer 1': {'height': {'mean': 'X0 um', 'std': 'Y0 um'}},"
                " 'Layer 2/3': {'height': {'mean': 'X1 um', 'std': 'Y1 um'}},"
                " ...                                                       }))"))

    #----------------------------------------------------------------------

    def generate_prediction(self, model, verbose=False):
        """Implementation of sciunit.Test.generate_prediction."""
        self.model_name = model.name
        prediction = model.get_layer_info()
        prediction = self.format_data(prediction)
        return prediction

    #----------------------------------------------------------------------

    def compute_score(self, observation, prediction, verbose=False):
        """Implementation of sciunit.Test.score_prediction."""
        try:
            assert len(observation) == len(prediction)
        except Exception:
            # or return InsufficientDataScore ??
            raise sciunit.InvalidScoreError(("Difference in # of layers."
                                    " Cannot continue test for layer heights."))

        zscores = {}
        for key0 in observation.keys():
            zscores[key0] = sciunit.scores.ZScore.compute(observation[key0]["height"], prediction[key0]["height"]).score
        self.score = morphounit.scores.CombineZScores.compute(zscores.values())
        self.score_dict = zscores
        self.score.description = "Mean of absolute Z-scores"

        # create output directory
        self.path_test_output = self.directory_output + 'layer_height/' + self.model_name + '/'
        if not os.path.exists(self.path_test_output):
            os.makedirs(self.path_test_output)

        self.observation = observation
        self.prediction = prediction
        # create relevant output files
        # 1. Error Plot
        err_plot = plots.ErrorPlot(self)
        err_plot.xlabels = OrderedDict(sorted(self.observation.items(), key=lambda t: t[0]))
        err_plot.ylabel = "Layer Height (um)"
        file1 = err_plot.create()
        self.figures.append(file1)
        # 2. Text Table
        txt_table = plots.TxtTable(self)
        file2 = txt_table.create(mid_keys=["height"])
        self.figures.append(file2)
        """
        # save document with Z-score data
        filename = path_test_output + 'score_summary' + '.txt'
        dataFile = open(filename, 'w')
        dataFile.write("==============================================================================\n")
        dataFile.write("Test Name: %s\n" % self.name)
        dataFile.write("Model Name: %s\n" % self.model_name)
        dataFile.write("------------------------------------------------------------------------------\n")
        dataFile.write("Layer #\tExpt. mean\tExpt. std\tModel value\tZ-score\n")
        dataFile.write("..............................................................................\n")
        for key0 in zscores.keys():
            o_mean = observation[key0]["height"]["mean"]
            o_std = observation[key0]["height"]["std"]
            p_value = prediction[key0]["height"]["value"]
            dataFile.write("%s\t%s\t%s\t%s\t%s\n" % (key0, o_mean, o_std, p_value, zscores[key0]))
        dataFile.write("------------------------------------------------------------------------------\n")
        dataFile.write("Combined Score: %s\n" % score)
        dataFile.write("==============================================================================\n")
        dataFile.close()
        self.figures.append(filename)
        """

        return self.score

    #----------------------------------------------------------------------

    def bind_score(self, score, model, observation, prediction):
        score.related_data["figures"] = self.figures
        return score
