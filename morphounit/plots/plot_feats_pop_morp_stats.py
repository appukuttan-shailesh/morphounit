# For data manipulation
import os
from scipy import stats
import pandas as pd

import matplotlib
matplotlib.use('Agg')  # Force matplotlib to not use any Xwindows backend.
from matplotlib import pyplot as plt

import seaborn as sns

class FeatsPop_MorphStats:
    """
    Displays data in dictionary of cells population morpho-features
    in the form of correlation, countour and distribution plots
    """

    def __init__(self, testObj):

        self.testObj = testObj
        self.prefix_filename_lreg = "prediction_lreg_"
        self.prefix_filename_stats = "prediction_stats_"
        self.prefix_filename_stats_all = "prediction_allPlots_"
        self.filepath_list = list()

    def FeaturesPop_dict_DFrame(self):
        """
        Formats a dictionary of cells population morpho-features
        into a dictionary of DataFrame structures
        """

        pop_prediction_raw = self.testObj.prediction_cells_dict
        prediction_raw = pop_prediction_raw.values()[0]

        dict_pred_CellPart_df = dict()
        for CellPart in prediction_raw.keys():
            dict_pred_CellPart_df[CellPart] = pd.DataFrame(prediction_raw[CellPart])
            dict_pred_CellPart_df[CellPart].insert(0, 'CellPart', CellPart)

        return dict_pred_CellPart_df

    def feats_to_plot(self, all_feats=[], feats_exc=[]):

        for feat_name in feats_exc:
            try:
                all_feats.remove(feat_name)
            except:
                pass

        return all_feats

    def FeaturesPop_pairplots(self, dict_pred_CellPart_df=None):

        feats_exc = ['total_number_of_neurites', 'CellPart']
        for CellPart, prediction_raw_df in dict_pred_CellPart_df.items():

            all_feats = self.feats_to_plot(all_feats=list(prediction_raw_df), feats_exc=feats_exc)
            data = prediction_raw_df
            # plt.figure()
            g = sns.pairplot(data, vars=all_feats, diag_kind="kde", kind='reg', markers="+", diag_kws=dict(shade=True))
            g.fig.suptitle('Cell part: '+CellPart, fontsize=17)
            # plt.show()

            filepath = os.path.join(self.testObj.path_test_output, self.prefix_filename_stats + CellPart + '_FSI_pop.pdf')
            plt.savefig(filepath, dpi=600, )
            self.filepath_list.append(filepath)

    def corrfunc(self, x, y, **kws):

        r, p = stats.pearsonr(x, y)
        ax = plt.gca()
        ax.annotate("r = {:.2E}, p ={:.2E}".format(r, p),
                    xy=(.1, .9), xycoords=ax.transAxes)

    def FeaturesPop_linreg_plots(self, dict_pred_CellPart_df=None):

        feats_exc = ['total_number_of_neurites', 'CellPart']
        for CellPart, prediction_raw_df in dict_pred_CellPart_df.items():

            all_feats = self.feats_to_plot(all_feats=list(prediction_raw_df), feats_exc=feats_exc)
            data = prediction_raw_df
            # sns.pairplot(data, x_vars=all_feats, y_vars=all_feats, hue="CellPart", size=5, aspect=1, kind="reg")
            g = sns.PairGrid(data, x_vars=all_feats, y_vars=all_feats, size=5, aspect=1, palette=["red"])
            g.map(sns.regplot)
            g.map(self.corrfunc)
            plt.subplots_adjust(top=0.95)
            g.fig.suptitle('Cell part: '+CellPart, fontsize=17)

            filepath = os.path.join(self.testObj.path_test_output, self.prefix_filename_lreg + CellPart + '_FSI_pop.pdf')
            plt.savefig(filepath, dpi=600, )
            self.filepath_list.append(filepath)

    def FeaturesPop_PairtGrid_plots(self, dict_pred_CellPart_df=None):

        feats_exc = ['total_number_of_neurites', 'max_section_branch_order', 'CellPart']
        for CellPart, prediction_raw_df in dict_pred_CellPart_df.items():

            all_feats = self.feats_to_plot(all_feats=list(prediction_raw_df), feats_exc=feats_exc)
            data_excerpt_df = prediction_raw_df.loc[:, all_feats]
            data = data_excerpt_df
            g = sns.PairGrid(data, palette=["red"])
            g.map_upper(sns.regplot)
            g.map_upper(self.corrfunc)
            # g.map_upper(plt.reg, s=10)
            g.map_diag(sns.distplot, kde=False)
            g.map_lower(sns.kdeplot, cmap="Blues_d", n_levels=6)

            plt.subplots_adjust(top=0.95)
            g.fig.suptitle('Cell part: ' + CellPart, fontsize=17)

            filepath = os.path.join(self.testObj.path_test_output, self.prefix_filename_stats_all + CellPart + '_FSI_pop.pdf')
            plt.savefig(filepath, dpi=600, )
            self.filepath_list.append(filepath)

    def create(self):

        Dict_CellPart_DFrame_pred = self.FeaturesPop_dict_DFrame()
        self.FeaturesPop_pairplots(dict_pred_CellPart_df=Dict_CellPart_DFrame_pred)
        self.FeaturesPop_linreg_plots(dict_pred_CellPart_df=Dict_CellPart_DFrame_pred)
        # self.FeaturesPop_PairtGrid_plots(dict_pred_CellPart_df=Dict_CellPart_DFrame_pred)

        return self.filepath_list
