def solve(self, use_latest=None):  
    provider , locked  = Provider(self._package, self._pool, self._io), {}
    try:
        result = resolve_version(self._package, provider, locked=locked, use_latest=use_latest)
    except SolveFailure as e:
        raise SolverProblemError(e)
    packages , requested  = result.packages, self._package.all_requires
    for package in packages:
        category, optional, python, platform = self._get_tags_for_package(
            package, packages, requested
        )
        package.category , package.optional , requirements  = category, optional, {}
        if None is not python != '*':
            requirements['python'] = python
        if None is not platform != '*':
            requirements['platform'] = platform
        package.requirements = requirements
    operations = []
    for package in packages:
        for pkg in self._installed.packages:
            if package.name == pkg.name:
                if package.version != pkg.version:
                    operations.append(Update(pkg, package))
                else:
                    operations.append(Install(package).skip('Already installed'))
                break
        else:
            operations.append(Install(package))
    for pkg in self._locked.packages:
        for package in packages:
            if pkg.name == package.name:
                break
        else:
            skip = True
            for installed in self._installed.packages:
                if installed.name == pkg.name:
                    skip = False
                    break
            op = Uninstall(pkg)
            if skip:
                op.skip('Not currently installed')
            operations.append(op)
    requested_names = [r.name for r in self._package.all_requires]
    return sorted(
        operations,
        key=lambda o: (
            1 if o.package.name in requested_names else 0,
            o.package.name
        )
    )
