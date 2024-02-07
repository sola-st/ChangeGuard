import argparse
import json
import os
import subprocess
import time

import libcst as cst

from .Logging import get_logger
from lexecutor.Util import shutdown_server, start_server, calc_changed_lines_coverage, extract_executed_lines
from lexecutor.CleanedCodeChange import CleanedCodeChange
from lexecutor.Metadata import Metadata
from lexecutor.Hyperparams import Hyperparams

instrumentation_logger = get_logger('Instrumentation', False, True)
run_logger = get_logger('Runner', False, True)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--commits", help="Path to commits.json", required=True)
parser.add_argument(
    "--action", help="Which action to perform, either instrument or run", choices=['instrument', 'run'], required=True)

METADATA = Metadata()


class OffsetProvider(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self, *fct_names):
        super().__init__()
        self.fct_names = fct_names
        self.offsets = {}

    def leave_FunctionDef(self, original_node: cst.FunctionDef) -> None:
        if original_node.name.value not in self.fct_names:
            return
        position = self.get_metadata(cst.metadata.PositionProvider, original_node)
        self.offsets[original_node.name.value.split('_')[-1]] = position.start.line, position.end.line


class FunctionPreparator(cst.CSTTransformer):

    METADATA_DEPENDENCIES = (cst.metadata.ParentNodeProvider, cst.metadata.WhitespaceInclusivePositionProvider)

    def __init__(self, suffix):
        super().__init__()
        self._nb_param_lines = -1
        self.suffix = suffix
        self.params = []
        self.strings = set()
        self.integers = set()
        self.floats = set()
        self.fun_name = ''

    def leave_Integer(self, original_node: cst.Integer, updated_node: cst.Integer):
        self.integers.add(updated_node.evaluated_value)
        return updated_node

    def leave_Float(self, original_node: cst.Float, updated_node: cst.Float):
        self.floats.add(updated_node.evaluated_value)
        return updated_node

    def leave_SimpleString(self, original_node: cst.SimpleString, updated_node: cst.SimpleString):
        if updated_node.prefix not in ["b", "br", "rb"]:  # skip bytes for now
            self.strings.add(updated_node.evaluated_value)
        return updated_node

    def visit_Parameters(self, node: cst.Parameters):
        if self._nb_param_lines >= 0:  # ensure this is only set for outermost function
            return True
        position = self.get_metadata(cst.metadata.WhitespaceInclusivePositionProvider, node)
        self._nb_param_lines = position.end.line - position.start.line

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef):
        if not isinstance(self.get_metadata(cst.metadata.ParentNodeProvider, original_node), cst.Module):
            return updated_node  # not outermost function
        parameters = updated_node.params
        self.params.extend(map(lambda x: x.name.value, parameters.params))
        self.params.extend(map(lambda x: x.name.value, parameters.kwonly_params))
        self.params.extend(map(lambda x: x.name.value, parameters.posonly_params))
        if isinstance(parameters.star_arg, cst.Param):
            self.params.append(parameters.star_arg.name.value)
        if parameters.star_kwarg is not None:
            self.params.append(parameters.star_kwarg.name.value)

        fun_name = updated_node.name.value + self.suffix
        self.fun_name = fun_name

        # make sure that no lines are removed when deleting parameters
        if self._nb_param_lines > 0:
            if isinstance(original_node.whitespace_before_params, cst.SimpleWhitespace):
                whitespace = cst.ParenthesizedWhitespace(
                    first_line=cst.TrailingWhitespace(),
                    empty_lines=[cst.EmptyLine() for _ in range(self._nb_param_lines - 1)],
                    last_line=cst.SimpleWhitespace(value='')
                )
            elif isinstance(original_node.whitespace_before_params, cst.ParenthesizedWhitespace):
                whitespace = cst.ParenthesizedWhitespace(
                    first_line=cst.TrailingWhitespace(whitespace=cst.SimpleWhitespace(value=''),
                                                      newline=cst.Newline(value=None)),
                    empty_lines=[cst.EmptyLine() for _ in
                                 range(self._nb_param_lines + len(original_node.whitespace_before_params.empty_lines))],
                    indent=True,
                    last_line=cst.SimpleWhitespace(value='')
                )
            else:  # hopefully does not happen
                whitespace = updated_node.whitespace_before_params
        else:
            whitespace = updated_node.whitespace_before_params

        return updated_node.with_changes(name=updated_node.name.with_changes(value=fun_name),
                                         whitespace_before_params=whitespace,
                                         params=cst.Parameters(params=[], star_arg=cst.MaybeSentinel.DEFAULT,
                                                               kwonly_params=[], star_kwarg=None, posonly_params=[],
                                                               posonly_ind=cst.MaybeSentinel.DEFAULT))


def prepare_function(fun, suffix):
    p = FunctionPreparator(suffix)
    tree = cst.metadata.MetadataWrapper(cst.parse_module(fun))
    tree = tree.visit(p)
    return cst.Module([tree]).code,  p.fun_name, p.params, p.strings, p.integers, p.floats,


def get_offsets(script, *fct_names):
    offset_provider = OffsetProvider(*fct_names)
    code = cst.MetadataWrapper(cst.parse_module(script))
    code.visit(offset_provider)
    return offset_provider.offsets


def generate_compare_script(code_change, directory):
    old_fun, old_fun_name, old_params, *old_literals = prepare_function(code_change.old_code, '_old')
    new_fun, new_fun_name, new_params, *new_literals = prepare_function(code_change.new_code, '_new')

    # assemble compare.py (old way)
    comment = f"# {code_change.old_sha} -- {code_change.new_sha}\n\n"
    fct_def_code = old_fun + "\n\n" + new_fun
    main_code_template = f"""


if __name__ == "__main__":
    import sys
    from lexecutor.Runtime import switch_state
    from lexecutor.Comparator import compare_exceptions, compare_main_args, compare_args, compare_return_values, unwrap_return_value
    exception_old = None
    try:
        val1 = {old_fun_name}()
        val1 = unwrap_return_value(val1)
    except Exception as e:
        exception_old = e
    switch_state()
    exception_new = None
    try:
        val2 = {new_fun_name}()
        val2 = unwrap_return_value(val2)
    except Exception as e:
        exception_new = e
    if compare_exceptions(exception_new, exception_old):
        sys.exit(0)
    if compare_main_args():
        sys.exit(0)
    if compare_args():
        sys.exit(0)
    if compare_return_values(val1, val2):
        sys.exit(0)
"""

    compare_script = comment + fct_def_code + main_code_template
    offsets = get_offsets(compare_script, old_fun_name, new_fun_name)
    script_path = f'{directory}/compare.py'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(compare_script)

    meta = {
        os.path.abspath(script_path): {
            'old_params': old_params,
            'new_params': new_params,
            'string_literals': list(old_literals[0] | new_literals[0]),  # currently buggy with bytes
            'integer_literals':  list(old_literals[1] | new_literals[1]),
            'float_literals':   list(old_literals[2] | new_literals[2]),
            'old_changed_lines': code_change.old_changed_lines,
            'new_changed_lines': code_change.new_changed_lines,
            'line_offsets': offsets,

        }
    }
    return meta


def instrument_compare_script(directory):
    script_path = os.path.abspath(os.path.join(directory, 'compare.py'))
    process = subprocess.run(f'python -m lexecutor.Instrument --files {script_path} --verbose',
                             shell=True, capture_output=True)
    instrumentation_logger.info(process.stdout.decode('utf-8'))
    instrumentation_logger.info(process.stderr.decode('utf-8'))


def run_instrumentation(code_change):
    started = time.time()
    directory_name = f'{code_change.repo}_{code_change.new_sha}'
    target_directory = f'{ROOT}/{directory_name}'
    if not os.path.exists(target_directory):
        os.mkdir(target_directory)
    meta = generate_compare_script(code_change, target_directory)
    instrument_compare_script(target_directory)
    METADATA.update(meta)
    METADATA.store()
    instrumentation_logger.info(f'Instrumentation took: {time.time() - started}s')


def run_lexecutor(code_change):
    total_start = time.time()
    script_path = os.path.abspath(f'{ROOT}/{code_change.repo}_{code_change.new_sha}/compare.py')
    run_logger.info(f'LExecuting: {script_path}')
    iterations = {}
    data = METADATA.get(script_path)
    for i in range(1, Hyperparams.nb_of_iterations+1):
        try:
            start = time.time()
            completed_process = subprocess.run(f'python {script_path}',
                                               capture_output=True, shell=True, timeout=60)
            end = time.time()
            run_logger.info(f'iteration_{i} took {end-start} seconds')
            output = completed_process.stdout.decode('utf-8')
            error = completed_process.stderr.decode('utf-8')
            if 'both functions returned same value' in output or 'both functions raised same' in output:
                result = 'preserving'
            elif ('both functions returned different values' in output or 'functions raised different' in output or
                  'function raised intentional exception' in output or 'functions modified argument' in output or
                  'potential side effect occurred during 3rd party function call' in output or
                  'number of 3rd party function calls changed' in output):
                result = 'changing'
            elif 'raised unintentional exception' in output:
                result = 'error'
            else:
                result = 'unknown'
        except subprocess.TimeoutExpired:
            output = ''
            error = ''
            result = 'timeout'
        old_executed_lines, new_executed_lines = extract_executed_lines(error, data['line_offsets'])
        old_ratio = calc_changed_lines_coverage(data['old_changed_lines'], old_executed_lines)
        new_ratio = calc_changed_lines_coverage(data['new_changed_lines'], new_executed_lines)
        iterations[f'iteration_{i}'] = {'out': output, 'err': error, 'result': result,
                                        'coverage': {
                                                'old': {
                                                    'executed_lines': old_executed_lines,
                                                    'ratio': old_ratio
                                                },
                                                'new': {
                                                    'executed_lines': new_executed_lines,
                                                    'ratio': new_ratio
                                                }
                                        }}
        if result == 'changing' or result == 'timeout':
            break
    final_result = 'non_conclusive'
    if 'preserving' in (it['result'] for it in iterations.values()):
        final_result = 'preserving'
    if 'changing' in (it['result'] for it in iterations.values()):
        final_result = 'changing'

    old_tot_executed_lines = list(set().union(*(set(it['coverage']['old']['executed_lines']) for it in iterations.values())))
    new_tot_executed_lines = list(set().union(*(set(it['coverage']['new']['executed_lines']) for it in iterations.values())))

    run_logger.info(f'Total time: {time.time()-total_start} seconds')
    return {
        'repo': code_change.repo,
        'sha': code_change.new_sha,
        'final_result': final_result,
        'iterations': iterations,
        'coverage': {
            'old': {
                'changed_lines': data['old_changed_lines'],
                'executed_lines': old_tot_executed_lines,
                'ratio': calc_changed_lines_coverage(data['old_changed_lines'], old_tot_executed_lines)
            },
            'new': {
                'changed_lines': data['new_changed_lines'],
                'executed_lines': new_tot_executed_lines,
                'ratio': calc_changed_lines_coverage(data['new_changed_lines'], new_tot_executed_lines)
            }
        }
    }


if __name__ == '__main__':
    args = parser.parse_args()
    with open(args.commits, 'r', encoding='utf-8') as f:
        commits = json.load(f)
    ROOT = r'generated'
    if args.action == 'instrument':
        if not os.path.exists(ROOT):
            os.mkdir(ROOT)
        for idx, commit in enumerate(commits, start=1):
            cleaned_code_change = CleanedCodeChange(commit['repo'], commit['old_commit'], commit['new_commit'],
                                                    commit['old_clean_function'], commit['new_clean_function'],
                                                    commit['old_changed_lines'], commit['new_changed_lines'])
            print(f"creating compare.py: {idx} / {len(commits)}", end='\r' if idx < len(commits) else '\n', flush=True)
            run_instrumentation(cleaned_code_change)

    if args.action == 'run':
        if not os.path.exists(ROOT):
            exit('Run Instrument first')
        run_logger.info(f'Started execution: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
        start_server()
        results = []
        for idx, commit in enumerate(commits, start=1):
            cleaned_code_change = CleanedCodeChange(commit['repo'], commit['old_commit'], commit['new_commit'],
                                                    commit['old_clean_function'], commit['new_clean_function'],
                                                    commit['old_changed_lines'], commit['new_changed_lines'])
            print(f'Lexecuting script: {idx} / {len(commits)}', end='\r' if idx < len(commits) else '\n', flush=True)
            results.append(run_lexecutor(cleaned_code_change))
        shutdown_server()
        with open('std_out.json', 'w') as f:
            json.dump(results, f, indent=4)
        run_logger.info(f'Finished execution: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')

