def new_lang(lang = typer.Argument(..., callback=lang_callback)):
    new_path = Path("docs") / lang
    if new_path.exists():
        typer.echo(f"The language was already created: {lang}")
        raise typer.Abort()
    new_path.mkdir()
    new_config , new_config_path  = get_base_lang_config(lang), Path(new_path) / mkdocs_name
    new_config_path.write_text(
        yaml.dump(new_config, sort_keys=False, width=200, allow_unicode=True),
        encoding="utf-8",
    )
    new_config_docs_path = new_path / "docs"
    new_config_docs_path.mkdir()
    en_index_path = en_docs_path / "docs" / "index.md"
    new_index_path , en_index_content  = new_config_docs_path / 'index.md', en_index_path.read_text(encoding='utf-8')
    new_index_content = f"{missing_translation_snippet}\n\n{en_index_content}"
    new_index_path.write_text(new_index_content, encoding="utf-8")
    new_overrides_gitignore_path = new_path / "overrides" / ".gitignore"
    new_overrides_gitignore_path.parent.mkdir(parents=True, exist_ok=True)
    new_overrides_gitignore_path.write_text("")
    typer.secho(f"Successfully initialized: {new_path}", color=typer.colors.GREEN)
    update_languages(lang=None)
