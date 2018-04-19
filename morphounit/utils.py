import sciunit
import os
import json


class neuroM_loader(sciunit.Model):
    def __init__(self, name="neuroM_loader", description="", model_path=None):
        sciunit.Model.__init__(self, name=name)
        self.description = description
        if model_path == None:
            raise ValueError("Please specify the path to the morphology file!")
        if not os.path.isfile(model_path):
            raise ValueError("Specified path to the morphology file is invalid!")
        self.morph_path = model_path
        #self.model = neurom.load_neuron(self.morph_path)


class NeuroM_MorphStats(sciunit.Model):
    """A class to interact with morphology files via the morphometrics-NeuroM's API (morph_stats)"""

    # model_instance_uuid = "421e6a79-80b1-4d2f-8c43-b2f37bfc1cfc"  # environment="prod"
    model_instance_uuid = "cba18d6d-a60c-491d-bc8f-09114d127aac"  # environment="dev"

    def __init__(self, name='NeuroM_MorphStats', model_path=None, config_path=None, pred_path=None, stats_file=None):

        sciunit.Model.__init__(self, name=name)
        self.description = "A class to interact with morphology files via the morphometrics-NeuroM's API (morph_stats)"
        self.version = name
        self.morph_path = model_path
        self.config_path = config_path
        self.pred_path = pred_path
        self.output_path = os.path.join(pred_path, stats_file)
        self.morph_feature_info = self.set_morph_feature_info()

    def set_morph_feature_info(self):
        """
        Must return a dictionary of the form:
        {"cell1_ID": { 'cell_part_1': {'morph_feature_name_11': {'value': 'X11 units_str'},
                                       'morph_feature_name_12': {'value': 'X12 units_str'},
                                        ... },
                       'cell_part_2': {'morph_feature_name_21': {'value': 'X21 units_str'},
                                       'morph_feature_name_22': {'value': 'X22 units_str'},
                                        ... },
                       ... }
         "cell2_ID": { 'cell_part_1': {'morph_feature_name_11': {'value': 'Y11 units_str'},
                                       'morph_feature_name_12': {'value': 'Y12 units_str'},
                                        ... },
                       'cell_part_2': {'morph_feature_name_21': {'value': 'Y21 units_str'},
                                       'morph_feature_name_22': {'value': 'Y22 units_str'},
                                        ... },
                       ... }
        ... }
        """

        try:
            os.system('morph_stats -C {} -o {} {}'.format(self.config_path, self.output_path, self.morph_path))
        except IOError:
            print "Please specify the paths to the morphology directory and configuration file for morph_stats"

        # Saving NeuroM's morph_stats output in a formatted json-file
        fp = open(self.output_path, 'r+')
        mod_prediction = json.load(fp)
        fp.seek(0)
        json.dump(mod_prediction, fp, sort_keys=True, indent=4)
        fp.close()

        return mod_prediction

    def get_morph_feature_info(self):
        return self.morph_feature_info

