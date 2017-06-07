import math
import sciunit

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
