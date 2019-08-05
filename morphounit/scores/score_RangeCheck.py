import sciunit

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
