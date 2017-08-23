# Currently meant only for CellDensityTest
# Will be made generic soon
from tabulate import tabulate

#==============================================================================

class TxtTable:
    """
    Displays data in table inside text file
    Note: can be extended in future to provide more flexibility
    """

    def __init__(self, testObj):
        self.testObj = testObj
        self.filename = "score_summary"

    def create(self, mid_keys = []):
        filepath = self.testObj.path_test_output + self.filename + '.txt'
        dataFile = open(filepath, 'w')
        dataFile.write("==============================================================================\n")
        dataFile.write("Test Name: %s\n" % self.testObj.name)
        dataFile.write("Model Name: %s\n" % self.testObj.model_name)
        dataFile.write("Score Type: %s\n" % self.testObj.score.description)
        dataFile.write("------------------------------------------------------------------------------\n")
        header_list = ["Parameter", "Expt. mean", "Expt. std", "Model value", "Score"]
        row_list = []
        for key in self.testObj.observation.keys():
            if mid_keys: # this is currently used only by LayerHeightTest
                temp_obs = self.testObj.observation
                temp_prd = self.testObj.prediction
                for i in range(len(mid_keys)):
                    temp_obs = temp_obs[key][mid_keys[i]]
                    temp_prd = temp_prd[key][mid_keys[i]]
                o_mean = temp_obs["mean"]
                o_std = temp_obs["std"]
                p_value = temp_prd["value"]
                score = self.testObj.score_dict[key]
            elif "mean" in self.testObj.observation[key].keys():
                o_mean = self.testObj.observation[key]["mean"]
                o_std = self.testObj.observation[key]["std"]
                p_value = self.testObj.prediction[key]["value"]
                score = self.testObj.score
            elif "min" in self.testObj.observation[key].keys():
                o_mean = self.testObj.observation[key]["min"]
                o_std = self.testObj.observation[key]["max"]
                p_value = self.testObj.prediction[key]["value"]
                score = self.testObj.score
            else:
                print("Error in terminal keys!")
                raise
            row_list.append([key, o_mean, o_std, p_value, score])
        dataFile.write(tabulate(row_list, headers=header_list, tablefmt='orgtbl'))
        dataFile.write("\n------------------------------------------------------------------------------\n")
        dataFile.write("Final Score: %s\n" % self.testObj.score)
        dataFile.write("==============================================================================\n")
        dataFile.close()
        return filepath
