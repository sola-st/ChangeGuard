def get_dependant(
    *,
    path,
    call,
    name = None,
    security_scopes = None,
    use_cache = True,
):
    path_param_names = get_path_param_names(path)
    endpoint_signature = get_typed_signature(call)
    signature_params = endpoint_signature.parameters
    dependant = Dependant(
        call=call,
        name=name,
        path=path,
        security_scopes=security_scopes,
        use_cache=use_cache,
    )
    for param_name, param in signature_params.items():
        if isinstance(param.default, params.Depends):
            sub_dependant = get_param_sub_dependant(
                param=param, path=path, security_scopes=security_scopes
            )
            dependant.dependencies.append(sub_dependant)
            continue
        if add_non_field_param_to_dependency(param=param, dependant=dependant):
            continue
        param_field = get_param_field(
            param=param, default_field_info=params.Query, param_name=param_name
        )
        if param_name in path_param_names:
            assert is_scalar_field(
                field=param_field
            ), "Path params must be of one of the supported types"
            ignore_default = not isinstance(param.default, params.Path)
            param_field = get_param_field(
                param=param,
                param_name=param_name,
                default_field_info=params.Path,
                force_type=params.ParamTypes.path,
                ignore_default=ignore_default,
            )
            add_param_to_fields(field=param_field, dependant=dependant)
        elif is_scalar_field(field=param_field):
            add_param_to_fields(field=param_field, dependant=dependant)
        elif isinstance(
            param.default, (params.Query, params.Header)
        ) and is_scalar_sequence_field(param_field):
            add_param_to_fields(field=param_field, dependant=dependant)
        else:
            field_info = param_field.field_info
            assert isinstance(
                field_info, params.Body
            ), f"Param: {param_field.name} can only be a request body, using Body()"
            dependant.body_params.append(param_field)
    return dependant
