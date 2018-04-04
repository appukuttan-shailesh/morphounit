import sciunit
from sciunit.scores import BooleanScore
# import morphounit.capabilities as cap
import morphounit.plots as plots

import os
from subprocess import call
import shlex
import json
from datetime import datetime

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
        # check if local path, else try to retrieve online
        if not os.path.isfile(self.observation):
            # create a local copy for reference
            config_file = os.path.join(self.path_test_output, "config.yml")
            with open(config_file,'w') as f:
                f.write(self.observation)
            self.observation = config_file

        output_file = os.path.join(self.path_test_output, "output.json")
        call(shlex.split("morph_check -C {} -o {} {}".format(self.observation, output_file, model.morph_path)))
        with open(output_file) as json_data:
            prediction = json.load(json_data)
        print "Prediction = ", prediction

        self.figures.append(output_file)
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
        return score
