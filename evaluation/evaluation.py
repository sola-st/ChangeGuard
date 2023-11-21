import json


def evaluate_annotated_changes():
    with open('../annotated_changes/annotated_changes_old.json') as f:
        annotated_changes = json.load(f)

    preserving_changes = [change for change in annotated_changes if change['annotation'] == 'semantics_preserving']
    changing_changes = [change for change in annotated_changes if change['annotation'] == 'semantics_changing']
    print('Num Semantics_Preserving:', len(preserving_changes), 'Num Semantics_Changing:', len(changing_changes))
    source_refactor = [change for change in annotated_changes if change['source'] == 'refactor']
    source_change = [change for change in annotated_changes if change['source'] == 'change']
    print('Num Source_Refactor:', len(source_refactor), 'Num Source_Change:', len(source_change))
    incorrect_source_refactor = [change for change in source_refactor if change['annotation'] == 'semantics_changing']
    incorrect_source_change = [change for change in source_change if change['annotation'] == 'semantics_preserving']
    print('Num Incorrect_Refactor:', len(incorrect_source_refactor), 'Num Incorrect_Change:', len(incorrect_source_change))
    pandas_preserving = [change for change in annotated_changes if change['annotation'] == 'semantics_preserving' and change['repo'] == 'pandas']
    pandas_total = [change for change in annotated_changes if change['repo'] == 'pandas']
    print('Pandas Total:', len(pandas_total), 'Pandas Preserving:', len(pandas_preserving))
    # 3x instrumented code cannot be LExecuted because instrumentation is incorrect


def evaluate_stdout():
    with open('../annotated_changes/stdout.json') as f:
        outputs = json.load(f)
    error_outputs = [output for output in outputs if 'Function(s) raised an exception' in output['out']]
    print('Total', len(outputs))
    print('Num Commits_Exception', len(error_outputs))
    error_per_repo = {repo: len(list(filter(lambda x: x['repo'] == repo, error_outputs))) for repo in set(map(lambda x: x['repo'], error_outputs))}
    print(error_per_repo)
    preserving_outputs = [output for output in outputs if 'Both functions returned the same value' in output['out']]
    print('Num Commits_Preserving', len(preserving_outputs))
    changing_outputs = [output for output in outputs if 'Functions returned different values' in output['out']]
    print('Num Commits_Changing', len(changing_outputs))
    print('Num timeouts', len([output for output in outputs if output['err'] == 'timeout']))
    print('Num Failed_Function_Extraction (__init__)', len([output for output in outputs if "python: can't open file" in output['err']]))


if __name__ == '__main__':
    # evaluate_annotated_changes()
    evaluate_stdout()
