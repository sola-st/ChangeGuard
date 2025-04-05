import json


tests_verdicts = [
    '../evaluation/regression_tests/black_tests_verdict.json',
    
    '../evaluation/regression_tests/fastapi_github_verdict.json',
    '../evaluation/regression_tests/fastapi_tests_verdict.json',
    '../evaluation/regression_tests/flask_github_verdict.json',

    '../evaluation/regression_tests/poetry_github_verdict.json',
    '../evaluation/regression_tests/poetry_tests_verdict.json',

    '../evaluation/regression_tests/cli_tests_verdict.json',
    '../evaluation/regression_tests/scikit_learn_github_verdict.json',
    '../evaluation/regression_tests/pandas_github_verdict.json',
    '../evaluation/regression_tests/scrapy_github_verdict.json',
    '../evaluation/regression_tests/airflow_github_verdict.json',
]


if __name__ == '__main__':
    tp, fp, fn, tn = [], [], [], []
    tpl, fpl, fnl, tnl = [], [], [], []
    
    ANNOTATED_CHANGES = r'../LExecutorCC/annotated_changes.json'
    ANALYZED_ANNOTATED_CHANGES = []
    with open(ANNOTATED_CHANGES, 'r', encoding='utf-8') as f:
        changes = json.load(f)

        # tests results
        for file in tests_verdicts:
            with open(file, 'r', encoding='utf-8') as f:
                verdicts = json.load(f)

                for verdict in verdicts:
                    if 'github' not in file:
                        try:
                            # Both commits had tests executed
                            int(verdict["old_commit_passing"]) 
                            int(verdict["new_commit_passing"])
                        except:
                            continue

                    for change in changes:
                        if change['annotation'] == 'unclear':
                            continue
                        if change["repo"] == verdict["repo"] and change["sha"] == verdict["sha"]:
                            ANALYZED_ANNOTATED_CHANGES.append(change)

                            if verdict["final_result"] == "changing":
                                if change["annotation"] == "semantics_changing":
                                    tp.append(verdict)
                                    print(verdict["repo"])
                                    print(verdict["sha"])
                                else:
                                    fp.append(verdict)

                            elif verdict["final_result"] == "preserving":
                                if change["annotation"] == "semantics_preserving":
                                    tn.append(verdict)
                                else:
                                    fn.append(verdict)

    total_semantics_preserving = len([1 for change in ANALYZED_ANNOTATED_CHANGES if change['annotation'] == 'semantics_preserving'])
    total_semantics_changing = len([1 for change in ANALYZED_ANNOTATED_CHANGES if change['annotation'] == 'semantics_changing'])
    total_unclear = len([1 for change in ANALYZED_ANNOTATED_CHANGES if change['annotation'] == 'unclear'])
    
    with open('../evaluation/regression_tests/fp.json', 'w') as f:
        json.dump(fp, f, indent=4)
    with open('../evaluation/regression_tests/fn.json', 'w') as f:
        json.dump(fn, f, indent=4)
    with open('../evaluation/regression_tests/tp.json', 'w') as f:
        json.dump(tp, f, indent=4)
    with open('../evaluation/regression_tests/tn.json', 'w') as f:
        json.dump(tn, f, indent=4)
    
    print('Number annotated', f'preserving: {total_semantics_preserving}', f'changing: {total_semantics_changing}', f'unclear: {total_unclear}')
    print("Tests:")
    print('tp:', len(tp), 'fp:', len(fp), 'fn:', len(fn), 'tn:', len(tn))



                            
                            
                            
