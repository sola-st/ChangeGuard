def jmespath(self, query, **kwargs):
    if not hasattr(self.selector, "jmespath"):  
        raise AttributeError(
            "Please install parsel >= 1.8.1 to get jmespath support"
        )
    return self.selector.jmespath(query, **kwargs)  
