import sciunit
import sciunit.scores
import morphounit.capabilities as cap
import morphounit.plots as plots

import quantities
import os

#===============================================================================

class CellDensityTest(sciunit.Test):
    """Tests the cell density"""
    score_type = sciunit.scores.ZScore
    id = "/tests/6?version=7"

    def __init__(self,
                 observation={},
                 name="Cell Density Test"):
        description = ("Tests the cell density within a single layer of model")
        self.units = quantities.UnitQuantity(
                    '1000/mm3', 1e3/quantities.mm**3, symbol='1000/mm3')
        required_capabilities = (cap.ProvidesDensityInfo,)

        observation = self.format_data(observation)
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
                units_str = " ".join(quantity_parts[1:])
                assert (units_str == self.units.symbol)
                data["density"][key] = quantities.Quantity(number, self.units)
            except AssertionError:
                raise sciunit.Error("Values not in appropriate format. Required units: ", self.units.symbol)
            except:
                raise sciunit.Error("Values not in appropriate format.")
        return data

    #----------------------------------------------------------------------

    def validate_observation(self, observation):
        try:
            for key, val in observation["density"].items():
                assert type(observation["density"][key]) is quantities.Quantity
        except Exception:
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
        self.score = sciunit.scores.ZScore.compute(observation["density"], prediction["density"])
        self.score.description = "A simple Z-score"

        # create output directory
        self.path_test_output = self.directory_output + 'cell_density/' + self.model_name + '/'
        if not os.path.exists(self.path_test_output):
            os.makedirs(self.path_test_output)

        self.observation = observation
        self.prediction = prediction
        # create relevant output files
        # 1. Error Plot
        err_plot = plots.ErrorPlot(self)
        err_plot.xlabels = ["Layer"]
        err_plot.ylabel = "Cell Density (1000/mm3)"
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
