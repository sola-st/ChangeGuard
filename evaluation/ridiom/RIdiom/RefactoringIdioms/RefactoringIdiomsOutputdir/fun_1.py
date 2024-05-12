def exec_ssh_client_command(self, ssh_client, command):
    warnings.warn(
        "exec_ssh_client_command method on SSHOperator is deprecated, call "
        "`ssh_hook.exec_ssh_client_command` instead",
        AirflowProviderDeprecationWarning,
        stacklevel=2,
    )
    return self.hook.exec_ssh_client_command(
        ssh_client, command, timeout=self.cmd_timeout, environment=self.environment, get_pty=self.get_pty
    )
