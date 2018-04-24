import json
import os


class jsonFile_MorphStats:
    """
    Displays data as a dictionary inside a json file
    """

    def __init__(self, testObj, dictData, prefix_name):

        self.testObj = testObj
        self.dictData = dictData
        self.prefix_filename = prefix_name
        self.filepath_list = list()

    def score_jsonFile(self, filepath=None, data_dict=None):

        with open(filepath, 'w') as dataFile:
            json.dump(data_dict, dataFile, sort_keys=True, indent=4)

        self.filepath_list.append(filepath)
        return self.filepath_list

    def create(self):

        for key_0 in self.dictData:  # cell ID keys

            json_name = key_0
            filepath_summary_cell = \
                os.path.join(self.testObj.path_test_output, self.prefix_filename + json_name + '.json')

            self.score_jsonFile(filepath=filepath_summary_cell, data_dict=self.dictData)

        return self.filepath_list
