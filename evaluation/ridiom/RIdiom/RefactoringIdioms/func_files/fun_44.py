def finalize_options(self):
    TestCommand.finalize_options(self)
    self.test_args = [
        '--doctest-modules', '--verbose',
        './httpie', './tests'
    ]
    self.test_suite = True
