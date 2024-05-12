def load(dataset):
    import csv
    import os
    firis = csv.reader(open(os.path.dirname(__file__) + '/data/%s.csv' % dataset))
    fdescr , temp  = open(os.path.dirname(__file__) + '/descr/%s.rst' % dataset), firis.next()
    nsamples , nfeat  = int(temp[0]), int(temp[1])
    targetnames , data , target  = temp[2:], np.empty((nsamples, nfeat)), np.empty((nsamples,))
    for i, ir in enumerate(firis):
        data[i] , target[i]  = np.asanyarray(ir[:-1], dtype=np.float), np.asanyarray(ir[-1], dtype=np.float)
    return Bunch(data = data, target=target, targetnames=targetnames, DESCR=fdescr.read())
