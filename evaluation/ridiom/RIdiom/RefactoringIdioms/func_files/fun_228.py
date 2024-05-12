def __init__(self, data=None, **kwds):
    self.data = data
    self.aes = make_aes(**kwds)
    self.legend = {}
