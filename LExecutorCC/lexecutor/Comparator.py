import os
import sys
import inspect
import asyncio

from lexecutor.Runtime import IntentionalException, kind_and_name_to_value, callable_store
from lexecutor.ValueAbstraction import DummyObject
from lexecutor.Metadata import Metadata

METADATA = Metadata()


def _get_value_repr(val):
    return val.repr_without_internals() if isinstance(val, DummyObject) else repr(val)


async def __handle_async_gen(async_gen):
    return [x async for x in async_gen]


def unwrap_return_value(value):
    if inspect.isgenerator(value):
        return list(value)
    if inspect.iscoroutine(value):
        return asyncio.run(value)
    if inspect.isasyncgen(value):
        return asyncio.run(__handle_async_gen(value))
    if callable(value) and not isinstance(value, DummyObject):
        return value()
    return value


def compare_exceptions(exception_old, exception_new):
    if exception_old is None and exception_new is None:
        return False
    elif exception_old is None and exception_new is not None:
        if issubclass(type(exception_new), IntentionalException) or isinstance(exception_new, AssertionError):
            print(f'only new function raised intentional exception: {repr(exception_new)}')
        else:
            print(f'only new function raised unintentional exception: {repr(exception_new)}')
    elif exception_old is not None and exception_new is None:
        if issubclass(type(exception_old), IntentionalException) or isinstance(exception_old, AssertionError):
            print(f'only old function raised intentional exception: {repr(exception_old)}')
        else:
            print(f'only old function raised unintentional exception: {repr(exception_old)}')
    elif isinstance(exception_old, AssertionError) and isinstance(exception_new, AssertionError):
        if exception_old.args == exception_new.args:
            print(f'both functions raised same AssertionError: {repr(exception_old)}')
        else:
            print(f'functions raised different AssertionError: {repr(exception_old)} -- {repr(exception_new)}')
    elif issubclass(type(exception_old), IntentionalException) and issubclass(type(exception_new), IntentionalException):
        if exception_old.args == exception_new.args:
            print(f'both functions raised same IntentionalException: {repr(exception_old)}')
        else:
            print(f'functions raised different IntentionalException: {repr(exception_old)} -- {repr(exception_new)}')
    else:
        print(f'both functions raised unintentional exception: {repr(exception_old)} -- {repr(exception_new)}')
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
                print(f'functions modified argument {param} differently: {_get_value_repr(values.old)} -- {_get_value_repr(values.new)}')
                return True
    return False


def compare_args():
    if len(callable_store[0]) != len(callable_store[1]):
        print('number of 3rd party function calls changed')
        return True
    for old, new in zip(callable_store[0], callable_store[1]):
        if old != new:
            print(f'potential side effect occurred during 3rd party function call: {_get_value_repr(old)} -- {_get_value_repr(new)}')
            return True
    return False


def compare_stdout(old, new):
    if old != new:
        print(f'stdout is different between functions: {old} -- {new}')
        return True
    return False


def compare_stderr(old, new):
    if old != new:
        print(f'stderr is different between functions: {old} -- {new}')
        return True
    return False


def compare_return_values(val1, val2):
    if val1 != val2:
        print(f'both functions returned different values: {_get_value_repr(val1)} -- {_get_value_repr(val2)}')
        return True
    print(f'both functions returned same value: {_get_value_repr(val1)}')
    return False
