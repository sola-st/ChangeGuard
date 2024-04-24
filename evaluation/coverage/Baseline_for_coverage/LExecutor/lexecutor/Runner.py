import argparse
import json
import os
import subprocess
import sys
import time
import logging

import libcst as cst

from lexecutor.Util import calc_changed_lines_coverage, extract_executed_lines
from lexecutor.CleanedCodeChange import CleanedCodeChange
from lexecutor.Metadata import Metadata
from lexecutor.Hyperparams import Hyperparams
from lexecutor.FunctionPreparator import FunctionPreparator, OffsetProvider


logger = logging.getLogger('baseline')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('"%(name)s" : %(message)s')
file_handler = logging.FileHandler('time.log', encoding='UTF-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--commits", help="Path to commits.json", required=True)
parser.add_argument(
    "--action", help="Which action to perform, either instrument or run", choices=['instrument', 'run'], required=True)

METADATA = Metadata()

def prepare_function(fun, suffix):
    p = FunctionPreparator(suffix)
    tree = cst.metadata.MetadataWrapper(cst.parse_module(fun))
    tree = tree.visit(p)
    return cst.Module([tree]).code, p.fun_name, p.func_to_exc, p.found_classes, p.params, p.strings, p.integers, p.floats,


def get_offsets(script, *fct_names):
    offset_provider = OffsetProvider(*fct_names)
    code = cst.MetadataWrapper(cst.parse_module(script))
    code.visit(offset_provider)
    return offset_provider.offsets


def generate_compare_script(code_change, directory):
    old_fun, old_fun_name, old_excs, old_classes, old_params, *old_literals = prepare_function(code_change.old_code, '_old')
    new_fun, new_fun_name, new_excs, new_classes, new_params, *new_literals = prepare_function(code_change.new_code, '_new')

    # assemble compare.py
    comment = f"# {code_change.old_sha} -- {code_change.new_sha}\n\n"
    fct_def_code = old_fun + "\n\n" + new_fun
    main_code_template = f"""

def _context_stdout():
    import contextlib
    import io
    return contextlib.redirect_stdout(io.StringIO())
    
def _context_stderr():
    import contextlib
    import io
    return contextlib.redirect_stderr(io.StringIO())
    
def _exit_lexecutor():
    import sys
    sys.exit(0)

if __name__ == "__main__":
    from lexecutor.Runtime import switch_state
    from lexecutor.Comparator import compare_exceptions, compare_main_args, compare_args, compare_return_values, compare_stdout, compare_stderr, unwrap_return_value
    exception_old = None
    old_stdout = ''
    old_stderr = ''
    try:
        with _context_stdout() as f_out, _context_stderr() as f_err:
            val1 = {old_fun_name}()
            val1 = unwrap_return_value(val1)
        old_stdout = f_out.getvalue()
        old_stderr = f_err.getvalue()
    except Exception as e:
        exception_old = e
    switch_state()
    exception_new = None
    new_stdout = ''
    new_stderr = ''
    try:
        with _context_stdout() as f_out, _context_stderr() as f_err:
            val2 = {new_fun_name}()
            val2 = unwrap_return_value(val2)
        new_stdout = f_out.getvalue()
        new_stderr = f_err.getvalue()
    except Exception as e:
        exception_new = e
    if compare_exceptions(exception_old, exception_new):
        _exit_lexecutor()
    if compare_main_args():
        _exit_lexecutor()
    if compare_args():
        _exit_lexecutor()
    if compare_stdout(old_stdout, new_stdout):
        _exit_lexecutor()
    if compare_stderr(old_stderr, new_stderr):
        _exit_lexecutor()
    if compare_return_values(val1, val2):
        _exit_lexecutor()
"""

    compare_script = comment + fct_def_code + main_code_template
    offsets = get_offsets(compare_script, old_fun_name, new_fun_name)
    script_path = f'{directory}/compare.py'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(compare_script)

    func_to_excs = {}
    for key in old_excs.keys() | new_excs.keys():
        func_to_excs[key] = list(old_excs.get(key, set()) | new_excs.get(key, set()))

    project_name = directory.split('/')[-1]

    meta = {
        os.path.abspath(script_path): {
            'old_params': old_params,
            'new_params': new_params,
            'func_to_excs': func_to_excs,
            'classes': list(old_classes | new_classes),
            'renames': None,
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
                             shell=True, stdout=sys.stdout, stderr=sys.stderr)


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
    logger.info(f'Instrumentation took: {time.time() - started}s')


def run_lexecutor(code_change):
    total_start = time.time()
    script_path = os.path.abspath(f'{ROOT}/{code_change.repo}_{code_change.new_sha}/compare.py')
    logger.info(f'LExecuting: {script_path}')
    iterations = {}
    data = METADATA.get(script_path)
    successful = False
    for i in range(1, Hyperparams.nb_of_iterations+1):
        try:
            completed_process = subprocess.run(f'python {script_path}',
                                               capture_output=True, shell=True, timeout=60)
            #run_logger.info(f'iteration_{i} took {end-start} seconds')
            output = completed_process.stdout.decode('utf-8')
            error = completed_process.stderr.decode('utf-8')

        except subprocess.TimeoutExpired:
            output = ''
            error = 'timeout'

        old_executed_lines, new_executed_lines = extract_executed_lines(error, data['line_offsets'])
        iterations[f'iteration_{i}'] = {'out': output, 'err': error, 'old_executed_lines': old_executed_lines, 'new_executed_lines': new_executed_lines}
        if output and 'Function(s) raised an exception' not in output:
            successful = True

    old_tot_executed_lines = list(
        set().union(*(set(it['old_executed_lines']) for it in iterations.values())))
    new_tot_executed_lines = list(
        set().union(*(set(it['new_executed_lines']) for it in iterations.values())))
    logger.info(f'Total time: {time.time() - total_start} seconds')
    return {
        'repo': commit['repo'],
        'sha': commit['sha'],
        'successful': successful,
        'iterations': iterations,
        'old_tot_executed_lines': old_tot_executed_lines,
        'new_tot_executed_lines': new_tot_executed_lines
    }



if __name__ == '__main__':
    args = parser.parse_args()
    with open(args.commits, 'r', encoding='utf-8') as f:
        commits = json.load(f)
    ROOT = r'generated'
    if args.action == 'instrument':
        logger.info(f'Started instrumentation: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
        if not os.path.exists(ROOT):
            os.mkdir(ROOT)
        for idx, commit in enumerate(commits, start=1):
            cleaned_code_change = CleanedCodeChange(commit['repo'], commit['old_commit'], commit['new_commit'],
                                                    commit['old_clean_function'], commit['new_clean_function'],
                                                    commit['old_changed_lines'], commit['new_changed_lines'])
            print(f"creating compare.py: {idx} / {len(commits)}", end='\r' if idx < len(commits) else '\n', flush=True)
            run_instrumentation(cleaned_code_change)
        logger.info(f'Finished instrumentation: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')

    if args.action == 'run':
        if not os.path.exists(ROOT):
            exit('Run Instrument first')
        logger.info(f'Started execution: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
        #start_server()
        results = []
        for idx, commit in enumerate(commits, start=1):
            cleaned_code_change = CleanedCodeChange(commit['repo'], commit['old_commit'], commit['new_commit'],
                                                    commit['old_clean_function'], commit['new_clean_function'],
                                                    commit['old_changed_lines'], commit['new_changed_lines'])
            print(f'Lexecuting script: {idx} / {len(commits)}', end='\r' if idx < len(commits) else '\n', flush=True)
            results.append(run_lexecutor(cleaned_code_change))
        #shutdown_server()
        with open('../std_out.json', 'w') as f:
            json.dump(results, f, indent=4)
        logger.info(f'Finished execution: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')

