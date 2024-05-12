def binary_exponentiation(a, n):
    if not n:
        return 1
    elif n % 2 == 1:
        return binary_exponentiation(a, n - 1) * a
    else:
        b = binary_exponentiation(a, n // 2)
        return b * b
