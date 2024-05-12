def solve(self):
    locked = {}
    for package in self._locked.packages:
        locked[package.name] = package
    return locked
