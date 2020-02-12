import sciunit
import sciunit.scores as sci_scores
import morphounit.scores as mph_scores
# import morphounit.capabilities as mph_cap
import morphounit.plots as mph_plots

import os
import copy
import json

import neurom as nm

import numpy as np
import quantities


class NeuroM_MorphStats_Test(sciunit.Test):
    """Tests a set of cell's morphological features"""
    score_type = mph_scores.CombineZScores

    def __init__(self, observation=None, name="NeuroM_MorphStats_Test", base_directory=None):

        self.description = "Tests a set of cell's morpho-features in a digitally reconstructed neuron"
        # require_capabilities = (mph_cap.ProvidesMorphFeatureInfo,)

        if not base_directory:
            base_directory = "."
        self.path_test_output = base_directory
        # create output directory
        if not os.path.exists(self.path_test_output):
            os.makedirs(self.path_test_output)

        # Checks raw observation data compliance with NeuroM's nomenclature
        self.check_observation(observation)
        self.raw_observation = observation

        json.dumps(observation, sort_keys=True, indent=3)

        self.figures = []
        observation = self.format_data(observation)
        sciunit.Test.__init__(self, observation, name)

    # ----------------------------------------------------------------------

    def check_observation(self, observation):
        """Checks raw observation file compliance with NeuroM's ('fst' module) nomenclature"""

        # Cell parts available
        neuron_parts_avail = [neurite_type.name for neurite_type in nm.NEURITE_TYPES[1:]]
        neuron_parts_avail.append('neuron')

        # Cell features available
        cell_feats_avail = nm.fst.NEURONFEATURES.keys()

        # Neurite features available
        neurite_feats_avail = list(nm.fst.NEURITEFEATURES.keys())
        neurite_feats_extra = ['neurite_field_diameter', 'neurite_largest_extent', 'neurite_shortest_extent',
                               'neurite_X_extent', 'neurite_Y_extent', 'neurite_Z_extent']
        neurite_feats_avail.extend(neurite_feats_extra)

        # Statistical modes available
        stat_modes = ['min', 'max', 'median', 'mean', 'total', 'std']

        # morph_stats's nomenclature constraints to specify observation files
        """
        self.neuroM_morph_stats_doc(neuron_parts_avail,
                                    cell_feats_avail, neurite_feats_avail, neurite_feats_extra,
                                    stat_modes)
        """

        # print "Checking observation file compliance with NeuroM's ('fst' module) nomenclature..."
        for dict1 in observation.values():  # Dict. with cell's part-features dictionary pairs for each cell
            for key2, dict2 in list(dict1.items()):  # Dict. with feature name-value pairs for each cell part:
                                                #  neuron, apical_dendrite, basal_dendrite or axon
                assert (key2 in neuron_parts_avail), \
                    f"{key2} is not permitted for neuron parts. Please, use one in the following \
                    list:\n {neuron_parts_avail}"

                for key3 in dict2.keys():
                    feat_name, stat_mode = key3.split('_', 1)[1], key3.split('_', 1)[0]
                    if key2 == 'neuron':
                        # Checking the NeuroM features for the cell
                        assert (feat_name in cell_feats_avail), \
                            f"{feat_name} is not permitted for cells. Please, use one in the following \
                            list:\n {sorted(cell_feats_avail)}"
                        # Checking the statistical mode for the cell features
                        assert (stat_mode in stat_modes), \
                            f"{stat_mode} is not permitted for statistical modes. Please, use one in \
                            the following list:\n {stat_modes}"
                    elif feat_name in nm.fst.NEURITEFEATURES.keys():
                        assert (stat_mode in stat_modes), \
                            f"{stat_mode} is not permitted for statistical modes. Please, use one in \
                            the following \list:\n {stat_modes}"
                    else:
                        # Checking the extra-NeuroM features for Neurites, if any
                        assert (key3 in neurite_feats_extra), \
                            f"{key3} is not permitted for neurites. Please, use one in the following \
                            list:\n {sorted(neurite_feats_avail)}"

    # ----------------------------------------------------------------------

    def neuroM_morph_stats_doc(self, neuron_parts_avail, cell_feats_avail,
                               neurite_feats_avail, neurite_feats_extra, stat_modes):
        """Prints NeuroM ('fst' module) nomenclature constraints to be followed
        by the user when specifying observation files"""

        print ('Cell parts available:\n', sorted(neuron_parts_avail), '\n')
        print ('Cell features available:\n', sorted(cell_feats_avail), '\n')
        print ('Neurite features available:\n', sorted(neurite_feats_avail), '\n')
        print ('A summary statistics must be indicated for each feature, with the ' \
              'exception of those contained in the set ', neurite_feats_extra, \
            '. Statistics modes available: ', stat_modes, '\n')
        # How to specify feature_name = mode + feature
        print ("To that end, a prefix formed with the stats. mode intended, followed by '_', " \
              "should be added to the feature name. For instance: 'total_number_of_neurites' \n")
        print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \n\n")

    # ----------------------------------------------------------------------

    def format_data(self, data):

        """
        This accepts data input in the form:
        ***** (observation) *****
        {"cell_kind": { "cell_part_1": {'morph_feature_name_11': {'mean value': 'X11_mean units_str', 'std': 'X11_std units_str'},
                                        'morph_feature_name_12': {'mean value': 'X12_mean units_str', 'std': 'X12_std units_str'},
                                        ... },
                        "cell_part_2": {'morph_feature_name_21': {'mean value': 'X21_mean units_str', 'std': 'X21_std units_str'},
                                        'morph_feature_name_22': {'mean value': 'X22_mean units_str', 'std': 'X22_std units_str'},
                                        ... },
                        ... }
        }
        ***** (prediction) *****
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

        It splits the values of mean, std and value to numeric quantities
        and their units (via quantities package)
        """
        dim_non = ['order', 'number', 'asymmetry', 'rate']
        dim_um = ['radii', 'length', 'distance', 'extent']
        dim_umSq = ['area']
        dim_umCb = ['volume']
        dim_deg = ['angle']
        for dict1 in data.values():  # Dict. with cell's part-features dictionary pairs for each cell
            for dict2 in dict1.values():  # Dict. with feature name-value pairs for each cell part:
                                            # neuron, apical_dendrite, basal_dendrite or axon
                for dict3 in dict2.values():  # Dict. with 'value', 'mean' and 'std' values
                    for key, val in dict3.items():
                        quantity_parts = val.split()
                        number, units_str = float(quantity_parts[0]), " ".join(quantity_parts[1:])
                        try:
                            if any(sub_str in key for sub_str in dim_um):
                                assert (units_str == quantities.um | units_str == quantities.mm), \
                                    sciunit.Error("Values not in appropriate format. Required units: mm or um")
                            elif any(sub_str in key for sub_str in dim_non):
                                assert (units_str == quantities.dimensionless), \
                                    sciunit.Error("Values not in appropriate format. Required units: ",
                                                  quantities.dimensionless)
                        finally:
                            dict3[key] = quantities.Quantity(number, units_str)

        return data

    # ----------------------------------------------------------------------

    def validate_observation(self, observation):

        # Checking format of the observation data
        for dict1 in observation.values():  # Dict. with cell's part-features dictionary pairs for each cell
            for dict2 in dict1.values():  # Dict. with feature name-value pairs for each cell part:
                                            # neuron, apical_dendrite, basal_dendrite or axon
                for dict3 in dict2.values():  # Dict. with 'value' or 'mean' and 'std' values
                    for val in dict3.values():
                        assert type(val) is quantities.Quantity, \
                            sciunit.Error(("Observation must be of the form "
                                           "{'mean': 'XX units_str','std': 'YY units_str'}"))

    # ----------------------------------------------------------------------

    def set_morph_stats_config_file(self):
        """ Creates two configuration files, following the structure of a
        raw observation JSON file (previously to SciUnit formatting):
        - One for morph_stats features to be computed, and
        a second one for non-morph_stats features found in the observation file."""

        observation = self.raw_observation

        neurite_type_list = list()
        feat_name_stat_mode_neurite_dict = dict()
        feat_name_stat_mode_cell_dict = dict()
        neurite_feats_extra_dict = dict()  # For non-morph_stats features
        for dict1 in observation.values():  # Dict. with cell's part-features dictionary pairs for each cell
            for key2, dict2 in dict1.items():  # Dict. with feature name-value pairs for each cell part:
                                                #  neuron, apical_dendrite, basal_dendrite or axon
                if key2 == 'neuron':
                    feat_name_stat_mode_cell_dict = dict()
                else:
                    neurite_type_list.append(key2.upper())
                    neurite_feats_extra_dict.update({key2: []})
                for key3 in dict2.keys():
                    feat_name, stat_mode = key3.split('_', 1)[1], key3.split('_', 1)[0]

                    if key2 == 'neuron':
                        if feat_name in feat_name_stat_mode_cell_dict and \
                                stat_mode not in feat_name_stat_mode_cell_dict[feat_name]:
                            feat_name_stat_mode_cell_dict[feat_name].append(stat_mode)
                        else:
                            feat_name_stat_mode_cell_dict.update({feat_name: [stat_mode]})

                    elif feat_name in nm.fst.NEURITEFEATURES.keys():
                        if feat_name in feat_name_stat_mode_neurite_dict and \
                                stat_mode not in feat_name_stat_mode_neurite_dict[feat_name]:
                            feat_name_stat_mode_neurite_dict[feat_name].append(stat_mode)
                        else:
                            feat_name_stat_mode_neurite_dict.update({feat_name: [stat_mode]})
                    else:
                        neurite_feats_extra_dict[key2].append(key3)

        # Morphometrics of morph_stats features to be computed
        morph_stats_config_dict = dict()
        morph_stats_config_dict.update({'neurite_type': neurite_type_list,
                                        'neurite': feat_name_stat_mode_neurite_dict,
                                        'neuron': feat_name_stat_mode_cell_dict})
        # print('Configuration file for morph_stats was completed. \n', \
        #  json.dumps(morph_stats_config_dict, sort_keys=True, indent=3))

        obs_dir = self.path_test_output
        # obs_dir = os.path.dirname(observation_path)
        # obs_file_name = os.path.basename(observation_path)

        # Saving NeuroM's morph_stats configuration file in JSON format
        # morph_stats_conf_file = os.path.splitext(obs_file_name)[0] + '_config.json'
        morph_stats_config_path = os.path.join(obs_dir, 'morph_stats_config.json')
        with open(morph_stats_config_path, 'w') as fp:
            json.dump(morph_stats_config_dict, fp, sort_keys=True, indent=3)

        # Morphometrics of non-morph_stats features to be computed
        for key, value in neurite_feats_extra_dict.items():
            if not value:
                del neurite_feats_extra_dict[key]

        # neuroM_extra_config_file = os.path.splitext(obs_file_name)[0] + '_extra.json'
        neuroM_extra_config_path = os.path.join(obs_dir, 'neuroM_extra_config.json')
        # Remove existing file, if any
        extra_file_exists = os.path.isfile(neuroM_extra_config_path)
        if extra_file_exists:
            os.remove(neuroM_extra_config_path)
        if neurite_feats_extra_dict:
            # print('The following morphometrics will be extracted separately and added to the model prediction: \n', \
            # json.dumps(neurite_feats_extra_dict, sort_keys=True, indent=3))
            # Saving NeuroM's configuration extra-file in JSON format
            with open(neuroM_extra_config_path, 'w') as fp:
                json.dump(neurite_feats_extra_dict, fp, sort_keys=True, indent=3)

        return morph_stats_config_path, neuroM_extra_config_path

    # ----------------------------------------------------------------------

    def raw_model_prediction(self, model):
        """ Creates a model prediction file containing the morphometrics \
        specified in configuration files for NeuroM """

        # Creates a configuration file for morph_stats, following the structure of a raw observation data
        morph_stats_config_path, neuroM_extra_config_path = self.set_morph_stats_config_file()

        # Creating the prediction file with morph_stats
        self.morp_path = model.morph_path

        mod_prediction_temp = model.set_morph_feature_info(morph_stats_config_path=morph_stats_config_path)
        os.remove(morph_stats_config_path)

        # Deleting some neurite's morphometrics added by morph_stats, but not present in the observation file
        mod_prediction = copy.deepcopy(mod_prediction_temp)
        cell_t = list(self.raw_observation.keys())[0]  # Cell type
        for cell_ID, cell_dict in list(mod_prediction_temp.items()):
            for cell_part, cell_part_dict in list(cell_dict.items()):
                for feat_name_stat_mode in cell_part_dict:
                    if cell_part != 'neuron' and feat_name_stat_mode not in self.raw_observation[cell_t][cell_part]:
                        del mod_prediction[cell_ID][cell_part][feat_name_stat_mode]

        with open(model.output_pred_file, 'w') as fp:
            json.dump(mod_prediction, fp, sort_keys=True, indent=3)

        mod_prediction_all = model.complete_morph_feature_info(neuroM_extra_config_path=neuroM_extra_config_path)
        os.remove(neuroM_extra_config_path)

        os.remove(model.output_pred_file)

        return mod_prediction_all

    # ----------------------------------------------------------------------

    def generate_prediction(self, model, verbose=False):
        """Implementation of sciunit.Test.generate_prediction"""

        # Creates a model prediction file following some NeuroM configuration
        # files for NeuroM, but additional formatting is needed
        mod_prediction_all = self.raw_model_prediction(model)

        mod_prediction = model.pre_formatting(mod_data=mod_prediction_all)
        self.prediction_txt = copy.deepcopy(mod_prediction)

        prediction = self.format_data(mod_prediction)
        return prediction

    # ----------------------------------------------------------------------

    def compute_score(self, observation, prediction, verbose=True):
        """Implementation of sciunit.Test.score_prediction"""

        self.observation = observation
        self.prediction = prediction

        # Computing the scores
        cell_t = list(observation.keys())[0]  # Cell type

        score_cell_dict = dict.fromkeys([key0 for key0 in prediction.keys()], [])
        obs_features = copy.deepcopy(list(observation.values()))[0]

        score_feat_dict = dict()
        for key0 in prediction:  # cell_ID keys

            score_feat_dict.update({key0: obs_features})
            scores_cell_list = list()
            for key1 in score_feat_dict[key0]:  # cell's part: neuron, axon, apical_dendrite or basal_dendrite
                for key2 in score_feat_dict[key0][key1]:  # features names

                    score_feat_value = sci_scores.ZScore.compute(observation[cell_t][key1][key2],
                                                                 prediction[key0][key1][key2]).score
                    scores_cell_list.extend([score_feat_value])

                    score_feat_dict[key0][key1][key2] = {"score": score_feat_value}

            Mean_Zscore_dict = {"A mean |Z-score|": mph_scores.CombineZScores.compute(scores_cell_list).score}
            score_feat_dict[key0].update(Mean_Zscore_dict)
            score_cell_dict[key0] = Mean_Zscore_dict

        self.score_cell_dict = score_cell_dict
        self.score_feat_dict = score_feat_dict

        # Taking the average of the cell's scores as the overall score for the Test
        mean_score = np.mean([dict1["A mean |Z-score|"] for dict1 in score_cell_dict.values()])
        self.score = mph_scores.CombineZScores(mean_score)
        self.score.description = "A mean |Z-score|"

        # ---------------------- Saving relevant results ----------------------
        # Saving json file with model predictions
        json_pred_file = mph_plots.jsonFile_MorphStats(testObj=self, dictData=self.prediction_txt,
                                                       prefix_name="prediction_summary_")
        json_pred_files = json_pred_file.create()
        self.figures.extend(json_pred_files)

        # Saving json file with scores
        json_scores_file = mph_plots.jsonFile_MorphStats(testObj=self, dictData=self.score_feat_dict,
                                                         prefix_name="scores_summary_")
        json_scores_files = json_scores_file.create()
        self.figures.extend(json_scores_files)

        # Saving table with results
        txt_table = mph_plots.TxtTable_MorphStats(testObj=self)
        table_files = txt_table.create()
        self.figures.extend(table_files)

        # Saving figure with scores bar-plot
        barplot_figure = mph_plots.ScoresBars_MorphStats(testObj=self)
        barplot_files = barplot_figure.create()
        self.figures.extend(barplot_files)

        return self.score

    def bind_score(self, score, model, observation, prediction):
        score.related_data["figures"] = self.figures
        return score
