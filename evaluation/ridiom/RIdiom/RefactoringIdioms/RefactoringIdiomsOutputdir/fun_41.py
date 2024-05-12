def format_body(self, body, mime):
    maybe_json = [
        'json',
        'javascript',
        'text',
    ]
    if (any(token in mime for token in maybe_json) or
            self.kwargs['explicit_json']):
        try:
            obj = json.loads(body)
        except ValueError:
            pass  
        else:
            body = json.dumps(
                obj=obj,
                sort_keys=True,
                ensure_ascii=False,
                indent=DEFAULT_INDENT
            )
    return body
