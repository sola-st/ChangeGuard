def handle_user_exception(self, e):
    exc_type, exc_value, tb = sys.exc_info()
    assert exc_value is e
    if (
        (self.debug or self.config['TRAP_BAD_REQUEST_ERRORS'])
        and isinstance(e, BadRequestKeyError)
        and e.description is BadRequestKeyError.description
    ):
        e.description = "KeyError: '{0}'".format(*e.args)
    if isinstance(e, HTTPException) and not self.trap_http_exception(e):
        return self.handle_http_exception(e)
    handler = self._find_error_handler(e)
    if handler is None:
        reraise(exc_type, exc_value, tb)
    return handler(e)
