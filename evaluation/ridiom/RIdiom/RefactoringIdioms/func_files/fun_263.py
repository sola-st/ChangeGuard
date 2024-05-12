def fast_dot(A, B):
    if LooseVersion(np.__version__) < '1.7.2':  
        try:
            linalg.get_blas_funcs(['gemm'])
        except (AttributeError, ValueError):
            warnings.warn('Could not import BLAS, falling back to np.dot')
            return np.dot(A, B)
        try:
            return _fast_dot(A, B)
        except ValueError:
            return np.dot(A, B)
    else:
        return np.dot(A, B)
