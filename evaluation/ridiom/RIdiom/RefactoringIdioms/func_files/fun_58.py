def build_lang(
    lang = typer.Argument(
        ..., callback=lang_callback, autocompletion=complete_existing_lang
    )
):
    lang_path = Path("docs") / lang
    if not lang_path.is_dir():
        typer.echo(f"The language translation doesn't seem to exist yet: {lang}")
        raise typer.Abort()
    typer.echo(f"Building docs for: {lang}")
    build_dir_path = Path("docs_build")
    build_dir_path.mkdir(exist_ok=True)
    build_lang_path = build_dir_path / lang
    en_lang_path = Path("docs/en")
    site_path = Path("site").absolute()
    if lang == "en":
        dist_path = site_path
    else:
        dist_path = site_path / lang
    shutil.rmtree(build_lang_path, ignore_errors=True)
    shutil.copytree(lang_path, build_lang_path)
    shutil.copytree(en_docs_path / "data", build_lang_path / "data")
    en_config_path = en_lang_path / mkdocs_name
    en_config = mkdocs.utils.yaml_load(en_config_path.read_text(encoding="utf-8"))
    nav = en_config["nav"]
    lang_config_path = lang_path / mkdocs_name
    lang_config = mkdocs.utils.yaml_load(
        lang_config_path.read_text(encoding="utf-8")
    )
    lang_nav = lang_config["nav"]
    use_nav = nav[2:]
    lang_use_nav = lang_nav[2:]
    file_to_nav = get_file_to_nav_map(use_nav)
    sections = get_sections(use_nav)
    lang_file_to_nav = get_file_to_nav_map(lang_use_nav)
    use_lang_file_to_nav = get_file_to_nav_map(lang_use_nav)
    for file in file_to_nav:
        file_path = Path(file)
        lang_file_path = build_lang_path / "docs" / file_path
        en_file_path = en_lang_path / "docs" / file_path
        lang_file_path.parent.mkdir(parents=True, exist_ok=True)
        if not lang_file_path.is_file():
            en_text = en_file_path.read_text(encoding="utf-8")
            lang_text = get_text_with_translate_missing(en_text)
            lang_file_path.write_text(lang_text, encoding="utf-8")
            file_key = file_to_nav[file]
            use_lang_file_to_nav[file] = file_key
            if file_key:
                composite_key = ()
                new_key = ()
                for key_part in file_key:
                    composite_key += (key_part,)
                    key_first_file = sections[composite_key]
                    if key_first_file in lang_file_to_nav:
                        new_key = lang_file_to_nav[key_first_file]
                    else:
                        new_key += (key_part,)
                use_lang_file_to_nav[file] = new_key
    key_to_section = {(): []}
    for file, orig_file_key in file_to_nav.items():
        if file in use_lang_file_to_nav:
            file_key = use_lang_file_to_nav[file]
        else:
            file_key = orig_file_key
        section = get_key_section(key_to_section=key_to_section, key=file_key)
        section.append(file)
    new_nav = key_to_section[()]
    export_lang_nav = [lang_nav[0], nav[1]] + new_nav
    lang_config["nav"] = export_lang_nav
    build_lang_config_path = build_lang_path / mkdocs_name
    build_lang_config_path.write_text(
        yaml.dump(lang_config, sort_keys=False, width=200, allow_unicode=True),
        encoding="utf-8",
    )
    current_dir = os.getcwd()
    os.chdir(build_lang_path)
    mkdocs.commands.build.build(mkdocs.config.load_config(site_dir=str(dist_path)))
    os.chdir(current_dir)
    typer.secho(f"Successfully built docs for: {lang}", color=typer.colors.GREEN)
