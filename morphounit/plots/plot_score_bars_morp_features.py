# For data manipulation
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')  # Force matplotlib to not use any Xwindows backend.

from matplotlib import pyplot as plt
import seaborn as sns

#==============================================================================


class ScoresBars_MorphFeatures:
    """
    Displays data in table inside text file
    """

    def __init__(self, testObj):
        self.testObj = testObj
        self.filename = "score_bars"

    def create(self):

        filepath = self.testObj.path_test_output + "/" + self.filename + '.pdf'

        score_label = "Mean-ZScore"
        scores_cell_floats = dict.fromkeys(self.testObj.score_cell_dict.keys(), [])
        for cell_ID, score_val in self.testObj.score_cell_dict.items():
            scores_cell_floats[cell_ID] = score_val[score_label]

        scores_cell_df = pd.DataFrame(scores_cell_floats, index=[score_label])
        scores_cell_df = scores_cell_df.transpose()

        # pal = sns.cubehelix_palette(len(observation))
        pal = sns.color_palette('Reds', len(scores_cell_floats))
        rank = [int(value) - 1 for value in scores_cell_df[score_label].rank()]
        axis_obj = sns.barplot(x=scores_cell_df[score_label], y=scores_cell_df.index, palette=np.array(pal)[rank])
        plt.subplots_adjust(left=0.3)
        axis_obj.set_yticklabels(axis_obj.get_yticklabels(), fontsize=4)
        axis_obj.set(xlabel=score_label, ylabel='Cell')
        sns.despine()

        plt.savefig(filepath, dpi=600, )

        return filepath
