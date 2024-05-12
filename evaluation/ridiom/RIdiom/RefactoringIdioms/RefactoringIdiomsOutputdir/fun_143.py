def param_allowed(self, stat_name, include, exclude):
    if not include and not exclude:
        return True
    for p in exclude:
        if p in stat_name:
            return False
    if exclude and not include:
        return True
    for p in include:
        if p in stat_name:
            return True
    return False
