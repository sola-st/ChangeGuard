def handle_exception(self, e):
    exc_type, exc_value, tb = sys.exc_info()
    got_request_exception.send(self, exception=e)
    if self.propagate_exceptions:
        if exc_value is e:
            reraise(exc_type, exc_value, tb)
        else:
            raise e
    self.log_exception((exc_type, exc_value, tb))
    handler = self._find_error_handler(InternalServerError())
    if handler is None:
        return InternalServerError()
    return self.finalize_request(handler(e), from_error_handler=True)
