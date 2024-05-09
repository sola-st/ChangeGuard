import random
import copy
import types
from collections import namedtuple
from abc import ABC


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
    _type = random.choices([LexecutorObject, _get_random_integer, _get_random_str, _get_random_float, _get_random_bool, lambda: None], cum_weights=[50, 65, 80, 92, 97, 100])[0]
    return tuple(_type() for _ in range(size))


def _get_random_list(include_dummy=True):
    size = random.randint(0, 4)
    if include_dummy:
        _type = random.choices([LexecutorObject, _get_random_integer, _get_random_str, _get_random_float, _get_random_bool, lambda: None], cum_weights=[50, 65, 80, 92, 97, 100])[0]
    else:
        _type = random.choices([_get_random_integer,  _get_random_str, _get_random_float, _get_random_bool, lambda: None], cum_weights=[30, 60, 85, 95, 100])[0]
    return LexecutorList([_type() for _ in range(size)])


def _get_random_sets():
    size = random.randint(0, 1)
    _type = random.choices([LexecutorObject, _get_random_integer, _get_random_str, _get_random_float, _get_random_bool, lambda: None], cum_weights=[50, 65, 80, 92, 97, 100])[0]
    return LexecutorSet({_type() for _ in range(size)})


def _get_random_dict(include_dummy=True):
    size = random.randint(0, 2)
    if include_dummy:
        _type = random.choices([LexecutorObject, _get_random_integer, _get_random_str, _get_random_float, _get_random_bool, lambda: None], cum_weights=[50, 65, 80, 92, 97, 100])[0]
    else:
        _type = random.choices([_get_random_integer,  _get_random_str, _get_random_float, _get_random_bool, lambda: None], cum_weights=[30, 60, 85, 95, 100])[0]
    return LexecutorDict({_get_random_str(): _type() for _ in range(size)})


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


class Dummy(ABC):

    _internal_attributes = ['_parent', '_name_in_parent']

    def __init__(self):
        self._parent = None  # parent and corresponding name is set in Runtime
        self._name_in_parent = None

    def set_to_parent(self, key=None):
        if self._parent is None or self._name_in_parent is None:
            return
        if key in self._internal_attributes:
            return

        # following check needed in case the attribute
        # has already been overwritten in the parent
        if hasattr(self._parent, self._name_in_parent):
            return

        setattr(self._parent, self._name_in_parent, self)  # TODO private name mangling


class LexecutorObject(Dummy):

    _id_counter = 0
    _seen_ids = []
    _internal_attributes = ['_id', '_iterable', '_dict', '_int', '_float', '_str', '_bool', '_isinstance_class',
                            '_index', '_parent', '_name_in_parent']
    __comparing = False

    @staticmethod
    def serialize(obj):
        return 'obj#' + repr(sorted(map(lambda x: (x[0], x[1]) if not isinstance(x[1], types.FunctionType) else (x[0], x[1].__code__.co_name), [(k, v) for k, v in obj.__dict__.items() if k not in LexecutorObject._internal_attributes]), key=lambda x: x[0]))

    def __init__(self, *a, **b):
        super().__init__()
        self._iterable = _get_random_list(include_dummy=False)
        self._dict = _get_random_dict(include_dummy=False)
        self._int = _get_random_integer()
        self._float = _get_random_float()
        self._str = _get_random_str()
        self._bool = _get_random_bool()
        self._isinstance_class = random.choice(script_meta['classes']) if script_meta is not None else "None"
        self._id = LexecutorObject._id_counter
        self._index = 0
        LexecutorObject._id_counter += 1

    def repr_without_internals(self):
        LexecutorObject.__comparing = True
        LexecutorObject._seen_ids = [self._id]
        self_repr = self.serialize(self)
        LexecutorObject._seen_ids = []
        LexecutorObject.__comparing = False
        return self_repr

    def repr_only_internals(self):
        return ", ".join([attr + "=" + repr(getattr(self, attr)) for attr in LexecutorObject._internal_attributes])

    def __operation(self, other, operator, right=False):
        if isinstance(other, int):
            if right:
                return eval(f"{other} {operator} {self._int}")
            return eval(f"{self._int} {operator} {other}")
        if isinstance(other, float):
            if right:
                return eval(f"{other} {operator} {self._float}")
            return eval(f"{self._float} {operator} {other}")
        if isinstance(other, complex):
            if right:
                return eval(f"{other} {operator} {complex(self._int)}")
            return eval(f"{complex(self._int)} {operator} {other}")
        if isinstance(other, bool):
            if right:
                return eval(f"{other} {operator} {self._bool}")
            return eval(f"{self._bool} {operator} {other}")
        if isinstance(other, str):
            if right:
                return eval(f"'{other}' {operator} '{self._str}'")
            return eval(f"'{self._str}' {operator} '{other}'")
        return False

    def __abs__(self):
        return abs(self._int)

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
        return self._bool

    def __bytes__(self):
        return bytes(self._str, "utf-8")

    def __call__(self, *args, **kwargs):
        return self

    # def __ceil__(self):
    #     pass

    def __complex__(self):
        return complex(self._int)

    def __contains__(self, item):
        if isinstance(item, int):
            return item in self._iterable
        else:
            return item in self._dict


    # def __del__(self):
    #     pass  # TODO / REMOVE

    # def __delattr__(self, item):
    #     pass  # TODO / REMOVE

    # def __delete__(self, instance):
    #     pass  # TODO / REMOVE

    def __delitem__(self, item):
        if isinstance(item, (int, slice)):
            del self._iterable[item]
        else:
            del self._dict[item]

    # def __dir__(self):
    #     pass

    def __divmod__(self, other):
        return self.__operation(other, "//"), self.__operation(other, "%")

    def __enter__(self):
        return self

    def __eq__(self, other):
        if not isinstance(other, LexecutorObject):
            return self.__operation(other, "==")

        LexecutorObject.__comparing = True
        LexecutorObject._seen_ids = [self._id, other._id]
        serialized_self = self.serialize(self)
        LexecutorObject._seen_ids = [self._id, other._id]
        serialized_other = self.serialize(other)
        LexecutorObject._seen_ids = []  # reset list
        LexecutorObject.__comparing = False
        return serialized_self == serialized_other

    def __exit__(self, exc_type, exc_value, trace):
        return True

    def __float__(self):
        return self._float

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
        if isinstance(item, (int, slice)):
            return self._iterable[item]
        else:
            return self._dict[item]

    def __gt__(self, other):
        return self.__operation(other, ">")

    def __hash__(self):
        return hash(f"DummyObject{self._id}")

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
        return self._int

    # def __init_subclass__(cls, **kwargs):
    #     pass  # REMOVE

    # def __instancecheck__(self, instance):
    #     pass  # TODO!

    def __int__(self):
        return self._int

    def __invert__(self):
        return ~self._int

    def __ior__(self, other):
        return self.__operation(other, "or")

    def __ipow__(self, other):
        pass  # TODO

    def __irshift__(self, other):
        return self.__operation(other, ">>")

    def __isub__(self, other):
        return self.__operation(other, "-")

    def __iter__(self):
        return iter(self._iterable)

    def __itruediv__(self, other):
        return self.__operation(other, "/")

    def __ixor__(self, other):
        return self.__operation(other, "^")

    def __le__(self, other):
        return self.__operation(other, "<=")

    def __len__(self):
        return len(self._iterable)

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
        return -self._int

    # def __new__(cls, *args, **kwargs):
    #     pass

    def __next__(self):
        if self._index >= len(self._iterable):
            raise StopIteration
        self._index += 1
        return self._iterable[self._index - 1]

    def __or__(self, other):
        return self.__operation(other, "or")

    def __pos__(self):
        return +self._int

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
        if not LexecutorObject.__comparing or self._id in LexecutorObject._seen_ids:
            return f"obj#{self._id}"
        else:
            LexecutorObject._seen_ids.append(self._id)
            return self.serialize(self)

    def __reversed__(self):
        return reversed(self._iterable)

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

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)
        self.set_to_parent(key)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self._iterable.insert(key, value)
        if isinstance(key, slice):
            self._iterable[key] = value
        else:
            self._dict[key] = value

    # def __sizeof__(self):
    #     pass  # REMOVE

    def __str__(self):
        return self._str

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
        return self._str


class LexecutorList(list, Dummy):

    def __init__(self, iterable=()):
        super().__init__(iterable)
        Dummy.__init__(self)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.set_to_parent()

    def __iadd__(self, other):
        self.set_to_parent()
        return super().__iadd__(other)

    def __imul__(self, other):
        self.set_to_parent()
        return super().__imul__(other)

    def __delitem__(self, item):
        super().__delitem__(item)
        self.set_to_parent()

    def append(self, other):
        super().append(other)
        self.set_to_parent()

    def clear(self):
        super().clear()
        self.set_to_parent()

    def extend(self, other):
        super().extend(other)
        self.set_to_parent()

    def insert(self, index, item):
        super().insert(index, item)
        self.set_to_parent()

    def pop(self, index=-1):
        self.set_to_parent()
        return super().pop(index)

    def remove(self, item):
        super().remove(item)
        self.set_to_parent()

    def reversed(self):
        super().reverse()
        self.set_to_parent()

    def sort(self, key=None, reverse=False):
        super().sort(key=key, reverse=reverse)
        self.set_to_parent()


class LexecutorDict(dict, Dummy):

    def __init__(self, *mapping, **kwargs):
        super().__init__(*mapping, **kwargs)
        Dummy.__init__(self)

    def __delitem__(self, item):
        super().__delitem__(item)
        self.set_to_parent()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.set_to_parent()

    def clear(self):
        super().clear()
        self.set_to_parent()

    def pop(self, item, *default):
        self.set_to_parent()
        return super().pop(item, *default)

    def popitem(self):
        self.set_to_parent()
        return super().popitem()

    def setdefault(self, key, default=None):
        self.set_to_parent()
        return super().setdefault(key, default)

    def update(self, *mapping, **kwargs):
        super().update(*mapping, **kwargs)
        self.set_to_parent()


class LexecutorSet(set, Dummy):

    def __init__(self, iterable=()):
        super().__init__(iterable)
        Dummy.__init__(self)

    def __iand__(self, other):
        self.set_to_parent()
        return super().__iand__(other)

    def __ior__(self, other):
        self.set_to_parent()
        return super().__ior__(other)

    def __isub__(self, other):
        self.set_to_parent()
        return super().__isub__(other)

    def __ixor__(self, other):
        self.set_to_parent()
        return super().__ixor__(other)

    def add(self, other):
        super().add(other)
        self.set_to_parent()

    def clear(self):
        super().clear()
        self.set_to_parent()

    def difference_update(self, other):
        super().difference_update(other)
        self.set_to_parent()

    def discard(self, item):
        super().discard(item)
        self.set_to_parent()

    def intersection_update(self, other):
        super().intersection_update(other)
        self.set_to_parent()

    def pop(self):
        self.set_to_parent()
        return super().pop()

    def remove(self, item):
        super().remove(item)
        self.set_to_parent()

    def symmetric_difference_update(self, other):
        super().symmetric_difference_update(other)
        self.set_to_parent()

    def update(self, other):
        super().update(other)
        self.set_to_parent()


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
                return [LexecutorObject()]
            elif abstract_value == "tuple":
                return (LexecutorObject(),)
            # built-in set and dict types
            elif abstract_value == "set":
                return {LexecutorObject()}
            elif abstract_value == "dict":
                return {"a": LexecutorObject()}
            # functions and methods
            elif abstract_value == "resource":
                return LexecutorObject()
            elif abstract_value == "callable":
                return LexecutorObject
            elif abstract_value == "object":
                return LexecutorObject()
            # all other types
            else:
                logger.info("Unknown abstract value: %s", abstract_value)
                return LexecutorObject()
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
                return get_value_pairs(_get_random_dict())
            # functions and methods
            elif abstract_value == "resource":
                return get_value_pairs(LexecutorObject())
            elif abstract_value == "callable":
                return get_value_pairs(LexecutorObject)
            elif abstract_value == "object":
                return get_value_pairs(LexecutorObject())
            # all other types
            else:
                logger.info("Unknown abstract value: %s", abstract_value)
                return get_value_pairs(LexecutorObject())

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
            return [LexecutorObject()]
        elif abstract_value == "tuple_empty":
            return ()
        elif abstract_value == "tuple_nonempty":
            return (LexecutorObject(),)
        # built-in set and dict types
        elif abstract_value == "set_empty":
            return set()
        elif abstract_value == "set_nonempty":
            return {LexecutorObject()}
        elif abstract_value == "dict_empty":
            return {}
        elif abstract_value == "dict_nonempty":
            return {"a": LexecutorObject()}
        # functions and methods
        elif abstract_value == "resource":
            return LexecutorObject()
        elif abstract_value == "callable":
            return LexecutorObject
        elif abstract_value == "object":
            return LexecutorObject()
        # all other types
        else:
            logger.info("Unknown abstract value: %s", abstract_value)
            return LexecutorObject()

else:
    raise ValueError(
        f"Unknown setting for value_abstraction: {params.value_abstraction}")
