def load(dataset):
    import csv
    import os
    firis = csv.reader(open(os.path.dirname(__file__) + '/data/%s.csv' % dataset))
    fdescr = open(os.path.dirname(__file__) + '/descr/%s.rst' % dataset)
    temp = firis.next()
    nsamples = int(temp[0])
    nfeat = int(temp[1])
    targetnames = temp[2:]
    data = np.empty((nsamples, nfeat))
    target = np.empty((nsamples,))
    for i, ir in enumerate(firis):
        data[i] = np.asanyarray(ir[:-1], dtype=np.float)
        target[i] = np.asanyarray(ir[-1], dtype=np.float)
    return Bunch(data = data, target=target, targetnames=targetnames, DESCR=fdescr.read())
