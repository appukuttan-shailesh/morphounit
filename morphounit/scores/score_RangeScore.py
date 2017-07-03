import math
import sciunit
import quantities

#==============================================================================

class RangeScore(sciunit.Score):
    """
    Checks if value is within specified range
    Approach: Returns 0 if within range, the difference otherwise
    """

    _allowed_types = (float,)

    _description = ('Returns 0.0 if value of prediction is within the specified'
                    ' range for the observation; else returns difference')

    @classmethod
    def compute(cls, observation, prediction):
        """
        Computes score based on whether value is within the range or not.
        """
        assert isinstance(prediction,dict)
        assert isinstance(observation,dict)

        p_val = prediction['value']
        o_min = observation['min']
        o_max = observation['max']

        if p_val < o_min:
            score = o_min - p_val
        elif p_val > o_max:
            score = p_val - o_max
        else:
            score = 0.0

        if isinstance(score, quantities.quantity.Quantity):
            score = score.item()
        return RangeScore(score)

    @property
    def sort_key(self):
        """
        ## Copied from sciunit.scores.ZScore ##
        Returns 1.0 for a score of 0, falling to 0.0 for extremely positive
        or negative values.
        """
        cdf = (1.0 + math.erf(self.score / math.sqrt(2.0))) / 2.0
        return 1 - 2*math.fabs(0.5 - cdf)

    def __str__(self):
        return '%.2f' % self.score
