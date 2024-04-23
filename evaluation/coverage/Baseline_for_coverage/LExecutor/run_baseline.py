import libcst as cst
from os.path import join
import json
import argparse
import os
import subprocess
import time
import logging

logger = logging.getLogger('time')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('"%(name)s" : %(message)s')
file_handler = logging.FileHandler('time.log', encoding='UTF-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--dest", help="Destination directory", required=True)
parser.add_argument(
    "--commits", help="Path to commits.json", required=True)
parser.add_argument("--action", help="Which action to perform either instrument or run", choices=['instrument', 'run'], required=True)

# Copied From original LExecutor
class FunctionExtractor(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self, line):
        self.line = line
        self.function = None
        self.is_method = False
        self.param_names = []

    def leave_Param(self, node, updated_node):
        # remove parameter type annotation
        return updated_node.with_changes(annotation=None)

    def leave_FunctionDef(self, node, updated_node):
        if node.name.value == "__init__":
            # ignore constructors, because we want to compare return values
            return updated_node

        start = self.get_metadata(cst.metadata.PositionProvider, node).start
        end = self.get_metadata(cst.metadata.PositionProvider, node).end
        if start.line <= self.line <= end.line:
            self.function = updated_node.with_changes(returns=None)

            if len(node.params.params) > 0 and node.params.params[0].name.value == "self":
                self.is_method = True

            for param in node.params.params:
                self.param_names.append(param.name.value)

        return updated_node


# Copied from original LExecutor
def create_class_wrapper(fct_node, wrapper_name, suffix):
    fct_def_code = cst.Module([]).code_for_node(
        cst.ClassDef(
            name=cst.Name(
                value=wrapper_name
            ),
            body=cst.IndentedBlock([fct_node.with_changes(name=cst.Name(value=fct_node.name.value + suffix))])
            # body=cst.IndentedBlock(
            #     body=[node.with_changes(=None)]
            # )
        )
    )
    return fct_def_code


#Copied from LExecutorCC
def extract_executed_lines(result_string, offsets):
    prefix = 'Lines executed: ['
    if prefix not in result_string:
        return [], []
    temp = result_string[result_string.find(prefix) + len(prefix):]
    all_lines = list(map(int, temp[:temp.find(']')].split(', ')))
    return ([line-offsets['old'][0]+1 for line in all_lines if offsets['old'][0] <= line <= offsets['old'][1]],
            [line-offsets['new'][0]+1 for line in all_lines if offsets['new'][0] <= line <= offsets['new'][1]])


# Copied fron LExecutorCC
class OffsetProvider(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self):
        super().__init__()
        self.offsets = {}

    def leave_FunctionDef(self, original_node: cst.FunctionDef) -> None:
        if original_node.name.value.endswith('_old') or original_node.name.value.endswith('_new'):
            position = self.get_metadata(cst.metadata.PositionProvider, original_node)
            self.offsets[original_node.name.value.split('_')[-1]] = position.start.line, position.end.line


# Copied from LExecutorCC
def get_offsets(script):
    offset_provider = OffsetProvider()
    code = cst.MetadataWrapper(cst.parse_module(script))
    code.visit(offset_provider)
    return offset_provider.offsets

# Copied from original LExecutor
def write_function_comparison_script(old_fct_extractor, new_fct_extractor, dest_dir, commit):
    # create code that defines the functions/methods
    assert old_fct_extractor.is_method == new_fct_extractor.is_method
    if old_fct_extractor.is_method:
        # wrap function into a class
        old_fct_def_code = create_class_wrapper(old_fct_extractor.function, "Wrapper1", "_old")
        new_fct_def_code = create_class_wrapper(new_fct_extractor.function, "Wrapper2", "_new")
        fct_def_code = old_fct_def_code + "\n\n" + new_fct_def_code
    else:
        # change name of functions to distinguish old and new
        renamed_old_fct = old_fct_extractor.function.with_changes(
            name=cst.Name(value=old_fct_extractor.function.name.value + "_old"))
        renamed_new_fct = new_fct_extractor.function.with_changes(
            name=cst.Name(value=new_fct_extractor.function.name.value + "_new"))
        fct_def_code = cst.Module([]).code_for_node(renamed_old_fct) + "\n\n" + cst.Module([]).code_for_node(
            renamed_new_fct)

    # create code that calls and compares the two functions/methods
    main_code_template = """
def different(val1, val2):
    if type(val1) == Wrapper1 and type(val2) == Wrapper2:
        return False
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

    try:
        val1 = INVOCATION1
        val2 = INVOCATION2
    except Exception as e:
        print(p + ": Function(s) raised an exception: " + str(type(e)) + " -- " + str(e))
    else:
        if different(val1, val2):
            print(p + ": Functions returned different values: " + str(val1) + " vs. " + str(val2))
        else:
            print(p + ": Both functions returned the same value" + str(val1))

    """

    if old_fct_extractor.is_method:
        main_code_template = main_code_template.replace("INVOCATION1",
                                                        "Wrapper1()." + old_fct_extractor.function.name.value + "_old(" + ", ".join(
                                                            old_fct_extractor.param_names[1:]) + ")")
        main_code_template = main_code_template.replace("INVOCATION2",
                                                        "Wrapper2()." + new_fct_extractor.function.name.value + "_new(" + ", ".join(
                                                            new_fct_extractor.param_names[1:]) + ")")
    else:
        main_code_template = main_code_template.replace("INVOCATION1",
                                                        old_fct_extractor.function.name.value + "_old(" + ", ".join(
                                                            old_fct_extractor.param_names) + ")")
        main_code_template = main_code_template.replace("INVOCATION2",
                                                        new_fct_extractor.function.name.value + "_new(" + ", ".join(
                                                            new_fct_extractor.param_names) + ")")

    comment = f"# {commit['old_commit']} -- {commit['new_commit']}\n\n"

    all_code = comment + fct_def_code + "\n\n" + main_code_template
    file_name = join(dest_dir, "compare.py")
    with open(file_name, "w", encoding='utf-8') as f:
        f.write(all_code)

# Copied From original LExecutor
def extract_function(function):
    tree = cst.parse_module(function)
    tree = cst.MetadataWrapper(tree)
    extractor = FunctionExtractor(1)
    tree.visit(extractor)
    return extractor

# Copied From original LExecutor
def extract_function_pair(commit, dest_dir):
    # get old function
    old_function_extractor = extract_function(commit['old_clean_function'])

    # get new function
    new_function_extractor = extract_function(commit['new_clean_function'])

    if old_function_extractor.function is None or new_function_extractor.function is None:
        raise ValueError('Function to extract is __init__')

    if old_function_extractor.is_method != new_function_extractor.is_method:
        return

    # write original functions into files
    # write_function_to_file(old_function_extractor.function, dest_dir, "old", code_change)
    # write_function_to_file(new_function_extractor.function, dest_dir, "new", code_change)

    # write both functions to a single file that invokes and compares them
    write_function_comparison_script(old_function_extractor, new_function_extractor, dest_dir, commit)

    print(f"Extracted function pair to {dest_dir}")


def instrument_commit(commit, dest_dir):
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    try:
        extract_function_pair(commit, dest_dir)
    except Exception as e:
        print(
            f"Something went wrong when extracting from code change {commit['repo']}_{commit['source']}_{commit['sha']} -- ignoring  {e}")
    else:
        # instrument them
        script_path = os.path.abspath(os.path.join(dest_dir, 'compare.py'))
        print(script_path)
        subprocess.run(f'python -m lexecutor.Instrument --files {script_path} --verbose', cwd=os.path.abspath('./src'),
                       shell=True)


def run_commit(commit, dest_dir):
    start = time.time()
    script_path = os.path.abspath(os.path.join(dest_dir, 'compare.py'))

    # get line offsets
    with open(script_path + ".orig", 'r', encoding='utf-8') as f:
        compare_script = f.read()
        offsets = get_offsets(compare_script)
    iterations = {}
    successful = False
    for i in range(1, 501):
        try:
            completed_process = subprocess.run(f'python {script_path}', cwd=os.path.abspath('./src'), capture_output=True, shell=True, timeout=60)
            output, error = completed_process.stdout.decode('utf-8'), completed_process.stderr.decode('utf-8')
        except subprocess.TimeoutExpired:
            output, error = '', 'timeout'

        if output and 'Function(s) raised an exception' not in output:
            successful = True
        old_executed_lines, new_executed_lines = extract_executed_lines(error, offsets)
        iterations[f'iteration_{i}'] = {'out': output, 'err': error, 'old_executed_lines': old_executed_lines, 'new_executed_lines': new_executed_lines}

    old_tot_executed_lines = list(
        set().union(*(set(it['old_executed_lines']) for it in iterations.values())))
    new_tot_executed_lines = list(
        set().union(*(set(it['new_executed_lines']) for it in iterations.values())))
    logger.info(f'Total time: {time.time() - start} seconds')
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
    with open(args.commits) as f:
        commits = json.load(f)
    outputs = []
    logger.info(f'Started: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
    for commit in commits:
        identifier = f"{commit['repo']}_{commit['source']}_{commit['sha']}"
        dest_dir = join(args.dest, identifier)
        if args.action == 'instrument':
            instrument_commit(commit, dest_dir)
        if args.action == 'run':
            outputs.append(run_commit(commit, dest_dir))
            with open('std_out.json', 'w') as f:
                json.dump(outputs, f, indent=4)
    logger.info(f'Finished: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
