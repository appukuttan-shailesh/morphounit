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

from .test_NeuroM_MorphStats import NeuroM_MorphStats_Test

class NeuroM_MorphStats_pop_Test(NeuroM_MorphStats_Test):
    """Tests a set of cell's morphological features in a neuronal population"""
    score_type = mph_scores.CombineZScores

    def __init__(self, observation=None, name="NeuroM_MorphStats_pop_Test", base_directory=None):

        super().__init__(observation=observation, name=name, base_directory=base_directory)
        self.description = "Tests a set of cell's morpho-features in a population of digitally reconstructed neurons"
        # require_capabilities = (mph_cap.ProvidesMorphFeatureInfo,)

    # ----------------------------------------------------------------------

    def generate_prediction(self, model, verbose=False):
        """Implementation of sciunit.Test.generate_prediction"""

        # Creates a model prediction file following some NeuroM configuration
        # files for NeuroM, but additional formatting is needed
        mod_prediction_all = super().raw_model_prediction(model=model)

        # Collecting raw data from all cells and computing the
        # corresponding the mean morphometrics describing the whole population
        pop_cells_prediction, pop_avg_prediction = model.avg_prediction(mod_data=mod_prediction_all)

        mod_prediction = model.pre_formatting(mod_data=pop_avg_prediction)
        self.prediction_pop_dict = copy.deepcopy(mod_prediction)
        prediction = self.format_data(mod_prediction)

        self.prediction_cells_dict = copy.deepcopy(pop_cells_prediction)

        return prediction

    # ----------------------------------------------------------------------

    def compute_score(self, observation, prediction, verbose=True):
        """Implementation of sciunit.Test.score_prediction"""

        self.observation = observation
        self.prediction = prediction

        # Computing the scores
        cell_t = list(observation.keys())[0]  # Cell type

        score_cell_dict = dict.fromkeys([key0 for key0 in prediction.keys()], [])
        obs_features = copy.deepcopy(list(observation.values()))[0]  # only features registered in observation data are tested
        score_feat_dict = dict()
        for key0 in prediction:  # cell_ID keys

            score_feat_dict.update({key0: obs_features})
            scores_cell_list = list()
            for key1 in score_feat_dict[key0]:  # cell's part: soma, axon, apical_dendrite or basal_dendrite
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
        # create output directory
        # Currently done inside the model Class
        """
        if not os.path.exists(self.path_test_output):
            os.makedirs(self.path_test_output)
        """
        # Saving json file with all cells predictions
        json_pred_file = mph_plots.jsonFile_MorphStats(testObj=self, dictData=self.prediction_cells_dict,
                                                       prefix_name="prediction_summary_")
        json_pred_files = json_pred_file.create()
        self.figures.extend(json_pred_files)

        # Saving json file with population's prediction
        json_pred_file = mph_plots.jsonFile_MorphStats(testObj=self, dictData=self.prediction_pop_dict,
                                                       prefix_name="prediction_summary_")
        json_pred_files = json_pred_file.create()
        self.figures.extend(json_pred_files)

        # Saving json file with population's scores
        json_scores_file = mph_plots.jsonFile_MorphStats(testObj=self, dictData=self.score_feat_dict,
                                                         prefix_name="scores_summary_")
        json_scores_files = json_scores_file.create()
        self.figures.extend(json_scores_files)

        # Saving table with population's results
        txt_table = mph_plots.TxtTable_MorphStats(testObj=self)
        table_files = txt_table.create()
        self.figures.extend(table_files)

        # Saving figure with with population's in the form of bar-plot
        barplot_figure = mph_plots.ScoresBars_MorphStats(testObj=self)
        barplot_files = barplot_figure.create()
        self.figures.extend(barplot_files)

        # Saving figures with statistics of the cells' morpho-features,
        # in the form of correlation, countour and distribution plots
        statsplot_figure = mph_plots.FeatsPop_MorphStats(testObj=self)
        statsplot_files = statsplot_figure.create()
        self.figures.extend(statsplot_files)

        return self.score

    def bind_score(self, score, model, observation, prediction):
        score.related_data["figures"] = self.figures
        return score
