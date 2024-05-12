def package(
    self, name, version, extras = None
):
    canonicalized_name = canonicalize_name(name)
    for package in self.packages:
        if canonicalized_name == package.name and package.version == version:
            return package
    raise PackageNotFound(f"Package {name} ({version}) not found.")
