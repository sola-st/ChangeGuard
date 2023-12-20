import argparse
import json
import os
import subprocess
import time

import libcst as cst

from .logger import get_logger

instrumentation_logger = get_logger(__name__, 'instrument')
run_logger = get_logger('run', 'run')

parser = argparse.ArgumentParser()
parser.add_argument(
    "--commits", help="Path to commits.json", required=True)
parser.add_argument(
    "--action", help="Which action to perform either instrument or run", choices=['instrument', 'run'], required=True)


class FunctionPreparator(cst.CSTTransformer):
    def __init__(self, suffix):
        super().__init__()
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

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef):
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
        return updated_node.with_changes(name=updated_node.name.with_changes(value=fun_name),
                                         params=cst.Parameters(params=[], star_arg=cst.MaybeSentinel.DEFAULT,
                                                               kwonly_params=[], star_kwarg=None, posonly_params=[],
                                                               posonly_ind=cst.MaybeSentinel.DEFAULT))


def prepare_function(fun, suffix):
    p = FunctionPreparator(suffix)
    tree = cst.parse_statement(fun)
    tree = tree.visit(p)
    return cst.Module([tree]).code,  p.fun_name, p.params, p.strings, p.integers, p.floats,


def generate_compare_script(commit, directory):
    old_fun, old_fun_name, old_params, *old_literals = prepare_function(commit['old_clean_function'], '_old')
    new_fun, new_fun_name, new_params, *new_literals = prepare_function(commit['new_clean_function'], '_new')

    # assemble compare.py (old way)
    comment = f"# {commit['old_commit']} -- {commit['new_commit']}\n\n"
    fct_def_code = old_fun + "\n\n" + new_fun
    main_code_template = f"""
def different(val1, val2):
    if type(val1) != type(val2):
        return True
    if type(val1) == list and type(val2) == list and len(val1) != len(val2):
        return True
    if type(val1) == dict and type(val2) == dict and len(val1) != len(val2):
        return True
    if type(val1) == set and type(val2) == set and len(val1) != len(val2):
        return True
    if type(val1) == tuple and type(val2) == tuple and len(val1) != len(val2):
        return True
    if type(val1) in [int, float, str, bool, type(None)] and type(val2) in [int, float, str, bool, type(None)]:
        return val1 != val2
    return False


if __name__ == "__main__":
    import pathlib
    p = str(pathlib.Path(__file__).parent.resolve())
    from lexecutor.Runtime import switch_state

    try:
        val1 = {old_fun_name}()
        switch_state()
        val2 = {new_fun_name}()
    except Exception as e:
        print(p + ": Function(s) raised an exception: " + str(type(e)) + " -- " + str(e))
    else:
        if different(val1, val2):
            print(p + ": Functions returned different values: " + str(val1) + " vs. " + str(val2))
        else:
            print(p + ": Both functions returned the same value" + str(val1))
"""

    compare_script = comment + fct_def_code + main_code_template
    script_path = f'{directory}/compare.py'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(compare_script)

    meta = {
        os.path.abspath(script_path): {
            'old_params': old_params,
            'new_params': new_params,
            'string_literals': list(old_literals[0] | new_literals[0]),  # currently buggy with bytes
            'integer_literals':  list(old_literals[1] | new_literals[1]),
            'float_literals':   list(old_literals[2] | new_literals[2])
        }
    }
    return meta


def instrument_compare_script(directory):
    script_path = os.path.abspath(os.path.join(directory, 'compare.py'))
    process = subprocess.run(f'python -m lexecutor.Instrument --files {script_path} --verbose',
                             cwd=os.path.abspath('.'), shell=True, capture_output=True)
    instrumentation_logger.info(process.stdout.decode('utf-8'))
    instrumentation_logger.info(process.stderr.decode('utf-8'))


def run_instrumentation(path_to_commits):
    root = r'generated'
    if not os.path.exists(root):
        os.mkdir(root)
    with open(path_to_commits, 'r', encoding='utf-8') as f:
        commits = json.load(f)
    meta = {}
    for idx, commit in enumerate(commits, start=1):
        print(f"creating compare.py: {idx} / {len(commits)}", end='\r' if idx < len(commits) else '\n', flush=True)
        directory_name = f'{commit["repo"]}_{commit["sha"]}'
        directory = f'{root}/{directory_name}'
        if not os.path.exists(directory):
            os.mkdir(directory)
        meta.update(generate_compare_script(commit, directory))
        instrument_compare_script(directory)
    with open('./meta.json', 'w') as f:
        json.dump(meta, f, indent=4)


def run():
    run_logger.info(f'Started execution: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
    root = r'generated'
    dirs = [(entry.name, entry.path) for entry in os.scandir(root) if entry.is_dir()]
    results = []
    for idx, (folder_name, folder_path) in enumerate(dirs, start=1):
        print(f'Lexecuting script: {idx} / {len(dirs)}', end='\r' if idx < len(dirs) else '\n', flush=True)
        script_path = os.path.abspath(os.path.join(folder_path, 'compare.py'))
        repo, sha = folder_name.split('_')
        iterations = {}
        for i in range(1, 6):
            try:
                start = time.time()
                completed_process = subprocess.run(f'python {script_path}', cwd=os.path.abspath('.'),
                                                   capture_output=True, shell=True, timeout=30)
                end = time.time()
                run_logger.info(f'iteration_{i} took {end-start} seconds')
                output = completed_process.stdout.decode('utf-8')
                error = completed_process.stderr.decode('utf-8')
                if 'Both functions returned the same value' in output:
                    result = 'preserving'
                elif 'Functions returned different values' in output:
                    result = 'changing'
                elif 'Function(s) raised an exception' in output:
                    result = 'error'
                else:
                    result = 'unknown'
            except subprocess.TimeoutExpired:
                output = ''
                error = ''
                result = 'timeout'

            iterations[f'iteration_{i}'] = {'out': output, 'err': error, 'result': result}
            if result == 'changing' or result == 'timeout':
                break
        final_result = 'non_conclusive'
        if 'preserving' in (it['result'] for it in iterations.values()):
            final_result = 'preserving'
        if 'changing' in (it['result'] for it in iterations.values()):
            final_result = 'changing'
        results.append({
            'repo': repo,
            'sha': sha,
            'final_result': final_result,
            'iterations': iterations
        })
    with open('std_out.json', 'w') as f:
        json.dump(results, f, indent=4)
    run_logger.info(f'Finished execution: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')


if __name__ == '__main__':
    args = parser.parse_args()
    if args.action == 'instrument':
        run_instrumentation(args.commits)
    if args.action == 'run':
        run()
