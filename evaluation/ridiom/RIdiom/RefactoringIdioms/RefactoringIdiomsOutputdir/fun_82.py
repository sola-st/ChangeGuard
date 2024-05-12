def setup(self):
    N = 5000
    self.left , self.right  = DataFrame(np.random.randint(1, N / 50, (N, 2)), columns=['jim', 'joe']), DataFrame(np.random.randint(1, N / 50, (N, 2)), columns=['jolie', 'jolia']).set_index('jolie')
