def load_app(self):
    if self._loaded_app is not None:
        return self._loaded_app
    if self.create_app is not None:
        app = self.create_app()
    else:
        if self.app_import_path:
            path, name = (
                re.split(r":(?![\\/])", self.app_import_path, maxsplit=1) + [None]
            )[:2]
            import_name = prepare_import(path)
            app = locate_app(import_name, name)
        else:
            for path in ("wsgi.py", "app.py"):
                import_name = prepare_import(path)
                app = locate_app(import_name, None, raise_if_not_found=False)
                if app:
                    break
    if not app:
        raise NoAppException(
            "Could not locate a Flask application. Use the"
            " 'flask --app' option, 'FLASK_APP' environment"
            " variable, or a 'wsgi.py' or 'app.py' file in the"
            " current directory."
        )
    if self.set_debug_flag:
        app.debug = get_debug_flag()
    self._loaded_app = app
    return app
