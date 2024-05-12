def retroactive_resolution(
    coefficients, vector
):
    rows, columns = np.shape(coefficients)
    x = np.zeros((rows, 1), dtype=float)
    for row in reversed(range(rows)):
        total = np.dot(coefficients[row, row + 1 :], x[row + 1 :])
        x[row, 0] = (vector[row] - total) / coefficients[row, row]
    return x
