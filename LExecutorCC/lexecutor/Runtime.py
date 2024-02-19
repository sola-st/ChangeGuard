import atexit
import copy
import sys
import time
import random
import types
from .Hyperparams import Hyperparams as params
from .TraceWriter import TraceWriter
from .ValueAbstraction import restore_value, DummyObject, get_value_pairs
from .RuntimeStats import RuntimeStats
from .Logging import get_logger
from .Metadata import Metadata

logger = get_logger(__name__)

logger.info("Runtime starting")

METADATA = Metadata()
script_meta = METADATA.get_data_for_current_script()

# ------- begin: select mode -----
# mode = "RECORD"    # record values and write into a trace file
mode = "PREDICT"   # predict and inject values if missing in exeuction
# mode = "REPLAY"  # replay a previously recorded trace (mostly for testing)
# ------- end: select mode -------

file_type = "SOURCE"
# file_type = "TESTE"

if mode == "RECORD":
    trace = TraceWriter()
    atexit.register(lambda: trace.write_to_file())
    runtime_stats = None
elif mode == "PREDICT":
    # for running experiments
    if file_type == "SOURCE":
        file = sys.argv[0]
        execution = sys.argv[1] if len(sys.argv) > 1 else ""
    elif file_type == "TESTE":
        file = sys.argv[1]
        execution = sys.argv[2] if len(sys.argv) > 1 else ""
    
    runtime_stats = RuntimeStats(execution)
    atexit.register(runtime_stats.print)
    
    # from .predictors.AsIs import AsIs
    # predictor = AsIs()

    # from .predictors.NaiveValuePredictor import NaiveValuePredictor
    # predictor = NaiveValuePredictor()

    # from .predictors.RandomPredictor import RandomPredictor    
    # predictor = RandomPredictor()

    # from .predictors.FrequencyValuePredictor import FrequencyValuePredictor
    # predictor = FrequencyValuePredictor("values_frequencies.json")
    
    from .predictors.codet5.CodeT5ValuePredictor import CodeT5ValuePredictor
    predictor = CodeT5ValuePredictor(runtime_stats)

    # from .predictors.codebert.CodeBERTValuePredictor import CodeBERTValuePredictor
    # predictor = CodeBERTValuePredictor(runtime_stats)

    # from .predictors.Type4PyValuePredictor import Type4PyValuePredictor
    # predictor = Type4PyValuePredictor(file, runtime_stats)
    
    start_time = time.time()
    if file_type == "TESTE":
        predictor_name = "PynguinTests"
    else:
        predictor_name = predictor.__class__.__name__
        
    atexit.register(runtime_stats.save, file, predictor_name, start_time)
elif mode == "REPLAY":
    with open("trace.out", "r") as file:
        trace = file.readlines()
    next_trace_idx = 0
    runtime_stats = None

logger.info(f"### LExecutor running in {mode} mode ###")

state = 0  # 0: old, 1: new
def switch_state():
    global state
    state ^= 1


# map kind+name to predicted value to ensure consistent predictions for the same name
kind_and_name_to_value = {}
callable_store = ([], [])
raised_exc = {}


class IntentionalException(Exception):
    pass


class ExceptionFactory:

    store = {}

    @staticmethod
    def intentional_exception(name, *args):
        name = "IntentionalException_" + name.replace(".", "_")
        if name in ExceptionFactory.store:
            return ExceptionFactory.store[name](*args)
        exc = type(name, (IntentionalException,), {})
        ExceptionFactory.store[name] = exc
        return exc(*args)

    @staticmethod
    def intentional_exception_type(name):
        name = "IntentionalException_" + name.replace(".", "_")
        if name in ExceptionFactory.store:
            return ExceptionFactory.store[name]
        exc = type(name, (IntentionalException,), {})
        ExceptionFactory.store[name] = exc
        return exc

    @staticmethod
    def exception_type(name):
        try:
            return eval(name)
        except (NameError, AttributeError):
            name = "Dynamic_" + name.replace(".", "_")
            if name in ExceptionFactory.store:
                return ExceptionFactory.store[name]
            exc = type(name, (Exception,), {})
            ExceptionFactory.store[name] = exc
            return exc


def _isinstance(value, clazz):
    if isinstance(value, DummyObject):
        return value.pass_instance_check
    return isinstance(value, clazz)


class Super:
    pass


def _dummy_super(*args, **kwargs):
    callable_store[state].append(('super', copy.deepcopy(args), copy.deepcopy(kwargs)))
    return Super()


def _dummy_super_init__(*args, **kwargs):
    callable_store[state].append(('super.__init__', copy.deepcopy(args), copy.deepcopy(kwargs)))


def _n_(iid, name, lambada):
    if params.verbose:
        logger.info(f"\nAt iid={iid}, looking up name '{name}'")

    if runtime_stats is not None:
        runtime_stats.total_uses += 1
        runtime_stats.cover_iid(iid)

    perform_fct = lambada

    def record_fct(v):
        trace.append_name(iid, name, v)

    def predict_fct():
        key = f"name#{name}"
        if key in kind_and_name_to_value:
            return kind_and_name_to_value[key][state]
        else:
            if name == 'self':
                v = get_value_pairs(DummyObject())
                logger.info(f'Assigning {v} to {name}')
                kind_and_name_to_value[key] = v
                return v[state]
            v = predictor.name(iid, name)
            kind_and_name_to_value[key] = v
            return v[state]

    return mode_branch(iid, perform_fct, record_fct, predict_fct, kind="name")


def _handle_exception(fct_name, fct_to_excs):
    if fct_name in raised_exc:  # function did already raise an exception -> raise the same one
        raise raised_exc[fct_name]
    else:
        # dynamically compute probability such that it is always the same
        # for each try block no matter the number of functions called
        probability_for_exc = 1 - 0.1 ** (1 / len(fct_to_excs))
        if random.random() < probability_for_exc:  # raise exception
            exc_to_raise = random.choice(fct_to_excs[fct_name])
            raised_exc[fct_name] = ExceptionFactory.exception_type(exc_to_raise)
            raise raised_exc[fct_name]

def _c_(iid, fct, full_name, *args, **kwargs):
    if params.verbose:
        logger.info(f"\nAt iid={iid}, calling function {fct}")

    if runtime_stats is not None:
        runtime_stats.total_uses += 1
        runtime_stats.cover_iid(iid)

    def perform_fct():
        return fct(*args, **kwargs)

    def record_fct(v):
        trace.append_call(iid, fct, args, kwargs, v)

    def predict_fct():
        fct_name = fct.__name__ if hasattr(fct, "__name__") else str(fct)
        if " " in fct_name:  # some fcts that don't have a proper name
            fct_name = fct_name.split(" ")[0]
        key = f"call#{full_name}"
        callable_store[state].append((full_name,
                                      copy.deepcopy(tuple(arg if not isinstance(arg, types.FunctionType) else arg.__code__.co_name for arg in args)),
                                      copy.deepcopy({k: v if not isinstance(v, types.FunctionType) else v.__code__.co_name for k, v in kwargs.items()})))
        fct_to_excs = script_meta['func_to_excs']
        if key in kind_and_name_to_value:
            return kind_and_name_to_value[key][state]
        else:
            if full_name in fct_to_excs:  # function can raise exception (in try block)
                _handle_exception(full_name, fct_to_excs)
            v = predictor.call(iid, fct, fct_name, args, kwargs)  # TODO after retraining use static_fct_name for DummyObject
            kind_and_name_to_value[key] = v
            return v[state]

    kind = "call_dummy" if fct is DummyObject else "call"
    return mode_branch(iid, perform_fct, record_fct, predict_fct, kind=kind)


def _a_(iid, base, attr_name, full_name):
    if params.verbose:
        logger.info(f"\nAt iid={iid}, looking up attribute '{attr_name}'")

    if runtime_stats is not None:
        runtime_stats.total_uses += 1
        runtime_stats.cover_iid(iid)

    def perform_fct():
        # return getattr(base, attr_name)
        # unmangle private attributes (code copied from DynaPyt)
        if (attr_name.startswith('__')) and (not attr_name.endswith('__')):
            if type(base).__name__ == 'type':
                parents = [base]
            else:
                parents = [type(base)]
            found = True
            while len(parents) > 0:
                found = True
                cur_par = parents.pop()
                try:
                    cur_name = cur_par.__name__
                    cur_name = cur_name.lstrip('_')
                    return getattr(base, '_'+cur_name+attr_name)
                except AttributeError:
                    found = False
                    parents.extend(list(cur_par.__bases__))
                    continue
                break
            if not found:
                raise AttributeError()
        else:
            return getattr(base, attr_name)

    def record_fct(v):
        trace.append_attribute(iid, base, attr_name, v)

    def predict_fct():
        key = f"attribute#{full_name}"
        if key in kind_and_name_to_value:
            value = kind_and_name_to_value[key][state]
            if value is not DummyObject:
                setattr(base, attr_name, value)
            return value
        else:
            v = predictor.attribute(iid, base, attr_name)
            kind_and_name_to_value[key] = v
            value = v[state]
            if value is not DummyObject:
                setattr(base, attr_name, value)  # TODO private name mangling
            return value

    return mode_branch(iid, perform_fct, record_fct, predict_fct, kind="attribute")


def _l_(iid, expression=None):
    if runtime_stats is not None:
        runtime_stats.cover_line(iid)
        runtime_stats.save(file, predictor_name, start_time)
    return expression


def _s_(iid, name, lambada):

    perform_fct = lambada

    def record_fct(v):
        trace.append_subscript(iid, name, v)

    def predict_fct():
        key = f"subscript#{name}"
        if key in kind_and_name_to_value:
            return kind_and_name_to_value[key][state]
        else:
            v = get_value_pairs(DummyObject())
            logger.info(f'Predicting for {key}, returning {v}')
            kind_and_name_to_value[key] = v
            return v[state]

    return mode_branch(iid, perform_fct, record_fct, predict_fct, kind="subscript")

def mode_branch(iid, perform_fct, record_fct, predict_fct, kind):
    if mode == "RECORD":
        v = perform_fct()
        record_fct(v)
        return v
    elif mode == "PREDICT":
        if kind == "call_dummy":
            # predict and inject a return value
            v = predict_fct()
            return v
        else:
            # try to perform the regular behavior and intervene in case of exceptions caused by missing values
            try:
                v = perform_fct()
                if params.verbose:
                    logger.info("Found/computed/returned regular value")
                return v
            except Exception as e:
                if (type(e) == NameError and kind == "name") \
                        or (type(e) == AttributeError and kind == "attribute") \
                        or ((type(e) == IndexError or type(e) == KeyError) and kind == "subscript"):
                    if params.verbose:
                        logger.info(
                            f"Catching '{type(e)}' during {kind} and calling predictor instead")
                    v = predict_fct()
                    runtime_stats.guided_uses += 1
                    return v
                else:
                    if params.verbose:
                        logger.info(
                            f"Exception '{type(e)}' not caught, re-raising")
                    runtime_stats.uncaught_exception(iid, e)
                    raise e
    elif mode == "REPLAY":
        # replay mode
        global next_trace_idx
        trace_line = trace[next_trace_idx].rstrip()
        next_trace_idx += 1
        segments = trace_line.split(" ")
        trace_iid = int(segments[0])
        abstract_value = segments[-1]
        if iid != trace_iid:
            raise Exception(
                f"trace_iid={trace_iid} doesn't match execution iid={iid}")
        v = restore_value(abstract_value)
        return v
    else:
        raise Exception(f"Unexpected mode {mode}")
