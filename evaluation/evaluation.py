import json
import os
from typing import List
import re
import time
import matplotlib.pyplot as plt

REPO_PATH = r'../Repos'
REPOS: List[str] = [entry.name for entry in os.scandir(REPO_PATH) if entry.is_dir()]

def evaluate_annotated_changes():
    with open(ANNOTATED_CHANGES) as f:
        annotated_changes = json.load(f)

    preserving_changes = [change for change in annotated_changes if change['annotation'] == 'semantics_preserving']
    changing_changes = [change for change in annotated_changes if change['annotation'] == 'semantics_changing']
    unclear_changes = [change for change in annotated_changes if change['annotation'] == 'unclear']
    unclear_refactor_changes = [change for change in annotated_changes if change['annotation'] == 'unclear' and change['source'] == 'refactor']
    unclear_change_changes = [change for change in annotated_changes if change['annotation'] == 'unclear' and change['source'] == 'change']
    unclear_dict = {key: len([change for change in unclear_changes if change['repo'] == key]) for key in {change['repo'] for change in unclear_changes}}
    print('Num Semantics_Preserving:', len(preserving_changes), 'Num Semantics_Changing:', len(changing_changes))
    source_refactor = [change for change in annotated_changes if change['source'] == 'refactor']
    source_change = [change for change in annotated_changes if change['source'] == 'change']
    print('Num Source_Refactor:', len(source_refactor), 'Num Source_Change:', len(source_change))
    incorrect_source_refactor = [change for change in source_refactor if change['annotation'] == 'semantics_changing']
    incorrect_source_change = [change for change in source_change if change['annotation'] == 'semantics_preserving']
    print('Num Unclear', len(unclear_changes))
    print('Num Unclear_Refactor', len(unclear_refactor_changes))
    print('Num Unclear_Change', len(unclear_change_changes))
    print('Num Unclear_Per_Repo:', unclear_dict)
    print('Num Incorrect_Refactor:', len(incorrect_source_refactor), 'Num Incorrect_Change:', len(incorrect_source_change))
    changes_with_side_effects_total = [change for change in annotated_changes if not re.search('(return .*$)|(yield .*$)', change['old_clean_function'], re.MULTILINE) or not re.search('(return .*$)|(yield .*$)', change['new_clean_function'], re.MULTILINE)]
    print('Num Side_Effect_Only', len(changes_with_side_effects_total))
    print('Num Side_Effect_Only_Changing', len([change for change in changes_with_side_effects_total if change['annotation'] == 'semantics_changing']))
    print('Num Side_Effect_Only_Preserving', len([change for change in changes_with_side_effects_total if change['annotation'] == 'semantics_preserving']))

    print(f'{"Repo":^12} | Total | Refactor | Change | Preserving | Changing | Unclear')
    print('--------------------------------------------------------------------------')
    for repo in REPOS:
        repo_total = [change for change in annotated_changes if change['repo'] == repo.lower()]
        repo_refactor = [change for change in repo_total if change['source'] == 'refactor']
        repo_change = [change for change in repo_total if change['source'] == 'change']
        repo_preserving = [change for change in repo_total if change['annotation'] == 'semantics_preserving']
        repo_changing = [change for change in repo_total if change['annotation'] == 'semantics_changing']
        repo_unclear = [change for change in repo_total if change['annotation'] == 'unclear']
        print(f'{repo:^12} | {len(repo_total):^5} | {"{:02d}".format(len(repo_refactor)):^8} | {"{:02d}".format(len(repo_change)):^6} | {"{:02d}".format(len(repo_preserving)):^10} | {"{:02d}".format(len(repo_changing)):^8} | {"{:02d}".format(len(repo_unclear)):^7}')


def evaluate_stdout():
    with open('../annotated_changes/stdout_baseline.json') as f:
        outputs = json.load(f)
    error_outputs = [output for output in outputs if 'Function(s) raised an exception' in output['out']]
    print('Total', len(outputs))
    print('Num Commits_Exception', len(error_outputs))
    error_per_repo = {repo: len(list(filter(lambda x: x['repo'] == repo, error_outputs))) for repo in set(map(lambda x: x['repo'], error_outputs))}
    print('Num Error_Per_Repo', error_per_repo)
    preserving_outputs = [output for output in outputs if 'Both functions returned the same value' in output['out']]
    print('Num Commits_Preserving', len(preserving_outputs))
    changing_outputs = [output for output in outputs if 'Functions returned different values' in output['out']]
    print('Num Commits_Changing', len(changing_outputs))
    print('Num timeouts', len([output for output in outputs if output['err'] == 'timeout']))
    print('Num Failed_Function_Extraction (__init__)', len([output for output in outputs if "python: can't open file" in output['err']]))
    annotated_preserving_outputs = [output for output in outputs if output['annotation'] == 'semantics_preserving']
    annotated_preserving_outputs_exception = [output for output in annotated_preserving_outputs if 'Function(s) raised an exception' in output['out']]
    annotated_preserving_outputs_preserving = [output for output in annotated_preserving_outputs if 'Both functions returned the same value' in output['out']]
    annotated_preserving_outputs_changing = [output for output in annotated_preserving_outputs if 'Functions returned different values' in output['out']]
    print('Annotated Preserving:')
    print(' total:', len(annotated_preserving_outputs), '| exception:', len(annotated_preserving_outputs_exception), '| preserving:', len(annotated_preserving_outputs_preserving), '| changing:', len(annotated_preserving_outputs_changing))
    annotated_changing_outputs = [output for output in outputs if output['annotation'] == 'semantics_changing']
    annotated_changing_outputs_exception = [output for output in annotated_changing_outputs if 'Function(s) raised an exception' in output['out']]
    annotated_changing_outputs_preserving = [output for output in annotated_changing_outputs if 'Both functions returned the same value' in output['out']]
    annotated_changing_outputs_changing = [output for output in annotated_changing_outputs if 'Functions returned different values' in output['out']]
    print('Annotated Changing:')
    print(' total:', len(annotated_changing_outputs), '| exception:', len(annotated_changing_outputs_exception), '| preserving:', len(annotated_changing_outputs_preserving), '| changing:', len(annotated_changing_outputs_changing))
    annotated_unclear_outputs = [output for output in outputs if output['annotation'] == 'unclear']
    annotated_unclear_outputs_exception = [output for output in annotated_unclear_outputs if 'Function(s) raised an exception' in output['out']]
    annotated_unclear_outputs_preserving = [output for output in annotated_unclear_outputs if 'Both functions returned the same value' in output['out']]
    annotated_unclear_outputs_changing = [output for output in annotated_unclear_outputs if 'Functions returned different values' in output['out']]
    print('Annotated Unclear:')
    print(' total:', len(annotated_unclear_outputs), '| exception:', len(annotated_unclear_outputs_exception), '| preserving:', len(annotated_unclear_outputs_preserving), '| changing:', len(annotated_unclear_outputs_changing))
    print([output['out'] for output in outputs if output['err'].count('Predicting for') == 0])
    num_lexecutions = [output['err'].count('Predicting for') for output in outputs if  output['out'] != '']
    print('Avarage_Num_LExections:', sum(num_lexecutions)/len(num_lexecutions))


def evaluate_coverage():
    with open('../annotated_changes/stdout_SuperObject.json') as f:
        outputs = json.load(f)
    covered_lines = [entry['err'].split('Lines executed: ')[1] for entry in outputs if 'Lines executed: ' in entry['err']]
    covered_lines = [entry[:entry._index(']') + 1] for entry in covered_lines]
    print(covered_lines)
    covered_lines = [[int(line) for line in entry.strip('[]').split(', ')] for entry in covered_lines]
    print((sum(map(lambda x: len(x), covered_lines)))/len(covered_lines))


def evaluate_iter():
    with open(JSON_PATH, 'r') as f:
        outputs = json.load(f)
    print('Final Result Preserving', len([output for output in outputs if output['final_result'] == 'preserving']))
    print('Final Result Changing', len([output for output in outputs if output['final_result'] == 'changing']))
    print('Final Result Error', len([output for output in outputs if output['final_result'] == 'non_conclusive']))
    nb_lines_covered = 0
    for output in (output for output in outputs):
        iterations = [o['err'] for o in output['iterations'].values()]
        covered_lines = [iteration.split('Lines executed: ')[1] for iteration in iterations if 'Lines executed: ' in iteration]
        covered_lines = [entry[:entry._index(']') + 1] for entry in covered_lines]
        covered_lines = [{int(line) for line in entry.strip('[]').split(', ')} for entry in covered_lines]
        unique_lines = set().union(*covered_lines)
        # print(unique_lines)
        # print(len(unique_lines))
        nb_lines_covered += len(unique_lines)
    print(nb_lines_covered / len(outputs))


def get_final_results():
    with open(JSON_PATH, 'r') as f:
        results = json.load(f)
    results = [result['final_result'] for result in results]
    print('Number preserving:', results.count('preserving'))
    print('Number changing:', results.count('changing'))
    print('Number non_conclusive:', results.count('non_conclusive'))


def get_errors():
    with open(ANNOTATED_CHANGES, 'r') as f:
        changes = json.load(f)
    preserving_error, changing_error, unclear_error = [], [], []
    sha_to_change = {change['sha']: change for change in changes}
    with open(JSON_PATH, 'r') as f:
        results = json.load(f)
    for result in results:
        if result['final_result'] == 'non_conclusive':
            change = sha_to_change[result['sha']]
            annotation = change['annotation']
            if annotation == 'semantics_preserving':
                preserving_error.append(change)
            elif annotation == 'semantics_changing':
                changing_error.append(change)
            else:
                unclear_error.append(change)
    print('preserving error', len(preserving_error), 'changing error', len(changing_error), 'unclear error', len(unclear_error))

    results = [result['iterations'] for result in results]
    errors = {}
    for result in results:
        for value in result.values():
            out = value['out']
            match = re.search('raised .* exception: (.*?) --', out)
            if match:
                error = match.group(1)
                errors[error] = errors.get(error, 0) + 1
    print('\n'.join(map(str, sorted(errors.items(), key=lambda x: x[1], reverse=True))))
    #print(json.dumps(errors, indent=2))


def get_timing_profile():
    with open(LOG_PATH, 'r') as f:
        lines = f.read().splitlines()
    start_time = lines[0]
    end_time = lines[-1]
    fmt = '%Y-%m-%d %H:%M:%S'
    print(f'Full Duration: {time.mktime(time.strptime(end_time.split(": ")[2], fmt)) - time.mktime(time.strptime(start_time.split(": ")[2], fmt))}s')
    print(f'Time spent executing compare scripts: {sum(float(line.split(" ")[4]) for line in lines[1:-1] if "iteration" in line )}s')


def evaluate_run_log():
    with open(r'C:\Users\Lars\Uni\Master\Masterarbeit\history\isinstance_mock\LExecutorCC\logs\run.log', 'r') as f:
        lines = f.read().splitlines()
    print(sum(float(line.split(' ')[2]) for line in lines[1:-1]))


def get_changing_commits():
    with open(r'C:\Users\Lars\Uni\Master\Masterarbeit\master-thesis-lars-groeninger\annotated_changes\annotated_changes.json', 'r') as f:
        commits = json.load(f)
    commits = [commit for commit in commits if commit['annotation'] == 'semantics_changing' and 'return' in commit['old_clean_function']]
    with open(r'changes.json', 'w') as f:
        json.dump(commits, f, indent=4)


def foo():
    with open(ANNOTATED_CHANGES, 'r', encoding='utf-8') as f:
        changes = json.load(f)
    sha_to_change = {change['sha']: change for change in changes}
    with open(r'C:\Users\Lars\Uni\Master\Masterarbeit\history\call_args\LExecutorCC\std_out.json') as f:
        out = json.load(f)
    counter = 0
    important = []
    for o in out:
        if o['final_result'] == 'preserving' and sha_to_change[o['sha']]['annotation'] == 'semantics_changing':
            counter += 1
            important.append(sha_to_change[o['sha']])
    print(f'Errors that would be changing: {counter}')
    with open('important.json', 'w') as f:
        json.dump(important, f, indent=4)


def get_undetected_changes():
    with open(ANNOTATED_CHANGES, 'r', encoding='utf-8') as f:
        changes = json.load(f)
    sha_to_change = {change['sha']: change for change in changes}
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        out = json.load(f)
    undetected_changes = []
    for result in out:
        change = sha_to_change[result['sha']]
        # # annotated changing, but false negative
        # if change['annotation'] == 'semantics_changing' and result['final_result'] == 'preserving':
        # changed lines covered but change not detected
        if result['final_result'] != 'non_conclusive' and result['coverage']['old']['ratio'] == 0 and result['coverage']['new']['ratio'] == 0:
            undetected_changes.append(change)
    print('Undetected:', len(undetected_changes))
    with open('undetected_changes.json', 'w') as f:
        json.dump(undetected_changes, f, indent=4)


def get_confusion_matrix():
    with open(ANNOTATED_CHANGES, 'r', encoding='utf-8') as f:
        changes = json.load(f)
    sha_to_change = {change['sha']: change for change in changes}
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        out = json.load(f)
    tp, fp, fn, tn, nrc, nrp = [], [], [], [], [], []
    for result in out:
        change = sha_to_change[result['sha']]
        if change['annotation'] == 'unclear':
            continue
        if result['final_result'] == 'changing':
            if change['annotation'] == 'semantics_changing':
                tp.append(change)
            else:
                fp.append(change)
        elif result['final_result'] == 'preserving':
            if change['annotation'] == 'semantics_changing':
                fn.append(change)
            else:
                tn.append(change)
        elif result['final_result'] == 'not_reached':
            if change['annotation'] == 'semantics_changing':
                nrc.append(change)
            else:
                nrp.append(change)

    total_semantics_preserving = len([1 for change in changes if change['annotation'] == 'semantics_preserving'])
    total_semantics_changing = len([1 for change in changes if change['annotation'] == 'semantics_changing'])
    total_unclear = len([1 for change in changes if change['annotation'] == 'unclear'])
    with open('./accuracy/fp.json', 'w') as f:
        json.dump(fp, f, indent=4)
    with open('./accuracy/fn.json', 'w') as f:
        json.dump(fn, f, indent=4)
    with open('./accuracy/tp.json', 'w') as f:
        json.dump(tp, f, indent=4)
    with open('./accuracy/tn.json', 'w') as f:
        json.dump(tn, f, indent=4)
    with open('./accuracy/nrc.json', 'w') as f:
        json.dump(nrc, f, indent=4)
    with open('./accuracy/nrp.json', 'w') as f:
        json.dump(nrp, f, indent=4)
    print(total_semantics_preserving, total_semantics_changing, total_unclear)
    print('tp:', len(tp), 'fp:', len(fp), 'fn:', len(fn), 'tn:', len(tn), 'nrc:', len(nrc), 'nrp:', len(nrp))
    print('not_reached:', len([x for x in out if x['final_result'] == 'not_reached']))


def get_only_one_exception():
    with open(JSON_PATH, 'r') as f:
        j = json.load(f)
    only_results = []
    for result in j:
        for idx in range(1, 301):
            iteration = result['iterations'].get(f'iteration_{idx}')
            if iteration is None:
                break
            if iteration['out'].startswith('only'):
                only_results.append(result)
                break
    print(len(only_results))
    with open('only.json', 'w') as f:
        json.dump(only_results, f, indent=4)


def get_length_of_functions():
    with open(ANNOTATED_CHANGES, 'r', encoding='utf-8') as f:
        changes = json.load(f)
    sha_to_change = {change['sha']: change for change in changes}

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        results = json.load(f)
    reached_lens = []
    for result in results:
        if result['final_result'] != 'not_reached':
            change = sha_to_change[result['sha']]
            lines = change['old_clean_function'].splitlines()
            reached_lens.append(len(lines))
    print('Total Average:', sum(reached_lens)/len(reached_lens))


    not_reached_lens = []
    for result in results:
        if result['final_result'] == 'not_reached':
            change = sha_to_change[result['sha']]
            lines = change['old_clean_function'].splitlines()
            not_reached_lens.append(len(lines))
    print(sum(not_reached_lens)/len(not_reached_lens))
    return reached_lens, not_reached_lens


def get_complexity():
    with open(ANNOTATED_CHANGES, 'r', encoding='utf-8') as f:
        changes = json.load(f)
    sha_to_change = {change['sha']: change for change in changes}
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        results = json.load(f)
    reached_functions = []
    not_reached_functions = []
    for result in results:
        change = sha_to_change[result['sha']]
        if result['final_result'] != 'not_reached':
            reached_functions.append(change['old_clean_function'])
        else:
            not_reached_functions.append(change['old_clean_function'])
    if not os.path.exists('./complexity'):
        os.mkdir('./complexity')
    with open('./complexity/reached.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(reached_functions))
    with open('./complexity/not_reached.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(not_reached_functions))

def get_complexity_box_plots():
    with open('complexity/reached.txt', 'r') as f:
        lines = f.readlines()
    reached_complexity = [int(re.search('\\(([0-9]+)\\)', line).group(1)) for line in lines]
    print(sum(reached_complexity)/len(reached_complexity))
    with open('./complexity/not_reached.txt', 'r') as f:
        lines = f.readlines()
    not_reached_complexity = [int(re.search('\\(([0-9]+)\\)', line).group(1)) for line in lines]
    print(sum(not_reached_complexity) / len(not_reached_complexity))
    return reached_complexity, not_reached_complexity


def get_boxplots():
    reached_lens, not_reached_lens = get_length_of_functions()
    reached_complexity, not_reached_complexity = get_complexity_box_plots()
    fig, axs = plt.subplots(2, 2, figsize=(12, 6))
    axs[0, 0].boxplot([reached_lens, not_reached_lens], showfliers=False, showmeans=True, meanline=True, vert=True)
    axs[0, 0].set_title('No Outliers', fontsize=16)
    axs[0, 0].set_ylabel("Number of Lines", fontsize=14, labelpad=9)
    axs[0, 0].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    axs[0, 1].boxplot([reached_lens, not_reached_lens], showfliers=True, showmeans=True, meanline=True, vert=True)
    axs[0, 1].set_title('Outliers', fontsize=16)
    axs[0, 1].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

    axs[1, 0].boxplot([reached_complexity, not_reached_complexity], showfliers=False, showmeans=True, meanline=True, vert=True)
    axs[1, 0].set_xticklabels(['Reached', 'Not Reached'])
    axs[1, 0].set_ylabel("Cyclomatic Complexity", fontsize=14, labelpad=9)
    axs[1, 0].tick_params(axis='x', labelsize=14)
    bp = axs[1, 1].boxplot([reached_complexity, not_reached_complexity], showfliers=True, showmeans=True, meanline=True, vert=True)
    axs[1, 1].set_xticklabels(['Reached', 'Not Reached'])
    axs[1, 1].tick_params(labelsize=13)
    fig.legend([bp['means'][0], bp['medians'][0], bp['fliers'][0]], ['Mean', 'Median', 'Outlier'], loc='upper center', shadow=False, ncol=3, fontsize=14)
    fig.subplots_adjust(hspace=0.05)
    for ax in axs.flat:
        ax.tick_params(axis='y', which='both', labelsize=12)

    fig.savefig('./complexity/boxplot.pdf', bbox_inches='tight', dpi=1200)
    fig.show()

if __name__ == '__main__':
    prefix = r'C:\Users\Lars\Uni\Master\Masterarbeit\history\call_args'
    ANNOTATED_CHANGES = r'C:\Users\Lars\Uni\Master\Masterarbeit\master-thesis-lars-groeninger\LExecutorCC\annotated_changes.json'
    JSON_PATH = rf'C:\Users\Lars\Uni\Master\Masterarbeit\history\final_questionmark\std_out.json'
    LOG_PATH = rf'{prefix}\LExecutorCC\logs\Runner.log'
    # evaluate_annotated_changes()
    evaluate_stdout()
    # evaluate_coverage()
    # evaluate_run_log()
    # evaluate_iter()
    # get_final_results()
    # get_errors()
    # get_timing_profile()
    # get_changing_commits()
    # foo()
    # get_undetected_changes()
    # get_confusion_matrix()
    # get_only_one_exception()
    # get_length_of_functions()
    # get_complexity()
    # get_complexity_box_plots()
    # get_boxplots()
