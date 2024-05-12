def format_body(self, body, mime):
    maybe_json = [
        'json',
        'javascript',
        'text',
    ]
    if (self.kwargs['explicit_json'] or
            any(token in mime for token in maybe_json)):
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
