def stack_copy(
    stack
):
    return [(dfa, label, DUMMY_NODE) for dfa, label, _ in stack]
