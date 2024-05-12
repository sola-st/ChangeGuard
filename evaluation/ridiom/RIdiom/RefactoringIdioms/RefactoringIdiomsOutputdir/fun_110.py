def euler_phi(n):
    if n <= 0:
        raise ValueError("Only positive numbers are accepted")
    s = n
    for x in set(prime_factors(n)):
        s *= (x - 1) / x
    return int(s)
