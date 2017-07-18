import sciunit
import sciunit.scores
import morphounit.capabilities as cap

import quantities
import os

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#==============================================================================

class NeuriteLengthTest(sciunit.Test):
    """Tests a neurite length"""
    score_type = sciunit.scores.ZScore
    units = None
    id = "/tests/9?version=12"

    def __init__(self, observation={}, name="Neurite length test"):

        description = ("Tests the neurite length of a digitally reconstructed neuron")
        require_capabilities = (ProvidesNeuriteLengthInfo,)
        NeuriteLengthTest.units = quantities.um

        observation = self.format_data(observation)
        sciunit.Test.__init__(self, observation, name)
        self.directory_output = './output/'

    #----------------------------------------------------------------------

    def format_data(self, data):
        """
        This accepts data input in the form:
        ***** (observation) *****
        { 'NeuriteLength': {'mean': 'XX um', 'std': 'YY um'} }
        ***** (prediction) *****
        { 'NeuriteLength': {'mean': 'XX um'} }

        It splits the values of mean, std and value to numeric quantities
        and their units (via quantities package)
        """
        for key0 in data.keys():
            for key, val in data[key0].items():
                try:
                    quantity_parts = val.split()
                    number, units_str = float(quantity_parts[0]), " ".join(quantity_parts[1:])
                    assert (units_str == NeuriteLengthTest.units.units)
                    data[key0][key] = quantities.Quantity(number, units_str)
                except:
                    raise sciunit.Error("Values not in appropriate format. Required units: " + NeuriteLengthTest.units)
        return data

    # ----------------------------------------------------------------------

    def validate_observation(self, observation):
        for key0 in observation.keys():
            for val1 in observation[key0].values():
                try:
                    assert type(val1) is quantities.Quantity
                except Exception as e:
                    raise sciunit.ObservationError(("Observation must be of the form "
                                                    "{'mean': XX um,'std': YY um}"))

    #----------------------------------------------------------------------

    def generate_prediction(self, model, verbose=False):
        """Implementation of sciunit.Test.generate_prediction"""
        """
        nrn = nm.load_neuron('../corrected/fs-corrected3/030225-5-PV-rep-cor.swc')
        nrn_ap_seg_len = nm.get('neurite_lengths', nrn, neurite_type=nm.APICAL_DENDRITE)

        return features_names, features_list
        """
        self.model_name = model.name
        prediction = model.get_NeuriteLength_info()
        prediction = self.format_data(prediction)
        return prediction

    #----------------------------------------------------------------------

    def compute_score(self, observation, prediction, verbose=True):
        """Implementation of sciunit.Test.score_prediction"""
        print "observation = ", observation
        print "prediction = ", prediction
        score = sciunit.scores.ZScore.compute(observation['NeuriteLength'], prediction[''])
        score.description = "A simple Z-score"

        # create output directory
        path_test_output = self.directory_output + 'neurite_length/' + self.model_name + '/'
        if not os.path.exists(path_test_output):
            os.makedirs(path_test_output)

        # save figure with mean, std, value for observation and prediction
        fig = plt.figure()
        x = range(len(observation)) ## = 1
        ix = 0

        y_mean = observation["NeuriteLength"]["mean"]
        y_std = observation["NeuriteLength"]["std"]
        y_value = prediction["NeuriteLength"]["value"]
        ax_o = plt.errorbar(ix, y_mean, yerr=y_std, ecolor='black', elinewidth=2,
                        capsize=5, capthick=2, fmt='ob', markersize='5', mew=5)
        ax_p = plt.plot(ix, y_value, 'rx', markersize='8', mew=2)

        ix = ix + 1
        xlabels = 'NeuriteLength' # observation.keys()
        plt.xticks(x, xlabels, rotation=20)
        plt.tick_params(labelsize=11)
        plt.figlegend((ax_o,ax_p[0]), ('Observation', 'Prediction',), 'upper right')
        plt.margins(0.1)
        plt.ylabel("Neurite Length (um)")
        fig = plt.gcf()
        fig.set_size_inches(8, 6)
        filename = path_test_output + 'data_plot' + '.pdf'
        plt.savefig(filename, dpi=600,)
        self.figures.append(filename)

        # save document with Z-score data
        filename = path_test_output + 'score_summary' + '.txt'
        dataFile = open(filename, 'w')
        dataFile.write("==============================================================================\n")
        dataFile.write("Test Name: %s\n" % self.name)
        dataFile.write("Model Name: %s\n" % self.model_name)
        dataFile.write("------------------------------------------------------------------------------\n")
        dataFile.write("Parameter #\tExpt. mean\tExpt. std\tModel value\tZ-score\n")
        dataFile.write("..............................................................................\n")
        o_mean = observation["NeuriteLength"]["mean"]
        o_std = observation["NeuriteLength"]["std"]
        p_value = prediction["NeuriteLength"]["value"]
        dataFile.write("%s\t%s\t%s\t%s\t%s\n" % (key0, o_mean, o_std, p_value, score))
        dataFile.write("------------------------------------------------------------------------------\n")
        dataFile.write("Final Score: %s\n" % score)
        dataFile.write("==============================================================================\n")
        dataFile.close()
        self.figures.append(filename)

        return score

#==============================================================================
