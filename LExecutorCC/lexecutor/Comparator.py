import os
import sys

from lexecutor.Runtime import IntentionalException, kind_and_name_to_value, callable_store
from lexecutor.ValueAbstraction import DummyObject
from lexecutor.Metadata import Metadata

METADATA = Metadata()


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
    for old, new in zip(callable_store[0], callable_store[1]):
        if old != new:
            print(f'potential side effect occurred during 3rd party function call: {old} -- {new}')
            return True
    return False


def compare_return_values(val1, val2):
    if val1 != val2:
        print(f'both functions returned different values: {str(val1)} -- {str(val2)}')
        return True
    print(f'both functions returned same value: {str(val1)}')
    return False
