import sciunit
import os
import json
import copy
import neurom as nm
import numpy as np

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
        self.model_version = model_name

        self.morph_path = morph_path
        self.config_path = config_path

        # Defining output directory
        self.morph_stats_output = os.path.join(base_directory, 'validation_results', 'neuroM_morph_softChecks',
                                               self.model_version, datetime.now().strftime("%Y%m%d-%H%M%S"))

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
        # create output directory
        if not os.path.exists(self.morph_stats_output):
            os.makedirs(self.morph_stats_output)

        try:
            os.system('morph_stats -C {} -o {} {}'.format(self.config_path, self.output_file, self.morph_path))
        except IOError:
            print "Please specify the paths to the morphology directory and configuration file for morph_stats"

        with open(self.output_file, 'r') as fp:
            mod_prediction = json.load(fp)
        for key0, dict0 in mod_prediction.items():  # Dict. with cell's morph_path-features dict. pairs for each cell
            # Correcting cell's ID, given by some NeuroM versions:
            # omitting enclosing directory's name and file's extension
            cell_ID = (key0.split("/")[-1])
            # cell_ID = os.path.splitext(cell_ID)[0]
            del mod_prediction[key0]
            mod_prediction.update({cell_ID: dict0})

            # Regrouping all soma's features-values pairs into a unique 'soma' key inside mod_prediction
            soma_features = dict()
            for key, val in dict0.items():
                if 'soma' in key:
                    soma_features.update({key: val})
                    del dict0[key]
                    dict0.update({"soma": soma_features})

        # Saving NeuroM's morph_stats output in a formatted json-file
        with open(self.output_file, 'w') as fp:
            json.dump(mod_prediction, fp, sort_keys=True, indent=3)
        os.remove(self.output_file)


        return mod_prediction

    def get_morph_feature_info(self):
        return self.morph_feature_info


class NeuroM_MorphStats_AddFeatures(NeuroM_MorphStats):
    """A class to interact with morphology files via the morphometrics-NeuroM's API (morph_stats).
    It is used to add more features to the generated prediction from the parent class
    Averages and std are computed in case more than a morphology file is processed"""

    def __init__(self, model_name='NeuroM_MorphStats', morph_path=None,
                 config_path=None, morph_stats_file=None, base_directory='.'):

        super(NeuroM_MorphStats_AddFeatures, self).__init__(model_name=model_name, morph_path=morph_path,
                                                            config_path=config_path, morph_stats_file=morph_stats_file,
                                                            base_directory=base_directory)
        self.morph_feature_info = self.complete_prediction()
        self.morph_feature_info = self.avg_prediction()
        self.morph_feature_info = self.pre_formatting()

    # ----------------------------------------------------------------------

    def complete_prediction(self):
        """Adding more features by means of other NeuroM's functionalities
        to the generated prediction by the parent class, which uses just morph_stats"""

        mod_prediction = self.morph_feature_info

        mapping = lambda section: section.points
        for cell_ID, dict0 in mod_prediction.items():  # Dict. with cell's morph_path-features dict. pairs for each cell

            # Adding more neurite's features:
            # field diameter, bounding-box -X,Y,Z- extents and -largest,shortest- principal extents
            if os.path.isdir(self.morph_path):
                neuron_path = os.path.join(self.morph_path, cell_ID)
            else:
                neuron_path = self.morph_path
            neuron_model = nm.load_neuron(neuron_path)
            for key1, dict1 in dict0.items():  # Dict. with feature name-value pairs for each cell part:
                                                # soma, apical_dendrite, basal_dendrite or axon
                if any(sub_str in key1 for sub_str in ['axon', 'dendrite']):
                    cell_part = key1
                    filter = lambda neurite: neurite.type == getattr(nm.NeuriteType, cell_part)
                    neurite_points = [p for p in nm.iter_neurites(neuron_model, mapping, filter)]
                    neurite_points = np.concatenate(neurite_points)
                    neurite_cloud = neurite_points[:, 0:3]

                    # Compute the neurite's bounding-box -X,Y,Z- extents
                    neurite_X_extent, neurite_Y_extent, neurite_Z_extent = \
                        np.max(neurite_cloud, axis=0) - np.min(neurite_cloud, axis=0)
                    dict1.update({"neurite_X_extent": neurite_X_extent})
                    dict1.update({"neurite_Y_extent": neurite_Y_extent})
                    dict1.update({"neurite_Z_extent": neurite_Z_extent})

                    # Compute the neurite's -largest, shortest- principal extents
                    principal_extents = sorted(nm.morphmath.principal_direction_extent(neurite_cloud))
                    dict1.update({"neurite_shortest_extent": principal_extents[0]})
                    dict1.update({"neurite_largest_extent": principal_extents[-1]})

                    # Compute the neurite-field diameter
                    # neurite_field_diameter = nm.morphmath.polygon_diameter(neurite_cloud)
                    # dict1.update({"neurite_field_diameter": neurite_field_diameter})

        return mod_prediction

    # ----------------------------------------------------------------------

    def avg_prediction(self):
        """ Collecting raw data from all cells and computing the corresponding average"""

        mod_prediction = self.morph_feature_info

        population_features = copy.deepcopy(mod_prediction.values())[0]
        for cell_part, feature_dict in population_features.items():
            feat_dict_raw = {feat_name: [cell_dict[cell_part][feat_name] for cell_dict in mod_prediction.values()]
                             for feat_name in feature_dict.keys()}
            feature_dict.update({feat_name: [np.mean(feat_dict_raw[feat_name]), np.std(feat_dict_raw[feat_name])]
                                 for feat_name in feature_dict.keys()})

        pop_prediction = dict(pop_mean=population_features)

        return pop_prediction

    # ----------------------------------------------------------------------

    def pre_formatting(self):
        """Formatting the prediction by adding units and additional labels, e.g. 'mean', 'value', etc"""

        mod_prediction = self.morph_feature_info

        dim_um = ['radius', 'radii', 'diameter', 'length', 'distance', 'extent']
        for dict1 in mod_prediction.values():  # Set of cell's part-features dictionary pairs for each cell

            # Adding the right units and converting feature values to strings
            for dict2 in dict1.values():  # Dict. with feature name-value pairs for each cell part:
                                            # soma, apical_dendrite, basal_dendrite or axon
                for key, val in dict2.items():
                    if any(sub_str in key for sub_str in ['radius', 'radii']):
                        del dict2[key]
                        val[0] *= 2
                        key = key.replace("radius", "diameter")
                        key = key.replace("radii", "diameter")

                    if val[1] == 0:  # val[1] is the std, and a zero value is unrealistic
                        val[1] = 1.0  # To avoid division-by-zero error when computing scores
                    if any(sub_str in key for sub_str in dim_um):
                        dict2[key] = dict(mean=str(val[0]) + ' um', std=str(val[1]) + ' um')
                    else:
                        dict2[key] = dict(mean=str(val[0]), std=str(val[1]))

        """
        # Saving NeuroM's morph_stats output in a formatted json-file
        with open(self.output_file, 'w') as fp:
            json.dump(mod_prediction, fp, sort_keys=True, indent=3)
        """

        return mod_prediction
