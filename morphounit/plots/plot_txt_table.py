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

    def create(self):
        filepath = self.testObj.path_test_output + self.filename + '.txt'
        dataFile = open(filepath, 'w')
        dataFile.write("==============================================================================\n")
        dataFile.write("Test Name: %s\n" % self.testObj.name)
        dataFile.write("Model Name: %s\n" % self.testObj.model_name)
        dataFile.write("------------------------------------------------------------------------------\n")
        header_list = ["Parameter", "Expt. mean", "Expt. std", "Model value", "Z-score"]
        row_list = []
        for key in self.testObj.observation.keys():
            o_mean = self.testObj.observation[key]["mean"]
            print "o_mean = ", o_mean
            o_std = self.testObj.observation[key]["std"]
            p_value = self.testObj.prediction[key]["value"]
            row_list.append([key, o_mean, o_std, p_value, self.testObj.score])
        dataFile.write(tabulate(row_list, headers=header_list, tablefmt='orgtbl'))
        dataFile.write("\n------------------------------------------------------------------------------\n")
        dataFile.write("Final Score: %s\n" % self.testObj.score)
        dataFile.write("==============================================================================\n")
        dataFile.close()
        return filepath
