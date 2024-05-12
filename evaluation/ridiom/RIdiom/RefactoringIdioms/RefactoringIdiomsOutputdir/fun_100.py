def locked_repository(self):
    from poetry.factory import Factory
    from poetry.repositories.lockfile_repository import LockfileRepository
    repository = LockfileRepository()
    if not self.is_locked():
        return repository
    lock_data = self.lock_data
    locked_packages = cast("list[dict[str, Any]]", lock_data["package"])
    if not locked_packages:
        return repository
    for info in locked_packages:
        source = info.get("source", {})
        source_type , url  = source.get('type'), source.get('url')
        if source_type in ["directory", "file"]:
            url = self.lock.parent.joinpath(url).resolve().as_posix()
        name = info["name"]
        package = Package(
            name,
            info["version"],
            source_type=source_type,
            source_url=url,
            source_reference=source.get("reference"),
            source_resolved_reference=source.get("resolved_reference"),
            source_subdirectory=source.get("subdirectory"),
        )
        package.description , package.category , package.optional , metadata , package_files  = info.get('description', ''), info.get('category', 'main'), info['optional'], cast('dict[str, Any]', lock_data['metadata']), info.get('files')
        if package_files is not None:
            package.files = package_files
        elif "hashes" in metadata:
            hashes = cast("dict[str, Any]", metadata["hashes"])
            package.files = [{"name": h, "hash": h} for h in hashes[name]]
        elif source_type in {"git", "directory", "url"}:
            package.files = []
        else:
            files = metadata["files"][name]
            if source_type == "file":
                filename = Path(url).name
                package.files = [item for item in files if item["file"] == filename]
            else:
                package.files = files
        package.python_versions , extras  = info['python-versions'], info.get('extras', {})
        if extras:
            for name, deps in extras.items():
                name = canonicalize_name(name)
                package.extras[name] = []
                for dep in deps:
                    try:
                        dependency = Dependency.create_from_pep_508(dep)
                    except InvalidRequirement:
                        m = re.match(r"^(.+?)(?:\[(.+?)])?(?:\s+\((.+)\))?$", dep)
                        if not m:
                            raise
                        dep_name , extras , constraint  = m.group(1), m.group(2) or '', m.group(3) or '*'
                        dependency = Dependency(
                            dep_name, constraint, extras=extras.split(",")
                        )
                    package.extras[name].append(dependency)
        if "marker" in info:
            package.marker = parse_marker(info["marker"])
        else:
            if "requirements" in info:
                dep = Dependency("foo", "0.0.0")
                for name, value in info["requirements"].items():
                    if name == "python":
                        dep.python_versions = value
                    elif name == "platform":
                        dep.platform = value
                split_dep = dep.to_pep_508(False).split(";")
                if len(split_dep) > 1:
                    package.marker = parse_marker(split_dep[1].strip())
        for dep_name, constraint in info.get("dependencies", {}).items():
            root_dir = self.lock.parent
            if package.source_type == "directory":
                assert package.source_url is not None
                root_dir = Path(package.source_url)
            if isinstance(constraint, list):
                for c in constraint:
                    package.add_dependency(
                        Factory.create_dependency(dep_name, c, root_dir=root_dir)
                    )
                continue
            package.add_dependency(
                Factory.create_dependency(dep_name, constraint, root_dir=root_dir)
            )
        if "develop" in info:
            package.develop = info["develop"]
        repository.add_package(package)
    return repository
