def __init__(
    self,
    uri,
    access_key=None,
    secret_key=None,
    acl=None,
    endpoint_url=None,
    *,
    feed_options=None,
    session_token=None,
    region_name=None,
):
    if not is_botocore_available():
        raise NotConfigured("missing botocore library")
    u = urlparse(uri)
    self.bucketname , self.access_key , self.secret_key , self.session_token , self.keyname , self.acl , self.endpoint_url , self.region_name  = u.hostname, u.username or access_key, u.password or secret_key, session_token, u.path[1:], acl, endpoint_url, region_name
    if IS_BOTO3_AVAILABLE:
        import boto3.session
        session = boto3.session.Session()
        self.s3_client = session.client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            aws_session_token=self.session_token,
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
        )
    else:
        warnings.warn(
            "`botocore` usage has been deprecated for S3 feed "
            "export, please use `boto3` to avoid problems",
            category=ScrapyDeprecationWarning,
        )
        import botocore.session
        session = botocore.session.get_session()
        self.s3_client = session.create_client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            aws_session_token=self.session_token,
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
        )
    if feed_options and feed_options.get("overwrite", True) is False:
        logger.warning(
            "S3 does not support appending to files. To "
            "suppress this warning, remove the overwrite "
            "option from your FEEDS setting or set it to True."
        )
