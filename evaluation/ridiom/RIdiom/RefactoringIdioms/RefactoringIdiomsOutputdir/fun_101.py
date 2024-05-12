def _add_dist_info(self, added_files):
    from poetry.core.masonry.builders.wheel import WheelBuilder
    added_files , builder  = added_files[:], WheelBuilder(self._poetry)
    dist_info = self._env.site_packages.mkdir(Path(builder.dist_info))
    self._debug(
        f"  - Adding the <c2>{dist_info.name}</c2> directory to"
        f" <b>{dist_info.parent}</b>"
    )
    with dist_info.joinpath("METADATA").open("w", encoding="utf-8") as f:
        builder._write_metadata_file(f)
    added_files.append(dist_info.joinpath("METADATA"))
    with dist_info.joinpath("INSTALLER").open("w", encoding="utf-8") as f:
        f.write("poetry")
    added_files.append(dist_info.joinpath("INSTALLER"))
    if self.convert_entry_points():
        with dist_info.joinpath("entry_points.txt").open(
            "w", encoding="utf-8"
        ) as f:
            builder._write_entry_points(f)
        added_files.append(dist_info.joinpath("entry_points.txt"))
    direct_url_json = dist_info.joinpath("direct_url.json")
    direct_url_json.write_text(
        json.dumps(
            {
                "dir_info": {"editable": True},
                "url": self._poetry.file.path.parent.absolute().as_uri(),
            }
        )
    )
    added_files.append(direct_url_json)
    record = dist_info.joinpath("RECORD")
    with record.open("w", encoding="utf-8", newline="") as f:
        csv_writer = csv.writer(f)
        for path in added_files:
            hash , size  = self._get_file_hash(path), path.stat().st_size
            csv_writer.writerow((path, f"sha256={hash}", size))
        csv_writer.writerow((record, "", ""))
