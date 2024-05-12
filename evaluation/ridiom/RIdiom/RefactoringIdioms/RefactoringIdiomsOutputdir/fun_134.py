def check_classification_targets(y):
    y_type = type_of_target(y, input_name="y")
    if y_type not in [
        "binary",
        "multiclass",
        "multiclass-multioutput",
        "multilabel-indicator",
        "multilabel-sequences",
    ]:
        raise ValueError(
            f"Unknown label type: {y_type}. Maybe you are trying to fit a "
            "classifier, which expects discrete classes on a "
            "regression target with continuous values."
        )
