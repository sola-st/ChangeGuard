def _get_secret(self, path_prefix, secret_id):
    error_msg = "An error occurred when calling the get_secret_value operation"
    if path_prefix:
        secrets_path = self.build_path(path_prefix, secret_id, self.sep)
    else:
        secrets_path = secret_id
    try:
        response = self.client.get_secret_value(
            SecretId=secrets_path,
        )
        return response.get('SecretString')
    except self.client.exceptions.ResourceNotFoundException:
        self.log.debug(
            "ResourceNotFoundException: %s. Secret %s not found.",
            error_msg,
            secret_id,
        )
        return None
    except self.client.exceptions.InvalidParameterException:
        self.log.debug(
            "InvalidParameterException: %s",
            error_msg,
            exc_info=True,
        )
        return None
    except self.client.exceptions.InvalidRequestException:
        self.log.debug(
            "InvalidRequestException: %s",
            error_msg,
            exc_info=True,
        )
        return None
    except self.client.exceptions.DecryptionFailure:
        self.log.debug(
            "DecryptionFailure: %s",
            error_msg,
            exc_info=True,
        )
        return None
    except self.client.exceptions.InternalServiceError:
        self.log.debug(
            "InternalServiceError: %s",
            error_msg,
            exc_info=True,
        )
        return None
