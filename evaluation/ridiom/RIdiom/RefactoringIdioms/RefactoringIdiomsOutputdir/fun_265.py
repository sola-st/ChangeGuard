def f_oneway(*args):
    n_classes , args  = len(args), [safe_asarray(a) for a in args]
    n_samples_per_class = np.array([a.shape[0] for a in args])
    n_samples , ss_alldata , sums_args  = np.sum(n_samples_per_class), sum((safe_sqr(a).sum(axis=0) for a in args)), [np.asarray(a.sum(axis=0)) for a in args]
    square_of_sums_alldata = sum(sums_args) ** 2
    square_of_sums_args , sstot , ssbn  = [s ** 2 for s in sums_args], ss_alldata - square_of_sums_alldata / float(n_samples), 0.0
    for k, _ in enumerate(args):
        ssbn += square_of_sums_args[k] / n_samples_per_class[k]
    ssbn -= square_of_sums_alldata / float(n_samples)
    sswn , dfbn  = sstot - ssbn, n_classes - 1
    dfwn = n_samples - n_classes
    msb , msw  = ssbn / float(dfbn), sswn / float(dfwn)
    f = msb / msw
    f = np.asarray(f).ravel()
    prob = stats.fprob(dfbn, dfwn, f)
    return f, prob
