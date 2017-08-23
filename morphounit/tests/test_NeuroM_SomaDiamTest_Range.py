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

#==============================================================================

class NeuroM_SomaDiamTest_Range(sciunit.Test):
    """
    Tests the soma diameter for morphologies loaded via NeuroM
    Compares against Min, Max allowed range;
    Score = True if within range, False otherwise
    """
    score_type = morphounit.scores.RangeScore
    id = "/tests/7?version=11"

    def __init__(self,
                 observation={},
                 name="NeuroM soma diameter - range"):
        description = ("Tests the soma diameter for morphologies loaded via NeuroM")
        self.units = quantities.um
        required_capabilities = (cap.HandlesNeuroM,)

        observation = self.format_data(observation)
        self.figures = []
        sciunit.Test.__init__(self, observation, name)

        self.directory_output = './output/'

    #----------------------------------------------------------------------

    def format_data(self, data):
        """
        This accepts data input in the form:
        ***** (observation) *****
        {"diameter": {"min": "X0 um", "max": "2.5 um"}}
        ***** (prediction) *****
        {"diameter": {"value" : "X0 um"}}
        and splits the values of min, max and value to numeric quantities
        and their units (via quantities package).
        """
        for key,val in data["diameter"].items():
            try:
                quantity_parts = val.split(" ")
                number = float(quantity_parts[0])
                units_str = " ".join(quantity_parts[1:])
                assert (units_str == self.units.symbol)
                data["diameter"][key] = quantities.Quantity(number, self.units)
            except AssertionError:
                raise sciunit.Error("Values not in appropriate format. Required units: ", self.units.symbol)
            except:
                raise sciunit.Error("Values not in appropriate format.")
        return data

    #----------------------------------------------------------------------

    def validate_observation(self, observation):
        try:
            for key0 in observation.keys():
                for key, val in observation["diameter"].items():
                    assert type(observation["diameter"][key]) is quantities.Quantity
        except Exception:
            raise sciunit.ObservationError(
                ("Observation must return a dictionary of the form:"
                 "{'diameter': {'min': 'XX um', 'max': 'YY um'}}"))

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
        self.score = morphounit.scores.RangeScore.compute(observation["diameter"], prediction["diameter"])
        self.score.description = "score is 0.0 if within range; otherwise difference"

        # create output directory
        self.path_test_output = self.directory_output + 'soma_diameter_range/' + self.model_name + '/'
        if not os.path.exists(self.path_test_output):
            os.makedirs(self.path_test_output)

        self.observation = observation
        self.prediction = prediction
        # create relevant output files
        # 1. Error Plot
        err_plot = plots.ErrorPlot(self)
        err_plot.xlabels = ["Soma"]
        err_plot.ylabel = "Diameter (um)"
        file1 = err_plot.create()
        self.figures.append(file1)
        # 2. Text Table
        txt_table = plots.TxtTable(self)
        file2 = txt_table.create()
        self.figures.append(file2)

        return self.score

    #----------------------------------------------------------------------

    def bind_score(self, score, model, observation, prediction):
        score.related_data["figures"] = self.figures
        return score
