def coulombs_law(q1, q2, radius):
    if radius <= 0:
        raise ValueError("The radius is always a positive number")
    return round(((8.9875517923 * 10**9) * q1 * q2) / (radius**2), 2)
