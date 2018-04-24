## Adapted from
## https://github.com/appukuttan-shailesh/basalunit.git

from tabulate import tabulate
import quantities
import os


class TxtTable_MorphStats:
    """
    Displays data in table inside text file
    """

    def __init__(self, testObj):

        self.testObj = testObj
        self.prefix_filename_cell = "score_summary_"
        self.filepath_list = list()

    def quant_to_str(self, value_quant):

        if value_quant.units == quantities.dimensionless:
            value_str = str(value_quant.item())
        else:
            value_str = str(value_quant)

        return value_str

    def score_TxtTable(self, filepath=None, cell_ID=None, score_label=None, row_list=[]):

        dataFile = open(filepath, 'w')

        dataFile.write("============================================================================================\n")
        dataFile.write("Test Name: %s\n" % self.testObj.name)
        dataFile.write("Model Name: %s\n\n" % cell_ID)

        header_list = ["Morphological feature", "Expt. mean", "Expt. std", "Model value", "Score"]
        dataFile.write(tabulate(row_list, headers=header_list, tablefmt='orgtbl', stralign='right'))
        dataFile.write("\n-----------------------------------------------------------------------------------------"
                       "------------\n\n")

        dataFile.write("Final Score: %s (%s)\n" % (self.testObj.score_cell_dict[cell_ID][score_label], score_label))
        dataFile.write("============================================================================================\n")

        dataFile.close()

        self.filepath_list.append(filepath)
        return self.filepath_list

    def create(self):

        score_label = "A mean |Z-score|"

        cell_t = self.testObj.observation.keys()[0]  # Cell type
        for key_0 in self.testObj.prediction:  # cell ID keys

            tab_title = key_0
            filepath_summary_cell = \
                os.path.join(self.testObj.path_test_output, self.prefix_filename_cell + tab_title + '.txt')

            row_list = []

            for key_1 in self.testObj.prediction[key_0]:  # cell's part keys: soma, axon,
                                                        # apical_dendrite or basal_dendrite
                for key_2 in self.testObj.prediction[key_0][key_1]:  # features name keys

                    o_mean = self.quant_to_str(self.testObj.observation[cell_t][key_1][key_2]["mean"])
                    o_std = self.quant_to_str(self.testObj.observation[cell_t][key_1][key_2]["std"])
                    p_value = self.quant_to_str(self.testObj.prediction[key_0][key_1][key_2]["value"])
                    score = self.testObj.score_feat_dict[key_0][key_1][key_2]["score"]

                    feat_name = "{}.{}".format(key_1, key_2)
                    row_list.append([feat_name, o_mean, o_std, p_value, score])

            self.score_TxtTable(filepath=filepath_summary_cell, cell_ID=tab_title,
                                score_label=score_label, row_list=row_list)

        return self.filepath_list
