def validate_object(obj):
    schema_file = Path(SCHEMA_DIR, "poetry.json")
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)
    validation_errors = sorted(
        validator.iter_errors(obj),
        key=lambda e: e.path,  
    )
    errors = []
    for error in validation_errors:
        message = error.message
        if error.path:
            path = ".".join(str(x) for x in error.absolute_path)
            message = f"[{path}] {message}"
        errors.append(message)
    core_schema = json.loads(
        Path(CORE_SCHEMA_DIR, "poetry-schema.json").read_text(encoding="utf-8")
    )
    properties = {*schema["properties"].keys(), *core_schema["properties"].keys()}
    additional_properties = set(obj.keys()) - properties
    for key in additional_properties:
        errors.append(f"Additional properties are not allowed ('{key}' was unexpected)")
    return errors
