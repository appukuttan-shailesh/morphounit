import sciunit

#==============================================================================

class HandlesNeuroM(sciunit.Capability):
    """
    Generic capability for handling morphologies loaded via NeuroM
    """

    def get_soma_diameter_info(self):
        """
        Must return a dictionary of the form:
            {"diameter": {"value": "XX um"}}
        """
        raise NotImplementedError()
