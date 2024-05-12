def load(cls, env, with_dependencies = False):
    from poetry.core.packages.dependency import Dependency
    repo , seen , skipped  = cls(), set(), set()
    for entry in reversed(env.sys_path):
        if not entry.strip():
            logger.debug(
                "Project environment contains an empty path in <c1>sys_path</>,"
                " ignoring."
            )
            continue
        for distribution in sorted(
            metadata.distributions(  
                path=[entry],
            ),
            key=lambda d: str(d._path),  
        ):
            path = Path(str(distribution._path))  
            if path in skipped:
                continue
            name = distribution.metadata.get("name")  
            if name is None:
                logger.warning(
                    (
                        "Project environment contains an invalid distribution"
                        " (<c1>%s</>). Consider removing it manually or recreate"
                        " the environment."
                    ),
                    path,
                )
                skipped.add(path)
                continue
            name = canonicalize_name(name)
            if name in seen:
                continue
            package = cls.create_package_from_distribution(distribution, env)
            if with_dependencies:
                for require in distribution.metadata.get_all("requires-dist", []):
                    dep = Dependency.create_from_pep_508(require)
                    package.add_dependency(dep)
            seen.add(package.name)
            repo.add_package(package)
    return repo
