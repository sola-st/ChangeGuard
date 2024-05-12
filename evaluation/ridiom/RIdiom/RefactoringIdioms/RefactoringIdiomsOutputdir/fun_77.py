def warn_alias_replacement(
    obj,
    func,
    alias,
):
    if alias.startswith("np."):
        full_alias = alias
    else:
        full_alias , alias  = f'{type(obj).__name__}.{alias}', f'"{alias}"'
    warnings.warn(
        f"The provided callable {func} is currently using "
        f"{full_alias}. In a future version of pandas, "
        f"the provided callable will be used directly. To keep current "
        f"behavior pass the string {alias} instead.",
        category=FutureWarning,
        stacklevel=find_stack_level(),
    )
