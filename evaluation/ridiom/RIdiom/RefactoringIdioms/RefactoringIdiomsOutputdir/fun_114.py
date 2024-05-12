def bin_exp_mod(a, n, b):
    assert b, "This cannot accept modulo that is == 0"
    if not n:
        return 1
    if n % 2 == 1:
        return (bin_exp_mod(a, n - 1, b) * a) % b
    r = bin_exp_mod(a, n // 2, b)
    return (r * r) % b
