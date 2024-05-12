def _get_page_title(self, page):
    fname , doc  = os.path.join(SOURCE_PATH, f'{page}.rst'), docutils.utils.new_document('<doc>', docutils.frontend.get_default_settings(docutils.parsers.rst.Parser))
    with open(fname, encoding="utf-8") as f:
        data = f.read()
    parser = docutils.parsers.rst.Parser()
    with open(os.devnull, "a", encoding="utf-8") as f:
        doc.reporter.stream = f
        parser.parse(data, doc)
    section = next(
        node for node in doc.children if isinstance(node, docutils.nodes.section)
    )
    title = next(
        node for node in section.children if isinstance(node, docutils.nodes.title)
    )
    return title.astext()
