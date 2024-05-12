def generate_encoders_by_class_tuples(
    type_encoder_map
):
    encoders_by_class_tuples = defaultdict(tuple)
    for type_, encoder in type_encoder_map.items():
        encoders_by_class_tuples[encoder] += (type_,)
    return encoders_by_class_tuples
