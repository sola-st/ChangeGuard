def make_response(self, rv):
    status = headers = None
    if isinstance(rv, tuple):
        len_rv = len(rv)
        if len_rv == 3:
            rv, status, headers = rv
        elif len_rv == 2:
            if isinstance(rv[1], (Headers, dict, tuple, list)):
                rv, headers = rv
            else:
                rv, status = rv
        else:
            raise TypeError(
                'The view function did not return a valid response tuple.'
                ' The tuple must have the form (body, status, headers),'
                ' (body, status), or (body, headers).'
            )
    if rv is None:
        raise TypeError(
            'The view function did not return a valid response. The'
            ' function either returned None or ended without a return'
            ' statement.'
        )
    if not isinstance(rv, self.response_class):
        if isinstance(rv, (text_type, bytes, bytearray)):
            rv = self.response_class(rv, status=status, headers=headers)
            status = headers = None
        else:
            try:
                rv = self.response_class.force_type(rv, request.environ)
            except TypeError as e:
                new_error = TypeError(
                    '{e}\nThe view function did not return a valid'
                    ' response. The return type must be a string, tuple,'
                    ' Response instance, or WSGI callable, but it was a'
                    ' {rv.__class__.__name__}.'.format(e=e, rv=rv)
                )
                reraise(TypeError, new_error, sys.exc_info()[2])
    if status is not None:
        if isinstance(status, (text_type, bytes, bytearray)):
            rv.status = status
        else:
            rv.status_code = status
    if headers:
        rv.headers.extend(headers)
    return rv
