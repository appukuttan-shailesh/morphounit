import sciunit
from sciunit.scores import BooleanScore
# import morphounit.capabilities as cap
import morphounit.plots as plots

import os
from subprocess import call
import shlex
import json
from datetime import datetime

import matplotlib.backends.backend_pdf
from neurom.apps.cut_plane_detection import find_cut_plane
from neurom import load_neuron

#==============================================================================

class NeuroM_MorphoCheck(sciunit.Test):
    """
    Tests morphologies using NeuroM's `morph_check` feature.
    Returns `True` if all checks passed successfully; else `False`.
    """
    score_type = BooleanScore

    def __init__(self,
                 observation=None,
                 name="NeuroM MorphCheck",
                 base_directory=None):
        description = ("Tests morphologies using NeuroM's `morph_check` feature")
        # required_capabilities = (cap.HandlesNeuroM,)

        self.observation = observation
        if not base_directory:
            base_directory = "."
        self.base_directory = base_directory
        self.figures = []
        sciunit.Test.__init__(self, self.observation, name)

    #----------------------------------------------------------------------

    def generate_prediction(self, model, verbose=False):
        """Implementation of sciunit.Test.generate_prediction."""
        self.model_version = model.version
        self.path_test_output = os.path.join(self.base_directory, 'validation_results', 'neuroM_morph_hardChecks', self.model_version, datetime.now().strftime("%Y%m%d-%H%M%S"))
        if not os.path.exists(self.path_test_output):
            os.makedirs(self.path_test_output)

        # note: observation here is either the contents of the config file or a local path
        # if local path load contents
        if not isinstance(self.observation, dict):        
            with open(self.observation) as f:
                self.observation = json.load(f)
        # save morph_check config as local file
        morph_check_config_file = os.path.join(self.path_test_output, "morph_check_config.json")
        with open(morph_check_config_file,'w') as f:
            json.dump(self.observation["morph_check"], f, indent=4)
        cut_plane_config = self.observation["cut_plane"]

        morhpcheck_output_file = os.path.join(self.path_test_output, "morph_check_output.json")
        call(shlex.split("morph_check -C {} -o {} {}".format(morph_check_config_file, morhpcheck_output_file, model.morph_path)))
        with open(morhpcheck_output_file) as json_data:
            prediction = json.load(json_data)

        cut_plane_output_json = find_cut_plane(load_neuron(model.morph_path), bin_width=cut_plane_config["bin_width"], display=True)
        cut_plane_figure_list = []
        for key in cut_plane_output_json["figures"].keys():
            cut_plane_figure_list.append(cut_plane_output_json["figures"][key][0])
        cutplane_output_pdf = os.path.join(self.path_test_output, "cut_plane_figures.pdf")
        cut_plane_pdf = matplotlib.backends.backend_pdf.PdfPages(cutplane_output_pdf)
        for fig in xrange(1, len(cut_plane_figure_list)+1):
            cut_plane_pdf.savefig(fig)
        cut_plane_pdf.close()
        cutplane_output_file = os.path.join(self.path_test_output, "cut_plane_output.json")
        cut_plane_output_json.pop("figures")
        cut_plane_output_json["cut_leaves"] = cut_plane_output_json["cut_leaves"].tolist()
        with open(cutplane_output_file, "w") as outfile:
            json.dump(cut_plane_output_json, outfile, indent=4)

        self.figures.append(morhpcheck_output_file)
        self.figures.append(cutplane_output_file)
        self.figures.append(cutplane_output_pdf)
        return prediction

    #----------------------------------------------------------------------

    def compute_score(self, observation, prediction):
        """Implementation of sciunit.Test.score_prediction."""

        score_dict = {"PASS":True, "FAIL":False}
        self.score = BooleanScore(score_dict[prediction["STATUS"]])
        self.score.description = "Boolean: True = Pass / False = Fail"

        return self.score

    #----------------------------------------------------------------------

    def bind_score(self, score, model, observation, prediction):
        score.related_data["figures"] = self.figures
        score.related_data["passed"] = score.score
        return score
