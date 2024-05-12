def generate_back_references(link, base_path):
    is_downloaded, file_name = download_file(link)
    if not is_downloaded:
        old_to_new = []
    else:
        print(f"Constructs old to new mapping from redirects.txt for {base_path}")
        old_to_new = construct_old_to_new_tuple_mapping(file_name)
    old_to_new.append(("index.html", "changelog.html"))
    old_to_new.append(("index.html", "security.html"))
    old_to_new.append(("security.html", "security/security-model.html"))
    for versioned_provider_path in (p for p in base_path.iterdir() if p.is_dir()):
        print(f"Processing {base_path}, version: {versioned_provider_path.name}")
        for old, new in old_to_new:
            if (versioned_provider_path / old).exists():
                if "/" in new:
                    split_new_path, file_name = new.rsplit("/", 1)
                    dest_dir = versioned_provider_path / split_new_path
                else:
                    file_name = new
                    dest_dir = versioned_provider_path
                relative_path = os.path.relpath(old, new)
                relative_path = relative_path.replace("../", "", 1)
                os.makedirs(dest_dir, exist_ok=True)
                dest_file_path = dest_dir / file_name
                create_back_reference_html(relative_path, dest_file_path)
