## Adapted from
## https://github.com/appukuttan-shailesh/basalunit.git

from tabulate import tabulate

# ==============================================================================


class TxtTable_MorphStats:
    """
    Displays data in table inside text file
    """

    def __init__(self, testObj):
        self.testObj = testObj
        self.filename = "score_summary"

    def create(self):

        filepath = self.testObj.path_test_output + "/" + self.filename + '.txt'
        dataFile = open(filepath, 'w')

        dataFile.write("============================================================================================\n")
        dataFile.write("Test Name: %s\n\n\n" % self.testObj.name)
        header_list = ["Morphological feature", "Expt. mean", "Expt. std", "Model value", "Score"]

        cell_t = self.testObj.observation.keys()[0]  # Cell type
        for key_0 in self.testObj.prediction:  # cell ID keys

            dataFile.write("Model Name: %s\n" % key_0)
            row_list = []

            for key_1 in self.testObj.prediction[key_0]:  # cell's part keys: soma, axon, apical_dendrite or basal_dendrite
                for key_2 in self.testObj.prediction[key_0][key_1]:  # features name keys

                    o_mean = self.testObj.observation[cell_t][key_1][key_2]["mean"]
                    o_std = self.testObj.observation[cell_t][key_1][key_2]["std"]
                    p_value = self.testObj.prediction[key_0][key_1][key_2]["value"]
                    score = self.testObj.score_feat_dict[key_0][key_1][key_2]["score"]
                    feat_name = "{}.{}".format(key_1, key_2)
                    row_list.append([feat_name, o_mean, o_std, p_value, score])

            dataFile.write(tabulate(row_list, headers=header_list, tablefmt='orgtbl'))
            dataFile.write("\n-----------------------------------------------------------------------------------------"
                           "------------\n\n")

        dataFile.write("Final Score: %s\n" % self.testObj.score)
        dataFile.write("============================================================================================\n")
        dataFile.close()

        return filepath
