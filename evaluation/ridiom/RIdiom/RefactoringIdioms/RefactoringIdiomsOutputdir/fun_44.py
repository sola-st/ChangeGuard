def finalize_options(self):
    TestCommand.finalize_options(self)
    self.test_args , self.test_suite  = ['--doctest-modules', '--verbose', './httpie', './tests'], True
