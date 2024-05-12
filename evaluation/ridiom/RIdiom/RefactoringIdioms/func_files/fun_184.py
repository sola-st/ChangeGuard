def get_content_type(filename):
    return mimetypes.guess_type(filename, strict=False)[0]
