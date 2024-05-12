def build_all():
    site_path = Path("site").absolute()
    update_languages(lang=None)
    current_dir = os.getcwd()
    os.chdir(en_docs_path)
    typer.echo("Building docs for: en")
    subprocess.run(["mkdocs", "build", "--site-dir", site_path], check=True)
    os.chdir(current_dir)
    langs = []
    for lang in get_lang_paths():
        if lang == en_docs_path or not lang.is_dir():
            continue
        langs.append(lang.name)
    cpu_count = os.cpu_count() or 1
    process_pool_size = cpu_count * 4
    typer.echo(f"Using process pool size: {process_pool_size}")
    with Pool(process_pool_size) as p:
        p.map(build_lang, langs)
