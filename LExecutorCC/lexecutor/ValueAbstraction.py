import random
import copy
import types
from collections import namedtuple


from .Logging import get_logger
from .Metadata import Metadata
from .Hyperparams import Hyperparams as params

logger = get_logger(__name__)

INTEGER_OPTIONS = [-100, -10, -1, 0, 1, 10, 100]
FLOAT_OPTIONS = [-100.0, -10.0, -1.0, 0.0, 1.0, 10.0, 100.0]
STR_OPTIONS = ["", "a"]

Values = namedtuple('Values', 'old new')

metadata = Metadata()
script_meta = metadata.get_data_for_current_script()
if script_meta is not None:
    INTEGER_OPTIONS.extend(script_meta['integer_literals'])
    FLOAT_OPTIONS.extend(script_meta['float_literals'])
    STR_OPTIONS.extend(script_meta['string_literals'])


def _get_random_integer():
    return random.choice(INTEGER_OPTIONS)


def _get_random_float():
    return random.choice(FLOAT_OPTIONS)


def _get_random_str():
    return random.choice(STR_OPTIONS)


def _get_random_bool():
    return random.choice([True, False])


def _get_random_tuple():
    size = random.randint(0, 4)
    _type = random.choices([DummyObject, _get_random_integer,  _get_random_str, _get_random_float, _get_random_bool, lambda: None], cum_weights=[50, 65, 80, 92, 97, 100])[0]
    return tuple(_type() for _ in range(size))


def _get_random_list(include_dummy=True):
    size = random.randint(0, 4)
    if include_dummy:
        _type = random.choices([DummyObject, _get_random_integer,  _get_random_str, _get_random_float, _get_random_bool, lambda: None], cum_weights=[50, 65, 80, 92, 97, 100])[0]
    else:
        _type = random.choices([_get_random_integer,  _get_random_str, _get_random_float, _get_random_bool, lambda: None], cum_weights=[30, 60, 85, 95, 100])[0]
    return [_type() for _ in range(size)]


def _get_random_sets():
    size = random.randint(0, 1)
    _type = random.choices([DummyObject, _get_random_integer,  _get_random_str, _get_random_float, _get_random_bool, lambda: None], cum_weights=[50, 65, 80, 92, 97, 100])[0]
    return {_type() for _ in range(size)}


def abstract_value(value):
    t = type(value)
    # common primitive values
    if value is None:
        abstract_value = "@None"
    elif value is True:
        abstract_value = "@True"
    elif value is False:
        abstract_value = "@False"
    # strings
    elif t is str:
        if len(value) == 0:
            abstract_value = "@str_empty"
        else:
            abstract_value = "@str_nonempty"
    # built-in numeric types
    elif t is int:
        if value < 0:
            abstract_value = "@int_neg"
        elif value == 0:
            abstract_value = "@int_zero"
        else:
            abstract_value = "@int_pos"
    elif t is float:
        if value < 0:
            abstract_value = "@float_neg"
        elif value == 0:
            abstract_value = "@float_zero"
        else:
            abstract_value = "@float_pos"
    # built-in sequence types
    elif t is list:
        if len(value) == 0:
            abstract_value = "@list_empty"
        else:
            abstract_value = "@list_nonempty"
    elif t is tuple:
        if len(value) == 0:
            abstract_value = "@tuple_empty"
        else:
            abstract_value = "@tuple_nonempty"
    # built-in set and dict types
    elif t is set:
        if len(value) == 0:
            abstract_value = "@set_empty"
        else:
            abstract_value = "@set_nonempty"
    elif t is dict:
        if len(value) == 0:
            abstract_value = "@dict_empty"
        else:
            abstract_value = "@dict_nonempty"
    # functions and methods
    elif callable(value):
        if hasattr(value, "__enter__") and hasattr(value, "__exit__"):
            abstract_value = "@resource"
        else:
            abstract_value = "@callable"
    # all other types
    else:
        abstract_value = "@object"

    return abstract_value, str(t)[:20]


# class DummyResource(object):
#     def __enter__(self):
#         return self
#
#     def __exit__(self, exc_type, exc_value, trace):
#         return True
#
#     def __repr__(self):
#         return "DummyResource"
#
#     def __eq__(self, other):
#         return isinstance(other, DummyResource)
#
#
#     def __call__(self, *args, **kwargs):
#         return DummyObject()


class DummyObject(Exception):

    id_counter = 0
    seen_ids = []
    __internal_attributes = ['id', 'iterable', 'dict', 'int', 'float', 'str', 'bool', 'pass_instance_check']
    __comparing = False

    def __init__(self, *a, **b):
        self.iterable = _get_random_list(include_dummy=False)
        self.dict = {}
        self.int = _get_random_integer()
        self.float = _get_random_float()
        self.str = _get_random_str()
        self.bool = _get_random_bool()
        self.pass_instance_check = random.choice([True, False])
        self.id = DummyObject.id_counter
        DummyObject.id_counter += 1

    def repr_without_internals(self):
        DummyObject.__comparing = True
        DummyObject.seen_ids = [self.id]
        self_repr = repr({k: v for k, v in self.__dict__.items() if k not in DummyObject.__internal_attributes})
        DummyObject.seen_ids = []
        DummyObject.__comparing = False
        return self_repr

    def __operation(self, other, operator, right=False):
        if isinstance(other, int):
            if right:
                return eval(f"{other} {operator} {self.int}")
            return eval(f"{self.int} {operator} {other}")
        if isinstance(other, float):
            if right:
                return eval(f"{other} {operator} {self.float}")
            return eval(f"{self.float} {operator} {other}")
        if isinstance(other, complex):
            if right:
                return eval(f"{other} {operator} {complex(self.int)}")
            return eval(f"{complex(self.int)} {operator} {other}")
        if isinstance(other, bool):
            if right:
                return eval(f"{other} {operator} {self.bool}")
            return eval(f"{self.bool} {operator} {other}")
        if isinstance(other, str):
            if right:
                return eval(f"'{other}' {operator} '{self.str}'")
            return eval(f"'{self.str}' {operator} '{other}'")
        return False

    def __abs__(self):
        return abs(self.int)

    def __add__(self, other):
        return self.__operation(other, "+")

    # def __aenter__(self):
    #     pass  # TODO / REMOVE

    # def __aexit__(self, exc_type, exc_val, exc_tb):
    #     pass  # TODO / REMOVE

    # def __aiter__(self):
    #     pass  # TODO / REMOVE

    def __and__(self, other):
        return self.__operation(other, "and")

    # def __anext__(self):
    #     pass  # TODO / REMOVE

    # def __await__(self):
    #     pass  # TODO / REMOVE

    def __bool__(self):
        return self.bool

    def __bytes__(self):
        return bytes(self.str, "utf-8")

    def __call__(self, *args, **kwargs):
        return DummyObject()

    # def __ceil__(self):
    #     pass

    def __complex__(self):
        return complex(self.int)

    def __contains__(self, item):
        if isinstance(item, int):
            return item in self.iterable
        else:
            return item in self.dict


    # def __del__(self):
    #     pass  # TODO / REMOVE

    # def __delattr__(self, item):
    #     pass  # TODO / REMOVE

    # def __delete__(self, instance):
    #     pass  # TODO / REMOVE

    # def __delitem__(self, key):
    #     pass  # TODO

    # def __dir__(self):
    #     pass

    def __divmod__(self, other):
        return self.__operation(other, "//"), self.__operation(other, "%")

    def __enter__(self):
        return self

    def __eq__(self, other):
        if not isinstance(other, DummyObject):
            return self.__operation(other, "==")

        def serialize(obj):
            return repr(sorted(map(lambda x: (x[0], x[1]) if not isinstance(x[1], types.FunctionType) else (x[0], x[1].__code__.co_name), [(k, v) for k, v in obj.__dict__.items() if k not in DummyObject.__internal_attributes]), key=lambda x: x[0]))

        DummyObject.__comparing = True
        DummyObject.seen_ids = [self.id, other.id]
        serialized_self = serialize(self)
        DummyObject.seen_ids = [self.id, other.id]
        serialized_other = serialize(other)
        DummyObject.seen_ids = []  # reset list
        DummyObject.__comparing = False
        return serialized_self == serialized_other

    def __exit__(self, exc_type, exc_value, trace):
        return True

    def __float__(self):
        return self.float

    # def __floor__(self):
    #     pass  # REMOVE

    def __floordiv__(self, other):
        return self.__operation(other, "//")

    # def __format__(self, format_spec):
    #     pass  # REMOVE

    def __ge__(self, other):
        return self.__operation(other, ">=")

    # def __get__(self, instance, owner):
    #     pass  # TODO

    # def __getattr__(self, item):
    #     pass  # TODO

    # def __getattribute__(self, item):
    #     pass  # TODO

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.iterable[item]
        else:
            return self.dict[item]

    def __gt__(self, other):
        return self.__operation(other, ">")

    def __hash__(self):
        return hash(f"DummyObject{self.id}")

    def __iadd__(self, other):
        return self.__operation(other, "+")

    def __iand__(self, other):
        return self.__operation(other, "and")

    def __idiv__(self, other):
        return self.__operation(other, "/")

    def __ifloordiv__(self, other):
        return self.__operation(other, "//")

    def __ilshift__(self, other):
        return self.__operation(other, "<<")

    def __imatmul__(self, other):
        return self.__operation(other, "@")

    def __imod__(self, other):
        return self.__operation(other, "%")

    def __imul__(self, other):
        return self.__operation(other, "*")

    def __index__(self):
        return self.int

    # def __init_subclass__(cls, **kwargs):
    #     pass  # REMOVE

    # def __instancecheck__(self, instance):
    #     pass  # TODO!

    def __int__(self):
        return self.int

    def __invert__(self):
        return ~self.int

    def __ior__(self, other):
        return self.__operation(other, "or")

    def __ipow__(self, other):
        pass  # TODO

    def __irshift__(self, other):
        return self.__operation(other, ">>")

    def __isub__(self, other):
        return self.__operation(other, "-")

    def __iter__(self):
        return iter(self.iterable)

    def __itruediv__(self, other):
        return self.__operation(other, "/")

    def __ixor__(self, other):
        return self.__operation(other, "^")

    def __le__(self, other):
        return self.__operation(other, "<=")

    def __len__(self):
        return len(self.iterable)

    def __lshift__(self, other):
        return self.__operation(other, "<<")

    def __lt__(self, other):
        return self.__operation(other, "<")

    def __matmul__(self, other):
        return self.__operation(other, "@")

    # def __missing__(self, key):
    #     pass  # REMOVE?

    def __mod__(self, other):
        return self.__operation(other, "%")

    def __mul__(self, other):
        return self.__operation(other, "*")

    # def __ne__(self, other): implicitly defined by __eq__
    #     pass

    def __neg__(self):
        return -self.int

    # def __new__(cls, *args, **kwargs):
    #     pass

    # def __next__(self):
    #     pass  # TODO

    def __or__(self, other):
        return self.__operation(other, "or")

    def __pos__(self):
        return +self.int

    def __pow__(self, power, modulo=None):
        pass  # TODO

    def __radd__(self, other):
        return self.__operation(other, "+", right=True)

    def __rand__(self, other):
        return self.__operation(other, "and", right=True)

    def __rdiv__(self, other):
        return self.__operation(other, "/", right=True)

    def __rdivmod__(self, other):
        return self.__operation(other, "//"), self.__operation(other, "%")

    def __repr__(self):
        if not DummyObject.__comparing or self.id in DummyObject.seen_ids:
            return f"Dummy#{self.id}"
        else:
            DummyObject.seen_ids.append(self.id)
            return repr({k: v for k, v in self.__dict__.items() if k not in DummyObject.__internal_attributes})

    def __reversed__(self):
        return reversed(self.iterable)

    def __rfloordiv__(self, other):
        return self.__operation(other, "//", right=True)

    def __rlshift__(self, other):
        return self.__operation(other, "<<", right=True)

    def __rmatmul__(self, other):
        return self.__operation(other, "@", right=True)

    def __rmod__(self, other):
        return self.__operation(other, "%", right=True)

    def __rmul__(self, other):
        return self.__operation(other, "*", right=True)

    def __ror__(self, other):
        return self.__operation(other, "or", right=True)

    # def __round__(self, n=None):
    #     pass  # REMOVE

    def __rpow__(self, other):
        pass  # TODO

    def __rrshift__(self, other):
        return self.__operation(other, ">>", right=True)

    def __rshift__(self, other):
        return self.__operation(other, ">>", right=True)

    def __rsub__(self, other):
        return self.__operation(other, "-", right=True)

    def __rtruediv__(self, other):
        return self.__operation(other, "/", right=True)

    def __rxor__(self, other):
        return self.__operation(other, "^", right=True)

    # def __set__(self, instance, value):
    #     pass  # TODO

    # def __set_name__(self, owner, name):
    #     pass  # TODO

    # def __setattr__(self, key, value):
    #     pass  # TODO

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.iterable.insert(key, value)
        else:
            self.dict[key] = value

    # def __sizeof__(self):
    #     pass  # REMOVE

    def __str__(self):
        return f"Dummy#{self.id}"

    def __sub__(self, other):
        return self.__operation(other, "-")

    # def __subclasscheck__(self, subclass):
    #     pass  # TODO

    def __truediv__(self, other):
        return self.__operation(other, "/")

    # def __trunc__(self):
    #     pass  # REMOVE

    def __xor__(self, other):
        return self.__operation(other, "^")

    def __copy__(self):
        pass  # TODO

    def __fspath__(self):
        return self.str


fine_to_coarse_grained = {
    "@None": "@None",
    "@True": "@bool",
    "@False": "@bool",
    "@str_empty": "@str",
    "@str_nonempty": "@str",
    "@int_neg": "@int",
    "@int_zero": "@int",
    "@int_pos": "@int",
    "@float_neg": "@float",
    "@float_zero": "@float",
    "@float_pos": "@float",
    "@list_empty": "@list",
    "@list_nonempty": "@list",
    "@tuple_empty": "@tuple",
    "@tuple_nonempty": "@tuple",
    "@set_empty": "@set",
    "@set_nonempty": "@set",
    "@dict_empty": "@dict",
    "@dict_nonempty": "@dict",
    "@resource": "@resource",
    "@callable": "@callable",
    "@object": "@object",
}


def get_value_pairs(value):
    return Values(value, copy.deepcopy(value))


if params.value_abstraction.startswith("coarse-grained"):
    if params.value_abstraction == "coarse-grained-deterministic":
        def restore_value(abstract_value):
            # common primitive values
            if abstract_value == "None":
                return None
            elif abstract_value == "bool":
                return True
            # strings
            elif abstract_value == "str":
                return "a"
            # built-in numeric types
            elif abstract_value == "int":
                return 1
            elif abstract_value == "float":
                return 1.0
            # built-in sequence types
            elif abstract_value == "list":
                return [DummyObject()]
            elif abstract_value == "tuple":
                return (DummyObject(),)
            # built-in set and dict types
            elif abstract_value == "set":
                return {DummyObject()}
            elif abstract_value == "dict":
                return {"a": DummyObject()}
            # functions and methods
            elif abstract_value == "resource":
                return DummyObject()
            elif abstract_value == "callable":
                return DummyObject
            elif abstract_value == "object":
                return DummyObject()
            # all other types
            else:
                logger.info("Unknown abstract value: %s", abstract_value)
                return DummyObject()
    elif params.value_abstraction == "coarse-grained-randomized":
        def restore_value(abstract_value):
            # common primitive values
            if abstract_value == "None":
                return get_value_pairs(None)
            elif abstract_value == "bool":
                return get_value_pairs(_get_random_bool())
            # strings
            elif abstract_value == "str":
                return get_value_pairs(_get_random_str())
            # built-in numeric types
            elif abstract_value == "int":
                return get_value_pairs(_get_random_integer())
            elif abstract_value == "float":
                return get_value_pairs(_get_random_float())
            # built-in sequence types
            elif abstract_value == "list":
                return get_value_pairs(_get_random_list())
            elif abstract_value == "tuple":
                return get_value_pairs(_get_random_tuple())
            # built-in set and dict types
            elif abstract_value == "set":
                return get_value_pairs(_get_random_sets())
            elif abstract_value == "dict":
                return get_value_pairs(random.choice([{}, {"a": DummyObject()}]))
            # functions and methods
            elif abstract_value == "resource":
                return get_value_pairs(DummyObject())
            elif abstract_value == "callable":
                return get_value_pairs(DummyObject)
            elif abstract_value == "object":
                return get_value_pairs(DummyObject())
            # all other types
            else:
                logger.info("Unknown abstract value: %s", abstract_value)
                return get_value_pairs(DummyObject())

elif params.value_abstraction == "fine-grained":
    def restore_value(abstract_value):
        # common primitive values
        if abstract_value == "None":
            return None
        elif abstract_value == "True":
            return True
        elif abstract_value == "False":
            return False
        # strings
        elif abstract_value == "str_empty":
            return ""
        elif abstract_value == "str_nonempty":
            return "a"
        # built-in numeric types
        elif abstract_value == "int_neg":
            return -1
        elif abstract_value == "int_zero":
            return 0
        elif abstract_value == "int_pos":
            return 1
        elif abstract_value == "float_neg":
            return -1.0
        elif abstract_value == "float_zero":
            return 0.0
        elif abstract_value == "float_pos":
            return 1.0
        # built-in sequence types
        elif abstract_value == "list_empty":
            return []
        elif abstract_value == "list_nonempty":
            return [DummyObject()]
        elif abstract_value == "tuple_empty":
            return ()
        elif abstract_value == "tuple_nonempty":
            return (DummyObject(),)
        # built-in set and dict types
        elif abstract_value == "set_empty":
            return set()
        elif abstract_value == "set_nonempty":
            return {DummyObject()}
        elif abstract_value == "dict_empty":
            return {}
        elif abstract_value == "dict_nonempty":
            return {"a": DummyObject()}
        # functions and methods
        elif abstract_value == "resource":
            return DummyObject()
        elif abstract_value == "callable":
            return DummyObject
        elif abstract_value == "object":
            return DummyObject()
        # all other types
        else:
            logger.info("Unknown abstract value: %s", abstract_value)
            return DummyObject()

else:
    raise ValueError(
        f"Unknown setting for value_abstraction: {params.value_abstraction}")
