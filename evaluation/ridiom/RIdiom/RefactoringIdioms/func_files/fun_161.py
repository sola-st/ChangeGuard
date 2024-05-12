def __init__(
    self,
    vault_conn_id = default_conn_name,
    auth_type = None,
    auth_mount_point = None,
    kv_engine_version = None,
    role_id = None,
    kubernetes_role = None,
    kubernetes_jwt_path = None,
    token_path = None,
    gcp_key_path = None,
    gcp_scopes = None,
    azure_tenant_id = None,
    azure_resource = None,
    radius_host = None,
    radius_port = None,
    **kwargs,
):
    super().__init__()
    self.connection = self.get_connection(vault_conn_id)
    if not auth_type:
        auth_type = self.connection.extra_dejson.get("auth_type") or "token"
    if not auth_mount_point:
        auth_mount_point = self.connection.extra_dejson.get("auth_mount_point")
    if not kv_engine_version:
        conn_version = self.connection.extra_dejson.get("kv_engine_version")
        try:
            kv_engine_version = int(conn_version) if conn_version else DEFAULT_KV_ENGINE_VERSION
        except ValueError:
            raise VaultError(f"The version is not an int: {conn_version}. ")
    client_kwargs = self.connection.extra_dejson.get("client_kwargs", {})
    if kwargs:
        client_kwargs = merge_dicts(client_kwargs, kwargs)
    if auth_type == "approle":
        if role_id:
            warnings.warn(
                """The usage of role_id for AppRole authentication has been deprecated.
                    Please use connection login.""",
                DeprecationWarning,
                stacklevel=2,
            )
        elif self.connection.extra_dejson.get("role_id"):
            role_id = self.connection.extra_dejson.get("role_id")
            warnings.warn(
                """The usage of role_id in connection extra for AppRole authentication has been
                    deprecated. Please use connection login.""",
                DeprecationWarning,
                stacklevel=2,
            )
        elif self.connection.login:
            role_id = self.connection.login
    if auth_type == "aws_iam":
        if not role_id:
            role_id = self.connection.extra_dejson.get("role_id")
    azure_resource, azure_tenant_id = (
        self._get_azure_parameters_from_connection(azure_resource, azure_tenant_id)
        if auth_type == "azure"
        else (None, None)
    )
    gcp_key_path, gcp_keyfile_dict, gcp_scopes = (
        self._get_gcp_parameters_from_connection(gcp_key_path, gcp_scopes)
        if auth_type == "gcp"
        else (None, None, None)
    )
    kubernetes_jwt_path, kubernetes_role = (
        self._get_kubernetes_parameters_from_connection(kubernetes_jwt_path, kubernetes_role)
        if auth_type == "kubernetes"
        else (None, None)
    )
    radius_host, radius_port = (
        self._get_radius_parameters_from_connection(radius_host, radius_port)
        if auth_type == "radius"
        else (None, None)
    )
    key_id = self.connection.extra_dejson.get("key_id")
    if not key_id:
        key_id = self.connection.login
    if self.connection.conn_type == "vault":
        conn_protocol = "http"
    elif self.connection.conn_type == "vaults":
        conn_protocol = "https"
    elif self.connection.conn_type == "http":
        conn_protocol = "http"
    elif self.connection.conn_type == "https":
        conn_protocol = "https"
    else:
        raise VaultError("The url schema must be one of ['http', 'https', 'vault', 'vaults' ]")
    url = f"{conn_protocol}://{self.connection.host}"
    if self.connection.port:
        url += f":{self.connection.port}"
    mount_point = self.connection.schema if self.connection.schema else "secret"
    client_kwargs.update(
        url=url,
        auth_type=auth_type,
        auth_mount_point=auth_mount_point,
        mount_point=mount_point,
        kv_engine_version=kv_engine_version,
        token=self.connection.password,
        token_path=token_path,
        username=self.connection.login,
        password=self.connection.password,
        key_id=self.connection.login,
        secret_id=self.connection.password,
        role_id=role_id,
        kubernetes_role=kubernetes_role,
        kubernetes_jwt_path=kubernetes_jwt_path,
        gcp_key_path=gcp_key_path,
        gcp_keyfile_dict=gcp_keyfile_dict,
        gcp_scopes=gcp_scopes,
        azure_tenant_id=azure_tenant_id,
        azure_resource=azure_resource,
        radius_host=radius_host,
        radius_secret=self.connection.password,
        radius_port=radius_port,
    )
    self.vault_client = _VaultClient(**client_kwargs)
