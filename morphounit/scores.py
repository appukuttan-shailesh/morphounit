import math
import sciunit
import quantities

#==============================================================================


class CombineZScores(sciunit.Score):
    """
    Custom implementation for combining multiple Z-scores into a single value
    Approach: Mean of absolute Z-scores
    """

    def __init__(self, score, related_data={}):
        if not isinstance(score, Exception) and not isinstance(score, float):
            raise sciunit.InvalidScoreError("Score must be a float.")
        else:
            super(CombineZScores,self).__init__(score, related_data=related_data)


    @classmethod
    def compute(cls, input_scores):
        """
        Accepts a sequence of Z-scores (e.g. computed via sciunit.scores.ZScore)
        and combines them into a single score.

        To keep this generic, the input data format (supplied by the test) are:
        input_scores = [Z1, Z2, ..., Zn]
            where Zi corresponds to the individual Z-scores
        """
        score = sum(map(abs,input_scores)) / len(input_scores)
        return CombineZScores(score)

    _description = ("Combining Z-scores between observation and prediction")

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
        #return 'Combined Z-score = %.2f' % self.score
        return '%.2f' % self.score


#==============================================================================


class RangeCheck(sciunit.Score):
    """
    Checks if value is within specified range
    Approach: Returns True if within range, False otherwise
    """

    _allowed_types = (bool,)

    _description = ('Checks if value of prediction is within the '
                    ' specified range for the observation')

    @classmethod
    def compute(cls, observation, prediction):
        """
        Computes True/False based on whether value is within the range.
        """
        assert isinstance(prediction,dict)
        assert isinstance(observation,dict)

        p_val = prediction['value']
        o_min = observation['min']
        o_max = observation['max']

        if p_val >= o_min and p_val <= o_max:
            score = True
        else:
            score = False
        return RangeCheck(score)

    @property
    def sort_key(self):
        """
        Returns 1.0 for a Boolean score of True, and 0.0 for a score of False.
        """
        return 1.0 if self.score else 0.0

    def __str__(self):
        return 'Pass' if self.score else 'Fail'


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
