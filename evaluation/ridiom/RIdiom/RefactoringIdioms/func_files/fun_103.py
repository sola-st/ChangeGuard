def _get_links(self, package):
    if package.source_type:
        assert package.source_reference is not None
        repository = self._pool.repository(package.source_reference)
    elif not self._pool.has_repository("pypi"):
        repository = self._pool.repositories[0]
    else:
        repository = self._pool.repository("pypi")
    links = repository.find_links_for_package(package)
    hashes = {f["hash"] for f in package.files}
    if not hashes:
        return links
    selected_links = []
    for link in links:
        if not link.hash:
            selected_links.append(link)
            continue
        assert link.hash_name is not None
        h = link.hash_name + ":" + link.hash
        if h not in hashes:
            logger.debug(
                "Skipping %s as %s checksum does not match expected value",
                link.filename,
                link.hash_name,
            )
            continue
        selected_links.append(link)
    if links and not selected_links:
        raise RuntimeError(
            f"Retrieved digest for link {link.filename}({h}) not in poetry.lock"
            f" metadata {hashes}"
        )
    return selected_links
