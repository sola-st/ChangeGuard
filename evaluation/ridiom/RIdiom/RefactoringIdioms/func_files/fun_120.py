def _unique_indicator(y):
    xp, _ = get_namespace(y)
    return xp.arange(
        check_array(y, input_name="y", accept_sparse=["csr", "csc", "coo"]).shape[1]
    )
