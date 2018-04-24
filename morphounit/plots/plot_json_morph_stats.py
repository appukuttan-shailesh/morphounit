import json
import os


class jsonFile_MorphStats:
    """
    Displays data as a dictionary inside a json file
    """

    def __init__(self, testObj):

        self.testObj = testObj
        self.prefix_filename_cell = "score_summary_"
        self.filepath_list = list()

    def score_jsonFile(self, filepath=None, cell_ID=None, score_feat_dict=None):

        with open(filepath, 'w') as dataFile:
            json.dump(score_feat_dict, dataFile, sort_keys=True, indent=4)

        self.filepath_list.append(filepath)
        return self.filepath_list

    def create(self):

        for key_0 in self.testObj.prediction:  # cell ID keys

            json_name = key_0
            filepath_summary_cell = \
                os.path.join(self.testObj.path_test_output, self.prefix_filename_cell + json_name + '.json')
            score_feat_dict = self.testObj.score_feat_dict

            self.score_jsonFile(filepath=filepath_summary_cell, cell_ID=json_name, score_feat_dict=score_feat_dict)

        return self.filepath_list
