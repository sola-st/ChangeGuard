def _download_link(self, operation, link):
    package = operation.package
    output_dir = self._artifact_cache.get_cache_directory_for_link(link)
    original_archive = self._artifact_cache.get_cached_archive_for_link(
        link, strict=True
    )
    if original_archive is None:
        try:
            original_archive = self._download_archive(operation, link)
        except BaseException:
            cache_directory = self._artifact_cache.get_cache_directory_for_link(
                link
            )
            cached_file = cache_directory.joinpath(link.filename)
            if cached_file.exists():
                cached_file.unlink()
            raise
    archive = self._artifact_cache.get_cached_archive_for_link(
        link,
        strict=False,
        env=self._env,
    )
    if archive is None:
        raise RuntimeError(
            f"Package {link.url} cannot be installed in the current environment"
            f" {self._env.marker_env}"
        )
    if archive.suffix != ".whl":
        message = (
            f"  <fg=blue;options=bold>•</> {self.get_operation_message(operation)}:"
            " <info>Preparing...</info>"
        )
        self._write(operation, message)
        archive = self._chef.prepare(archive, output_dir=output_dir)
    self._populate_hashes_dict(original_archive, package)
    return archive
