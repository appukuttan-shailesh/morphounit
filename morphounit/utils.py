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


# ----------------------------------------------------------------------


class NeuroM_MorphStats(sciunit.Model):
    """A class to interact with morphology files via the morphometrics-NeuroM's API (morph_stats)"""

    def __init__(self, model_name='NeuroM_MorphStats', morph_path=None, \
                neuroM_pred_file=None, base_directory='.'):

        sciunit.Model.__init__(self, name=model_name)
        self.description = "A class to interact with morphology files " \
                           "via the morphometrics-NeuroM's API (morph_stats)"
        self.model_version = model_name

        # Setting the morphology file to be processed by means of morph_stats
        self.morph_path = morph_path

        # Defining output dir and files
        self.morph_stats_output = os.path.join(base_directory, 'validation_results', 'neuroM_morph_softChecks',
                                               self.model_version, datetime.now().strftime("%Y%m%d-%H%M%S"))
        self.output_pred_file = os.path.join(self.morph_stats_output, neuroM_pred_file)

    # ----------------------------------------------------------------------

    def set_morph_feature_info(self, morph_stats_config_path=None):
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
            os.system(f"morph_stats -C {morph_stats_config_path} -o {self.output_pred_file} {self.morph_path}")
        except IOError:
            print("Please specify the path to the morphology directory and configuration file for morph_stats")

        with open(self.output_pred_file, 'r') as fp:
            mod_prediction = json.load(fp)

        for key0, dict0 in list(mod_prediction.items()):  # Dict. with cell's morph_path-features dict. pairs for each cell
            # Correcting cell's ID, given by some NeuroM versions:
            # omitting enclosing directory's name
            cell_ID = (key0.split("/")[-1])
            del mod_prediction[key0]
            mod_prediction.update({cell_ID: dict0})

            # Additional formatting for neurom.fst.NEURONFEATURES.keys(), when present.
            # Regrouping all neuron features-values pairs into a unique key ('neuron'),
            # as in NeuroM's nomenclature, e.g. total_soma_radii, mean_trunk_section_lengths
            neuron_feat_name_stat_mode = dict()
            for key, val in list(dict0.items()):
                if not any(sub_str in key for sub_str in ['dendrite', 'axon']):
                    neuron_feat_name_stat_mode.update({key: val})
                    del dict0[key]
            if neuron_feat_name_stat_mode:
                dict0.update({"neuron": neuron_feat_name_stat_mode})

        # Additional formatting to morph_stats output:
        # reversing some changes introduced into original NeuroM ('fst' module) nomenclature,
        # e.g., number in feature names is changed from plural to singular, and sometimes 'radii' to 'radius'
        # The configuration file for morph_stats is taken as the reference, to re-format the output file
        # (instead of taking the observation file as reference, to keep independence between Model and Test classes)
        with open(morph_stats_config_path, 'r') as fp:
            morph_stats_config_dict = json.load(fp)
        # print('morph_stats_config_dict = ', json.dumps(morph_stats_config_dict, sort_keys=True, indent=3))

        neurite_feats_plural = list()
        neuron_feats_plural = list()
        for key0, dict0 in list(morph_stats_config_dict.items()):
            if key0 == 'neurite':
                neurite_feats_plural = [key1 for key1 in dict0.keys() if key1[-1] == 's']
            elif key0 == 'neuron':
                neuron_feats_plural = [key1 for key1 in dict0.keys() if key1[-1] == 's']

        for cell_ID, dict0 in list(mod_prediction.items()):  # Dict. with cell's morph_path-features dict. pairs
                                                            # for each cell
            for cell_part, dict1 in list(dict0.items()):
                for feat_name_stat_mode, value in list(dict1.items()):

                    new_key = ''
                    if 'radii' in feat_name_stat_mode:
                        continue
                    # Replacing "radius" by "radii", as in original NeuroM's nomenclature
                    elif 'radius' in feat_name_stat_mode:
                        new_key = feat_name_stat_mode.replace("radius", "radii")
                    # Recovering the plural, as in original NeuroM's nomenclature
                    elif cell_part == 'neuron':
                        if neuron_feats_plural and any(feat_name_plural[:-1] in feat_name_stat_mode
                                                       for feat_name_plural in neuron_feats_plural):
                            new_key = feat_name_stat_mode + 's'
                    elif neurite_feats_plural and any(feat_name_plural[:-1] in feat_name_stat_mode
                                                      for feat_name_plural in neurite_feats_plural):
                            new_key = feat_name_stat_mode + 's'

                    if new_key:
                        # print('Changing %s -> %s = \n' % (feat_name_stat_mode, new_key))
                        del dict1[feat_name_stat_mode]
                        dict1.update({new_key: value})

        # Saving NeuroM's morph_stats output in a formatted json-file
        # with open(self.output_pred_file, 'w') as fp:
        #    json.dump(mod_prediction, fp, sort_keys=True, indent=3)

        return mod_prediction

    # ----------------------------------------------------------------------

    def complete_morph_feature_info(self, neuroM_extra_config_path=None):
        """Adding more features by means of other NeuroM's functionalities
        to the prediction generated by function 'set_morph_feature_info',
        which uses just NeuroM's API for morph_stats
        Example of features added: field diameter, bounding-box -X,Y,Z- extents
        and -largest,shortest- principal extents"""

        extra_file_exists = os.path.isfile(neuroM_extra_config_path)
        if not extra_file_exists:
            return
        with open(neuroM_extra_config_path, 'r') as fp:
            morph_extra_dict = json.load(fp)

        # Adding more neurite's features, if requested:
        # field diameter, bounding-box -X,Y,Z- extents and -largest,shortest- principal extents
        with open(self.output_pred_file, 'r') as fp:
            mod_prediction = json.load(fp)

        if os.path.isdir(self.morph_path):
            morph_files = nm.io.utils.get_morph_files(self.morph_path)

        mapping = lambda section: section.points
        for neurite_name, extra_feat_list in list(morph_extra_dict.items()): # Dict. with neurite names and
                                                                        # extra features to be computed
            for cell_ID, dict0 in list(mod_prediction.items()):  # Dict. with cell's morph_path-features dict. pairs
                                                            # for each cell

                if os.path.isdir(self.morph_path):
                    morph_file_name = [morph_file for morph_file in morph_files if cell_ID in morph_file]
                    neuron_path = os.path.join(self.morph_path, os.path.basename(morph_file_name[0]))
                else:
                    neuron_path = self.morph_path

                neuron_model = nm.load_neuron(neuron_path)

                for cell_part, dict1 in list(dict0.items()):
                    if cell_part == neurite_name:
                        neurite_filter = lambda neurite: neurite.type == getattr(nm.NeuriteType, cell_part)
                        neurite_points = [neurite_points for neurite_points in
                                          nm.iter_neurites(neuron_model, mapping, neurite_filter)]
                        neurite_points = np.concatenate(neurite_points)
                        neurite_cloud = neurite_points[:, 0:3]

                        for feat_name in extra_feat_list:
                            # Compute the neurite's bounding-box -X,Y,Z- extents
                            if feat_name=='neurite_X_extent':
                                neurite_X_extent = np.max(neurite_cloud[:, 0], axis=0) - \
                                                   np.min(neurite_cloud[:, 0], axis=0)
                                dict1.update({"neurite_X_extent": neurite_X_extent})

                            elif feat_name=='neurite_Y_extent':
                                neurite_Y_extent = np.max(neurite_cloud[:, 1], axis=0) - \
                                                   np.min(neurite_cloud[:, 1], axis=0)
                                dict1.update({"neurite_Y_extent": neurite_Y_extent})

                            elif feat_name=='neurite_Z_extent':
                                neurite_Z_extent = np.max(neurite_cloud[:, 2], axis=0) - \
                                                   np.min(neurite_cloud[:, 2], axis=0)
                                dict1.update({"neurite_Z_extent": neurite_Z_extent})

                            # Compute the neurite's principal extents
                            elif feat_name=='neurite_shortest_extent':
                                # Compute the neurite's shortest principal extents
                                principal_extents = sorted(nm.morphmath.principal_direction_extent(neurite_cloud))
                                dict1.update({"neurite_shortest_extent": principal_extents[0]})

                            elif feat_name=='neurite_largest_extent':
                                # Compute the neurite's largest principal extents
                                principal_extents = sorted(nm.morphmath.principal_direction_extent(neurite_cloud))
                                dict1.update({"neurite_largest_extent": principal_extents[-1]})

                            # Compute the neurite-field diameter
                            elif feat_name=='neurite_field_diameter':
                                neurite_field_diameter = nm.morphmath.polygon_diameter(neurite_cloud)
                                dict1.update({"neurite_field_diameter": neurite_field_diameter})

        # Saving NeuroM's output in a formatted json-file
        # with open(self.output_pred_file, 'w') as fp:
        #     json.dump(mod_prediction, fp, sort_keys=True, indent=3)

        return mod_prediction

    # ----------------------------------------------------------------------

    def pre_formatting(self, mod_data=None):
        """Formatting the prediction by adding (non-functional) units (as strings).
        Python package 'quantities' is not used yet, this is implemented in the Test class"""

        mod_prediction = mod_data

        dim_um = ['radii', 'length', 'distance', 'extent']
        for dict1 in mod_prediction.values():  # Set of cell's part-features dictionary pairs for each cell

            # Adding the right units and converting feature values to strings
            for dict2 in dict1.values():  # Dict. with feature name-value pairs for each cell part:
                                                #  neuron, apical_dendrite, basal_dendrite or axon
                for key, val in list(dict2.items()):
                    if any(sub_str in key for sub_str in dim_um):
                        dict2[key] = dict(value=str(val) + ' um')
                    else:
                        dict2[key] = dict(value=str(val))

        # Saving NeuroM's output in a formatted json-file
        # with open(self.output_pred_file, 'w') as fp:
        #    json.dump(mod_prediction, fp, sort_keys=True, indent=3)

        return mod_prediction


# ----------------------------------------------------------------------


class NeuroM_MorphStats_pop(NeuroM_MorphStats):
    """A class to interact with a population of morphologies via the morphometrics-NeuroM's API (morph_stats)"""
    def __init__(self, model_name='NeuroM_MorphStats_pop', morph_path=None, \
                neuroM_pred_file=None, base_directory='.'):

        super().__init__(model_name=model_name, morph_path=morph_path, \
                        neuroM_pred_file=neuroM_pred_file, \
                        base_directory=base_directory)
        self.description = "A class to interact with a population of morphologies \
                            via the morphometrics-NeuroM's API (morph_stats)"

    # ----------------------------------------------------------------------

    def avg_prediction(self, mod_data=None):
        """ Collecting raw data from all cells and computing the corresponding average"""

        mod_prediction = mod_data

        population_features = copy.deepcopy(list(mod_prediction.values()))[0]
        population_features_raw = dict.fromkeys(population_features, {})
        for cell_part, feature_dict in list(population_features.items()):
            feat_dict_raw = {feat_name: [cell_dict[cell_part][feat_name] for cell_dict in mod_prediction.values()]
                             for feat_name in feature_dict.keys()}
            population_features_raw.update({cell_part: feat_dict_raw})
            feature_dict.update({feat_name: np.mean(feat_dict_raw[feat_name])
                                 for feat_name in feature_dict.keys()})

        pop_avg_prediction = dict(FSI_mean=population_features)
        pop_cells_prediction = dict(FSI_pop=population_features_raw)

        # print 'pop_avg_prediction = ', json.dumps(pop_avg_prediction, sort_keys=True, indent=3), '\n\n'
        # print 'pop_cells_prediction = ', json.dumps(pop_cells_prediction, sort_keys=True, indent=3), '\n'

        # Saving NeuroM's average population output in a formatted json-file
        # with open(self.output_pred_file, 'w') as fp:
        #    json.dump(pop_avg_prediction, fp, sort_keys=True, indent=3)

        return pop_cells_prediction, pop_avg_prediction
