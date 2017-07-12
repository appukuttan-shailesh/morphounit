class ProvidesNeuriteLengthInfo(sciunit.Capability):
    """
    Indicates that the model returns morphological information, namely:
    the neurite length of a digitally reconstructed cell
    """

    def get_NeuriteLength_info(self):
        """
        Must return a dictionary of the form:
            { 'NeuriteLength': {'mean': 'XX um', 'std': 'YY um'} }
        """
        raise NotImplementedError()

    def get_NeuriteLength(self):
        """ returns the neurite length in a model of a reconstructed neuron """
        NeuriteLength_info = self.get_NeuriteLength_info()
        return NeuriteLength_info['NeuriteLength']['mean']

