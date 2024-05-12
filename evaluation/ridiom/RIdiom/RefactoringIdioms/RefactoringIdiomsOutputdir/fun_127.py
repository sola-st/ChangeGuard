def check_conda_version():
    conda_info_output = execute_command(["conda", "info", "--json"])
    conda_info = json.loads(conda_info_output)
    conda_version = Version(conda_info["conda_version"])
    if Version("22.9.0") < conda_version < Version("23.7"):
        raise RuntimeError(
            f"conda version should be <= 22.9.0 or >= 23.7 got: {conda_version}"
        )
