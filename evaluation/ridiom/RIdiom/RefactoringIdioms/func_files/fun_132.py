def remove_unnecessary_package_from_lock_file(build_metadata_list, build_name, package):
    build_metadata = None
    for metadata in build_metadata_list:
        if metadata["build_name"] == build_name:
            build_metadata = metadata
            break
    if build_metadata is None:
        logger.warning(
            f"Could not find {build_name} in build_metadata_list. This may be expected"
            " if --select-build is used"
        )
        return
    folder_path = Path(build_metadata["folder"])
    platform = build_metadata["platform"]
    lock_file_basename = build_name
    if not lock_file_basename.endswith(platform):
        lock_file_basename = f"{lock_file_basename}_{platform}"
    lock_file_path = folder_path / f"{lock_file_basename}_conda.lock"
    with open(lock_file_path, "r") as f_read_only:
        lock_file_content = f_read_only.readlines()
        with open(lock_file_path, "w") as f_write:
            for line in lock_file_content:
                if package in line:
                    logger.debug(f"Removing {package} from {build_name} lock file")
                    logger.debug(f"Removed line: {line}")
                    continue
                f_write.write(line)
