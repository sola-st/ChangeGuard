import os
import sys

from lexecutor.Runtime import IntentionalException, kind_and_name_to_value
from lexecutor.ValueAbstraction import DummyObject
from lexecutor.Metadata import Metadata
import copy
global_old_args = {}
global_new_args = {}

METADATA = Metadata()

def different(old_value, new_value):
    # TODO improve comparison
    return old_value != new_value


def compare_exceptions(exception_old, exception_new):
    if exception_old is None and exception_new is None:
        return False
    elif exception_old is None and exception_new is not None:
        print(f'only new function raised exception: {repr(exception_new)}')
    elif exception_old is not None and exception_new is None:
        print(f'only old function raised exception: {repr(exception_old)}')
    elif isinstance(exception_old, AssertionError) and isinstance(exception_new, AssertionError):
        if exception_old.args == exception_new.args:
            print(f'both functions raised same AssertionError: {repr(exception_old)}')
        else:
            print(f'functions raised different AssertionError: {repr(exception_old)} -- {repr(exception_new)}')
    elif isinstance(exception_old, IntentionalException) and isinstance(exception_new, IntentionalException):
        if exception_old.args[1:] == exception_new.args[1:]:
            print(f'both functions raised same IntentionalException: {repr(exception_old)}')
        else:
            print(f'functions raised different IntentionalException: {repr(exception_old)} -- {repr(exception_new)}')
    else:
        print(f'both functions raised unintentional Exception: {repr(exception_old)} -- {repr(exception_new)}')
    return True


def compare_main_args():
    script_path = os.path.abspath(sys.argv[0])
    data = METADATA.get(script_path)
    old_params = data['old_params']
    new_params = data['new_params']
    # only compare parameters that appear in both functions
    params = set(old_params) & set(new_params)
    for param in params:
        key = f'name#{param}'
        if key in kind_and_name_to_value:
            values = kind_and_name_to_value[key]
            if values.old != values.new:
                print(f'functions modified argument {param} differently: {values.old if not isinstance(values.old, DummyObject) else values.old.__dict__} -- {values.new if not isinstance(values.new, DummyObject) else values.new.__dict__}')
                return True
    return False


def compare_args():
    pass


def compare_return_values(val1, val2):
    pass


class Comparator:

    map = {}

    def __init__(self, old_params, new_params, kind_and_name_to_value=None):
        self.old_params = sorted(old_params)
        self.new_params = sorted(new_params)
        if kind_and_name_to_value is not None:
            Comparator.map = kind_and_name_to_value

    def compare_return_values(self, value1, value2):
        pass

    def compare_main_args(self):
        """
        Compares the arguments that are passed to the FUT and checks whether they are still the same after the function
        finished execution (this checks for potential side effects).

        If the number of arguments changes as result of the changes it is viewed as a potential side effect.

        It is assumed that the names of the parameters of the function have not been changed, otherwise it is also viewed
        as a potential side effect.

        Returns: True or False depending on whether the arguments are still equal.

        """
        if len(self.old_params) != len(self.new_params):
            return True

        for old_param, new_param in zip(self.old_params, self.new_params):
            if old_param != new_param:
                return True

        for param in self.old_params:
            values = Comparator.map.get('name#'+param, (None, None))
            if different(values[0], values[1]):
                return True
        return False

    def compare_callable_args(self):
        if len(global_old_args.keys()) != len(global_new_args.keys()):
            return True
        if set(global_old_args.keys()) != set(global_new_args.keys()):
            return True

        for key in global_old_args:
            if different(global_old_args[key], global_new_args[key]):
                return True
        return False


    @staticmethod
    def add_args(fct, args, state):
        if state:
            global_new_args[fct] = copy.deepcopy(args)
        else:
            global_old_args[fct] = copy.deepcopy(args)

