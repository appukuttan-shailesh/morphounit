# For data manipulation
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')  # Force matplotlib to not use any Xwindows backend.

from matplotlib import pyplot as plt
import seaborn as sns
import os


class ScoresBars_MorphStats:
    """
    Displays data in table inside text file
    """

    def __init__(self, testObj):
        self.testObj = testObj
        self.prefix_filename_cells = "score_bars_cells"
        self.prefix_filename_cell_feat = "score_barPlots_"
        self.filepath_list = list()

    def score_barplot(self, filepath=None, scores_floats={}, score_label=None,
                      xlabel=None, x_fontsize=5, ylabel=None, y_fontsize=5, title=None):

        fig = plt.figure()

        # pal = sns.cubehelix_palette(len(scores_floats))
        pal = sns.color_palette('Reds', len(scores_floats))

        scores_floats_df = pd.DataFrame(scores_floats, index=[score_label]).transpose()

        rank = [int(value) - 1 for value in scores_floats_df[score_label].rank()]
        axis_obj = sns.barplot(x=scores_floats_df[score_label], y=scores_floats_df.index, palette=np.array(pal)[rank])

        plt.subplots_adjust(left=0.3)
        axis_obj.set(xlabel=xlabel, ylabel=ylabel, title=title)
        axis_obj.set_yticklabels(axis_obj.get_yticklabels(), fontsize=y_fontsize)
        # axis_obj.set_xticklabels(axis_obj.get_xticklabels(), fontsize=x_fontsize)

        sns.despine()

        plt.savefig(filepath, dpi=600, )
        self.filepath_list.append(filepath)

        plt.close(fig)

        return self.filepath_list

    def create(self):

        # --------------------------- Plotting overall cell scores -------------------------------------------------
        """
        filepath_score_cells = os.path.join(self.testObj.path_test_output, self.prefix_filename_cells + '.pdf')
        score_label = "A mean |Z-score|"
        plt_title = "Cells scores summary"

        scores_cell_floats = dict.fromkeys(self.testObj.score_cell_dict.keys(), [])
        for cell_ID, score_val in self.testObj.score_cell_dict.items():
            scores_cell_floats[cell_ID] = score_val[score_label]

        self.score_barplot(filepath=filepath_score_cells, scores_floats=scores_cell_floats, score_label=score_label,
                           xlabel=score_label, ylabel='Cell', title=plt_title)
        """
        # -------------------------- Plotting cell's feature scores ------------------------------------------------

        score_label = "|Z-Score|"

        scores_dict = self.testObj.score_feat_dict
        for key_0 in scores_dict:  # cell ID keys
            plt_title = key_0
            filepath_score_feat = \
                os.path.join(self.testObj.path_test_output, self.prefix_filename_cell_feat + plt_title + '.pdf')

            scores_feat_floats = dict()
            for key_1 in scores_dict[key_0]:  # cell's part keys: soma, axon, apical_dendrite or basal_dendrite
                if 'score' in key_1:  # Excluding the overall cell's score
                    continue
                for key_2 in scores_dict[key_0][key_1]:  # features name keys

                    feat_name = "{}.{}".format(key_1, key_2)
                    scores_feat_floats[feat_name] = abs(scores_dict[key_0][key_1][key_2]["score"])

            plt.close('all')
            self.score_barplot(filepath=filepath_score_feat, scores_floats=scores_feat_floats, score_label=score_label,
                               xlabel=score_label, x_fontsize=6, ylabel='morpho-features', y_fontsize=6, title=plt_title)

        return self.filepath_list
