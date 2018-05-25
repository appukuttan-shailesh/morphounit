import sciunit
import os
import json

from datetime import datetime


class neuroM_loader(sciunit.Model):
    def __init__(self, name="neuroM_loader", description="", model_path=None):
        sciunit.Model.__init__(self, name=name)
        self.description = description
        if model_path == None:
            raise ValueError("Please specify the path to the morphology file!")
        if not os.path.isfile(model_path):
            raise ValueError("Specified path to the morphology file is invalid!")
        self.morph_path = model_path
        # self.model = neurom.load_neuron(self.morph_path)


class NeuroM_MorphStats(sciunit.Model):
    """A class to interact with morphology files via the morphometrics-NeuroM's API (morph_stats)"""

    def __init__(self, model_name='NeuroM_MorphStats', morph_path=None,
                 config_path=None, morph_stats_file=None, base_directory='.'):

        sciunit.Model.__init__(self, name=model_name)
        self.description = "A class to interact with morphology files " \
                           "via the morphometrics-NeuroM's API (morph_stats)"
        self.version = model_name

        self.morph_path = morph_path
        self.config_path = config_path

        # Defining output directory
        self.morph_stats_output = os.path.join(base_directory, 'validation_results', 'neuroM_morph_softChecks',
                                               self.version, datetime.now().strftime("%Y%m%d-%H%M%S"))

        self.output_file = os.path.join(self.morph_stats_output, morph_stats_file)

        self.morph_feature_info = self.set_morph_feature_info()

    def set_morph_feature_info(self):
        """
        Must return a dictionary of the form:
        {"cell1_ID": { 'cell_part_1': {'morph_feature_name_11': X11},
                                       'morph_feature_name_12': X12},
                                        ... },
                       'cell_part_2': {'morph_feature_name_21': X21},
                                       'morph_feature_name_22': X22},
                                        ... },
                       ... }
         "cell2_ID": { 'cell_part_1': {'morph_feature_name_11': Y11},
                                       'morph_feature_name_12': Y12},
                                        ... },
                       'cell_part_2': {'morph_feature_name_21': Y21},
                                       'morph_feature_name_22': Y22},
                                        ... },
                       ... }
        ... }
        """

        try:
            os.system('morph_stats -C {} -o {} {}'.format(self.config_path, self.output_file, self.morph_path))
        except IOError:
            print "Please specify the paths to the morphology directory and configuration file for morph_stats"

        # create output directory
        if not os.path.exists(self.morph_stats_output):
            os.makedirs(self.morph_stats_output)

        # Correcting cell's ID, given by some neuroM versions:
        # omitting enclosing directory's name  and file's extension
        with open(self.output_file, 'r') as fp:
            mod_prediction = json.load(fp)
        os.remove(self.output_file)
        """
        # Saving NeuroM's morph_stats output in a formatted json-file
        with open(self.output_file, 'w') as fp:
            json.dump(mod_prediction, fp, sort_keys=True, indent=4)
        """
        for key0, dict0 in mod_prediction.items():  # Dict. with cell's morph_path-features dict. pairs for each cell
            cell_ID = (key0.split("/")[-1]).split(".")[0]
            del mod_prediction[key0]
            mod_prediction.update({cell_ID: dict0})

        return mod_prediction

    def get_morph_feature_info(self):
        return self.morph_feature_info


class NeuroM_MorphStats_pop(sciunit.Model):
    """A class to interact with morphology populations via the morphometrics-NeuroM's API"""

    def __init__(self, model_name='NeuroM_MorphStats_pop', morph_path=None, base_directory='.'):

        sciunit.Model.__init__(self, name=model_name)
        self.description = "A class to interact with morphology populations " \
                           "via the morphometrics-NeuroM's API"
        self.version = model_name
        self.morph_path = morph_path

        # Defining output directory
        self.morph_stats_output = os.path.join(base_directory, 'validation_results', 'neuroM_morph_softChecks',
                                               self.version, datetime.now().strftime("%Y%m%d-%H%M%S"))

        self.morph_feature_info = self.set_morph_feature_info()

    def set_morph_feature_info(self):
        """
        Must return a dictionary structure of the form:
        {"FSI_pop": { 'cell_part_1': {'morph_feature_name_11': {}},
                                       'morph_feature_name_12': {}},
                                        ... },
                       'cell_part_2': {'morph_feature_name_21': {}},
                                       'morph_feature_name_22': {}},
                                        ... },
                       ... }
        }
        """
        assert(os.path.isdir(self.morph_path)), "Please specify the path to a morphology directory"

        # create output directory
        if not os.path.exists(self.morph_stats_output):
            os.makedirs(self.morph_stats_output)

        cell_parts = ['soma', 'axon', 'basal_dendrite']
        neurite_features = ['neurite_lengths', 'number_of_neurites', 'section_branch_orders']

        soma_features = ['soma_radii']
        dict_features = dict.fromkeys(cell_parts, dict())
        for key, val in dict_features.items():
            if key == 'soma':
                dict_features.update({key: {morph_feature: list() for morph_feature in soma_features}})
            else:
                dict_features.update({key: {morph_feature: list() for morph_feature in neurite_features}})

        mod_prediction = {"FSI_pop": dict_features}

        return mod_prediction

    def get_morph_feature_info(self):
        return self.morph_feature_info
