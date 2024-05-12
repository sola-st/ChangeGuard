def check_correctness_of_list_of_sensors_operators_hook_trigger_modules(
    yaml_files
):
    num_errors = 0
    num_modules = 0
    for (yaml_file_path, provider_data), resource_type in itertools.product(
        yaml_files.items(), ["sensors", "operators", "hooks", "triggers"]
    ):
        expected_modules, provider_package, resource_data = parse_module_data(
            provider_data, resource_type, yaml_file_path
        )
        expected_modules = {module for module in expected_modules if module not in DEPRECATED_MODULES}
        current_modules = {str(i) for r in resource_data for i in r.get("python-modules", [])}
        num_modules += len(current_modules)
        num_errors += check_if_objects_exist_and_belong_to_package(
            current_modules, provider_package, yaml_file_path, resource_type, ObjectType.MODULE
        )
        try:
            package_name = os.fspath(ROOT_DIR.joinpath(yaml_file_path).parent.relative_to(ROOT_DIR)).replace(
                "/", "."
            )
            assert_sets_equal(
                set(expected_modules),
                f"Found list of {resource_type} modules in provider package: {package_name}",
                set(current_modules),
                f"Currently configured list of {resource_type} modules in {yaml_file_path}",
                extra_message="[yellow]Additional check[/]: If there are deprecated modules in the list,"
                "please add them to DEPRECATED_MODULES in "
                f"{pathlib.Path(__file__).relative_to(ROOT_DIR)}",
            )
        except AssertionError as ex:
            nested_error = textwrap.indent(str(ex), "  ")
            errors.append(
                f"Incorrect content of key '{resource_type}/python-modules' "
                f"in file: {yaml_file_path}\n{nested_error}"
            )
            num_errors += 1
    return num_modules, num_errors
