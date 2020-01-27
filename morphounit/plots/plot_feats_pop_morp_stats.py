# For data manipulation
import os
from scipy import stats
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Force matplotlib to not use any Xwindows backend.
from matplotlib import pyplot as plt


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
        prediction_raw = list(pop_prediction_raw.values())[0]

        dict_pred_CellPart_df = dict()
        for CellPart in prediction_raw.keys():
            dict_pred_CellPart_df[CellPart] = pd.DataFrame(prediction_raw[CellPart])

        return dict_pred_CellPart_df

    def corrfunc(self, x, y, **kws):
        r, p = stats.pearsonr(x, y)
        ax = plt.gca()
        ax.annotate(f"r = {r:.2E}\n(p ={p:.2E})", xy=(.1, .9), xycoords=ax.transAxes)

    def df_drop_features(self, df=None, threshold_corr=0.95, threshold_var=0.05):
        '''Drops one in any pair of highly correlated features of a DataFrame,
        as the calculation of some quantities may not be posible. Besides,
        columns with no variance are excluded. For instance,
        joint kernel distributions estimates (kde) for two highly correlated
        features may not be computed. The same holds for features with low variability.

        The cutoffs for correlation (or variance) to be considered as too high (or too low)
        are given by 'threshold_corr' ('threshold_var').

        Note: Adapted from
        https://chrisalbon.com/machine_learning/feature_selection/
        drop_highly_correlated_features/
        '''

        feats_to_drop = list()
        # Compute the correlation DataFrame of the original DataFrame of feature values
        corr_matrix_df = df.corr().abs()
        # Build a copy with the elements below the first diagonal as False
        upper = corr_matrix_df.where(np.triu(np.ones(corr_matrix_df.shape), k=1).astype(np.bool))
        # Find and collect one feature name in any pair of correlated features
        features_hcorr = [column for column in df.columns
                          if any(upper[column] > threshold_corr)]
        feats_to_drop.extend(features_hcorr)

        # Compute the variance DataSeries of the original DataFrame of feature values
        var_series = df.var().abs()
        # Find and collect all features with low variance
        feats_no_var = [column for column in df.columns
                        if var_series[column] < threshold_var]
        feats_to_drop.extend(feats_no_var)

        # Drop all those disposable (maybe superfluous) features found
        df.drop(df[feats_to_drop], axis=1, inplace=True)

        return df

    def FeaturesPop_Linreg_plots(self, dict_pred_CellPart_df=None):
        '''Plots a histogram for values of each morpho-feature, in the diagonal,
        together with a kernel density estimation (kde) for that histogram.
        Linear correlation results are shown below and above the diagonal for
        the same pair of morpho-feattures (i.e., numerical results are symmetric).
        '''
        for CellPart, prediction_raw_df in list(dict_pred_CellPart_df.items()):
            data = self.df_drop_features(df=prediction_raw_df)

            g = sns.pairplot(data, height=5, aspect=1, diag_kind="kde")
            # g = sns.PairGrid(data, size=5, aspect=1, palette=["red"])
            # g.map(sns.regplot)
            # g.map(self.corrfunc)
            g.map_upper(sns.regplot)
            g.map_upper(self.corrfunc)
            g.map_diag(sns.distplot, kde=True)
            g.map_lower(sns.regplot)
            g.map_lower(self.corrfunc)

            plt.subplots_adjust(top=0.95)
            g.fig.suptitle('Cell part: '+CellPart, fontsize=17)

            filepath = os.path.join(self.testObj.path_test_output, self.prefix_filename_lreg + CellPart + '_FSI_pop.pdf')
            plt.savefig(filepath, dpi=600, )
            self.filepath_list.append(filepath)

    def FeaturesPop_ContourLinreg_plots(self, dict_pred_CellPart_df=None):
        '''Plots a histogram for values of each morpho-feature, in the diagonal,
        together with a kernel density estimation (kde) for that histogram.
        Linear correlation results and contour (kde) plots for the same pair of
        morpho-feattures are shown above and below the diagonal, respectively.

        Note that some morpho-features are excluded from the analysis, when their
        correlation is high , as their (kde) countour-plots can not be computed.
        '''
        for CellPart, prediction_raw_df in list(dict_pred_CellPart_df.items()):
            data = self.df_drop_features(df=prediction_raw_df)

            g = sns.pairplot(data, height=5, aspect=1, diag_kind="kde")
            # g = sns.PairGrid(data, size=5, aspect=1, palette=["red"]
            g.map_upper(sns.regplot)
            g.map_upper(self.corrfunc)
            # g.map_upper(plt.reg, s=10)
            g.map_diag(sns.distplot, kde=True)
            g.map_lower(sns.kdeplot, cmap="Blues_d", n_levels=8)

            plt.subplots_adjust(top=0.95)
            g.fig.suptitle('Cell part: ' + CellPart, fontsize=17)

            filepath = os.path.join(self.testObj.path_test_output, self.prefix_filename_stats_all + CellPart + '_FSI_pop.pdf')
            plt.savefig(filepath, dpi=600, )
            self.filepath_list.append(filepath)

    def create(self):
        Dict_CellPart_DFrame_pred = self.FeaturesPop_dict_DFrame()
        self.FeaturesPop_Linreg_plots(dict_pred_CellPart_df=Dict_CellPart_DFrame_pred)
        self.FeaturesPop_ContourLinreg_plots(dict_pred_CellPart_df=Dict_CellPart_DFrame_pred)

        return self.filepath_list
