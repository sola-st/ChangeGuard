import numpy as np
import numbers
import _bjst
import logging
from sklearn.preprocessing import normalize

logger = logging.getLogger()

class BJST:
    def __init__(self, n_topics, vocab_size, senti_lex=None, n_senti=3, n_iter=1000, refresh=10, random_state=None, theta=0.5):
        self.n_topics , self.n_iter , self.n_senti , self.vocab_size , self.theta , self.refresh , self.random_state , self.senti_lex , self.B  = n_topics, n_iter, n_senti, vocab_size, theta, refresh, random_state, senti_lex, []

        # random numbers that are reused
        rng = self.check_random_state(random_state)
        self._rands = rng.rand(1024 ** 2 // 8)  # 1MiB of random variates

    def _initialize(self, X):
        B , W , n_senti , n_topics , n_iter  = len(X), self.vocab_size, self.n_senti, self.n_topics, self.n_iter

        logger.info("n_biterms: {}".format(B))
        logger.info("vocab_size: {}".format(W))
        logger.info("n_sentiments: {}".format(n_senti))
        logger.info("n_topics: {}".format(n_topics))
        logger.info("n_iter: {}".format(n_iter))

        self.nlzw , self.nlz , self.nl  = np.zeros((n_senti, n_topics, W), dtype=np.intc), np.zeros((n_senti, n_topics), dtype=np.intc), np.zeros(n_senti, dtype=np.intc)

        self.BS1, self.BS2 = self.matrix_to_lists(X)
        self.ZS, self.LS = np.empty_like(self.BS1, dtype=np.intc), np.empty_like(self.BS1, dtype=np.intc)

        for i in range(B):
            b1, b2 = self.BS1[i], self.BS2[i]
            z_new = i % n_topics
            l_new = i % n_senti
            self.ZS[i] , self.LS[i]  = z_new, l_new
            self.nlzw[l_new, z_new, b1] += 1
            self.nlzw[l_new, z_new, b2] += 1
            self.nlz[l_new, z_new] += 1
            self.nl[l_new] += 1

        self.loglikelihoods_ = []
        print("BJST initialization done!")

    def fit(self, X, alpha=0, beta=0, gamma=0):
        """
        Fit model with X
        :return:
        """
        print("BJST start training...")
        self.init_params(X, alpha, beta, gamma)
        self._fit(X)


    def _fit(self, X):
        random_state , rands  = self.check_random_state(self.random_state), self._rands.copy()
        self._initialize(X)
        for it in range(self.n_iter):
            random_state.shuffle(rands)

            if not it % self.refresh:
                logger.info("Train %d / %d epoch" % (it, self.n_iter))
            #     ll = self.loglikelihood()
            #     logger.info("<{}> log likelihood: {:.0f}".format(it, ll))

            self.sample_(rands)
        # self.ll = self.loglikelihood()
        # logger.info("<{}> log likelihood: {:.0f}".format(self.n_iter - 1, self.ll))
        # compute components
        self.phi_lzw = self.compute_phi_lzw()

        del self.BS1
        del self.BS2
        del self.LS
        del self.ZS
        return self

    def sample_(self, rands):
        """
        Call Cython
        :param rands:
        :return:
        """

        _bjst._sample_topics(self.BS1, self.BS2, self.ZS, self.LS, self.nlzw, self.nlz, self.nl,
                            self.alpha_lz, self.alphaSum_l, self.beta_lzw, self.betaSum_lz,
                            self.gamma, rands)

    def compute_phi_lzw(self):
        phi_lzw = (self.nlzw + self.beta_lzw).astype(float) / (self.nlz + self.betaSum_lz)[:, :, np.newaxis]
        return phi_lzw

    def compute_theta_dlz(self, X_d):
        """
        Compute theta (d*l*z), after computing phi
        :param X_d:
        :return:
        """
        theta_dlz , plz  = np.zeros((len(X_d), self.n_senti, self.n_topics)), self.normalize(self.nlz + self.alpha_lz)
        for i, d_wij in enumerate(X_d):
            tmp = [self.normalize(self.phi_lzw[:, :, wi] * self.phi_lzw[:, :, wj] * plz) for (wi, wj) in d_wij]
            theta_dlz[i, :, :] = np.mean(tmp, axis=0)
        return theta_dlz

    def normalize(self, arr):
        return arr / arr.sum(axis=1, keepdims=True)
    # def print_words(self, prob, n_top_words=10):
    #     for k, beta_k in enumerate(prob):
    #         topic_words = [self.vocab_bow[w_id] for w_id in np.argsort(beta_k)[:-n_top_words - 1:-1]]
    #         yield 'Topic {}: {}'.format(k, ' '.join(x.encode('utf-8') for x in topic_words))

    def loglikelihood(self):
        """
        Compute ppl
        :return:
        """
        pass

    def check_random_state(self, seed):
        if seed is None:
            # i.e., use existing RandomState
            return np.random.mtrand._rand
        if isinstance(seed, (numbers.Integral, np.integer)):
            return np.random.RandomState(seed)
        if isinstance(seed, np.random.RandomState):
            return seed
        raise ValueError("{} cannot be used as a random seed.".format(seed))

    def matrix_to_lists(self, X):
        """Convert a (sparse) matrix of counts into arrays of biterms

        Parameters
        ----------
        X : array or biterms

        Returns
        -------
        BS1 : contains the first word in kth biterm in the corpus
        BS2 : contains the second word in kth biterm in the corpus

        """
        BS1 , BS2  = [], []
        for (bs_0, bs_1, *bs_len) in X:
            BS1.append(bs_0)
            BS2.append(bs_1)
        return np.array(BS1, dtype=np.intc), np.array(BS2, dtype=np.intc)

    def soft_align(self, B, window_size, theta):
        """
        Soft alignment to produce a soft weight sum of B according to window size
        """
        eta = B[-1]
        eta_new , weights  = np.zeros(eta.shape), self.softmax(eta, B, window_size)
        for i in range(window_size):
            if i > len(B)-1:
                break
            B_i = B[-i-1] * weights[i][:, :, np.newaxis]
            eta_new += B_i
        self.beta_lzw = theta * self.beta_lzw + (1 - theta) * eta_new
        self.betaSum_lz = np.sum(self.beta_lzw, 2)

    def softmax(self, eta, B, window_size):
        prods = []
        for i in range(window_size):
            if i > len(B)-1:
                break
            prods.append(np.einsum('ijk,ijk->ij', eta, B[-i-1]))
        weights = np.exp(np.array(prods))
        # weights = np.ones(weights.shape)            # compare to uniform
        n_weights = weights / np.sum(weights, 0)  # column normalize
        return n_weights


    def init_params(self, X, alpha, beta, gamma):
        avg_doc_len = 2
        if not alpha:
            alpha = 50.0 / (self.n_senti * self.n_topics)
        self.alpha_lz = np.full((self.n_senti, self.n_topics), alpha, dtype=np.float64)
        self.alphaSum_l = np.sum(self.alpha_lz, axis=1)
        if not beta:
            self.beta_lzw = np.full((self.n_senti, self.n_topics, self.vocab_size), 0.01, dtype=np.float64)
        else:
            self.beta_lzw = np.full((self.n_senti, self.n_topics, self.vocab_size), beta, dtype=np.float64)
        for wid, pl in self.senti_lex.items():
            if pl == 1: # pos
                self.beta_lzw[:,:, wid] *= np.array([0.05, 0.9, 0.05])[:, np.newaxis]
            elif pl == -1:  # neg
                self.beta_lzw[:,:, wid] *= np.array([0.05, 0.05, 0.9])[:, np.newaxis]
        self.betaSum_lz , self.gamma  = np.sum(self.beta_lzw, axis=2), gamma
        if not gamma:
            self.gamma = 50.0 / self.n_senti
        print("hello")
