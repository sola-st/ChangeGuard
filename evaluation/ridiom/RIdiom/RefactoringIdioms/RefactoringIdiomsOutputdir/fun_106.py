def armstrong_number(n):
    if not isinstance(n, int) or n < 1:
        return False
    total , number_of_digits  = 0, 0
    temp = n
    number_of_digits , temp  = len(str(n)), n
    while temp > 0:
        rem = temp % 10
        total += rem**number_of_digits
        temp //= 10
    return n == total
