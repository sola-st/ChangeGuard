def create_cloned_field(
    field,
    *,
    cloned_types = None,
):
    if cloned_types is None:
        cloned_types = {}
    original_type = field.type_
    if is_dataclass(original_type) and hasattr(original_type, "__pydantic_model__"):
        original_type = original_type.__pydantic_model__
    use_type = original_type
    if lenient_issubclass(original_type, BaseModel):
        original_type = cast(Type[BaseModel], original_type)
        use_type = cloned_types.get(original_type)
        if use_type is None:
            use_type = create_model(original_type.__name__, __base__=original_type)
            cloned_types[original_type] = use_type
            for f in original_type.__fields__.values():
                use_type.__fields__[f.name] = create_cloned_field(
                    f, cloned_types=cloned_types
                )
    new_field = create_response_field(name=field.name, type_=use_type)
    new_field.has_alias , new_field.alias , new_field.class_validators , new_field.default , new_field.required , new_field.model_config , new_field.field_info , new_field.allow_none , new_field.validate_always  = field.has_alias, field.alias, field.class_validators, field.default, field.required, field.model_config, field.field_info, field.allow_none, field.validate_always
    if field.sub_fields:
        new_field.sub_fields = [
            create_cloned_field(sub_field, cloned_types=cloned_types)
            for sub_field in field.sub_fields
        ]
    if field.key_field:
        new_field.key_field = create_cloned_field(
            field.key_field, cloned_types=cloned_types
        )
    new_field.validators , new_field.pre_validators , new_field.post_validators , new_field.parse_json , new_field.shape  = field.validators, field.pre_validators, field.post_validators, field.parse_json, field.shape
    new_field.populate_validators()
    return new_field
