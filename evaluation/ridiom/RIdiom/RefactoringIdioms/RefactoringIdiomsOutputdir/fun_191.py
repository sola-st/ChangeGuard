async def __call__(  
    self, request
):
    authorization = request.headers.get("Authorization")
    scheme, param = get_authorization_scheme_param(authorization)
    if self.realm:
        unauthorized_headers = {"WWW-Authenticate": f'Basic realm="{self.realm}"'}
    else:
        unauthorized_headers = {"WWW-Authenticate": "Basic"}
    if not authorization or scheme.lower() != "basic":
        if self.auto_error:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers=unauthorized_headers,
            )
        else:
            return None
    invalid_user_credentials_exc = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers=unauthorized_headers,
    )
    try:
        data = b64decode(param).decode("ascii")
    except (ValueError, UnicodeDecodeError, binascii.Error):
        raise invalid_user_credentials_exc
    username, separator, password = data.partition(":")
    if not separator:
        raise invalid_user_credentials_exc
    return HTTPBasicCredentials(username=username, password=password)
