def chain_deferred(d1, d2):
    return d1.chainDeferred(d2).addBoth(lambda _:d2)
