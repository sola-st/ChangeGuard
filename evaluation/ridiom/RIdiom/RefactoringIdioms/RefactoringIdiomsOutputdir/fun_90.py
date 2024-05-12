def complete_package(
    self, dependency_package
):
    package , dependency  = dependency_package.package, dependency_package.dependency
    if package.is_root():
        dependency_package = dependency_package.clone()
        package = dependency_package.package
        dependency , requires  = dependency_package.dependency, package.all_requires
    elif package.is_direct_origin():
        requires = package.requires
    else:
        try:
            dependency_package = DependencyPackage(
                dependency,
                self._pool.package(
                    package.pretty_name,
                    package.version,
                    extras=list(dependency.extras),
                    repository_name=dependency.source_name,
                ),
            )
        except PackageNotFound as e:
            try:
                dependency_package = next(
                    DependencyPackage(dependency, pkg)
                    for pkg in self.search_for_installed_packages(dependency)
                )
            except StopIteration:
                raise e from e
        package = dependency_package.package
        dependency , requires  = dependency_package.dependency, package.requires
    optional_dependencies , _dependencies  = [], []
    if dependency.extras:
        for extra in dependency.extras:
            if extra not in package.extras:
                continue
            optional_dependencies += [d.name for d in package.extras[extra]]
        dependency_package = dependency_package.with_features(
            list(dependency.extras)
        )
        package = dependency_package.package
        dependency , new_dependency  = dependency_package.dependency, package.without_features().to_dependency()
        if not new_dependency.source_name and dependency.source_name:
            new_dependency.source_name = dependency.source_name
        _dependencies.append(new_dependency)
    for dep in requires:
        if not self._python_constraint.allows_any(dep.python_constraint):
            continue
        if dep.name in self.UNSAFE_PACKAGES:
            continue
        if self._env and not dep.marker.validate(self._env.marker_env):
            continue
        if not package.is_root() and (
            (dep.is_optional() and dep.name not in optional_dependencies)
            or (
                dep.in_extras
                and not set(dep.in_extras).intersection(dependency.extras)
            )
        ):
            continue
        _dependencies.append(dep)
    if self._load_deferred:
        for dep in _dependencies:
            if dep.is_direct_origin():
                locked = self.get_locked(dep)
                if locked is not None and locked.package.is_same_package_as(dep):
                    continue
                self.search_for_direct_origin_dependency(dep)
    dependencies , duplicates  = self._get_dependencies_with_overrides(_dependencies, dependency_package), defaultdict(list)
    for dep in dependencies:
        duplicates[dep.complete_name].append(dep)
    dependencies = []
    for dep_name, deps in duplicates.items():
        if len(deps) == 1:
            dependencies.append(deps[0])
            continue
        self.debug(f"<debug>Duplicate dependencies for {dep_name}</debug>")
        deps = self._resolve_overlapping_markers(package, deps)
        if len(deps) == 1:
            self.debug(f"<debug>Merging requirements for {deps[0]!s}</debug>")
            dependencies.append(deps[0])
            continue
        def fmt_warning(d):
            dependency_marker = d.marker if not d.marker.is_any() else "*"
            return (
                f"<c1>{d.name}</c1> <fg=default>(<c2>{d.pretty_constraint}</c2>)</>"
                f" with markers <b>{dependency_marker}</b>"
            )
        warnings = ", ".join(fmt_warning(d) for d in deps[:-1])
        warnings += f" and {fmt_warning(deps[-1])}"
        self.debug(
            f"<warning>Different requirements found for {warnings}.</warning>"
        )
        overrides , overrides_marker_intersection  = [], AnyMarker()
        for dep_overrides in self._overrides.values():
            for dep in dep_overrides.values():
                overrides_marker_intersection = (
                    overrides_marker_intersection.intersect(dep.marker)
                )
        for dep in deps:
            if not overrides_marker_intersection.intersect(dep.marker).is_empty():
                current_overrides = self._overrides.copy()
                package_overrides = current_overrides.get(
                    dependency_package, {}
                ).copy()
                package_overrides.update({dep.name: dep})
                current_overrides.update({dependency_package: package_overrides})
                overrides.append(current_overrides)
        if overrides:
            raise OverrideNeeded(*overrides)
    clean_dependencies = []
    for dep in dependencies:
        if not dependency.transitive_marker.without_extras().is_any():
            transitive_marker_intersection = (
                dependency.transitive_marker.without_extras().intersect(
                    dep.marker.without_extras()
                )
            )
            if transitive_marker_intersection.is_empty():
                continue
            dep.transitive_marker = transitive_marker_intersection
        if not dependency.python_constraint.is_any():
            python_constraint_intersection = dep.python_constraint.intersect(
                dependency.python_constraint
            )
            if python_constraint_intersection.is_empty():
                continue
        clean_dependencies.append(dep)
    package = package.with_dependency_groups([], only=True)
    dependency_package = DependencyPackage(dependency, package)
    for dep in clean_dependencies:
        package.add_dependency(dep)
    return dependency_package
