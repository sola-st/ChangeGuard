import json
import os
from typing import List
import re
import matplotlib.pyplot as plt

REPO_PATH = r'../repos'
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


def get_final_results():
    with open(r'accuracy/std_out.json', 'r') as f:
        results = json.load(f)
    results = [result['final_result'] for result in results]
    print('Number identified as preserving:', results.count('preserving'))
    print('Number identified as changing:', results.count('changing'))
    print('Number identified as non_conclusive:', results.count('non_conclusive'))
    print('Number identified as not_reached:', results.count('not_reached'))


def get_errors():
    with open(ANNOTATED_CHANGES, 'r') as f:
        changes = json.load(f)
    preserving_error, changing_error, unclear_error = [], [], []
    sha_to_change = {change['sha']: change for change in changes}
    with open(r'accuracy/std_out.json', 'r') as f:
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


def get_confusion_matrix():
    with open(ANNOTATED_CHANGES, 'r', encoding='utf-8') as f:
        changes = json.load(f)
    sha_to_change = {change['sha']: change for change in changes}
    with open(r'accuracy/std_out.json', 'r', encoding='utf-8') as f:
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
    print('Number annotated', f'preserving: {total_semantics_preserving}', f'changing: {total_semantics_changing}', f'unclear: {total_unclear}')
    print('tp:', len(tp), 'fp:', len(fp), 'fn:', len(fn), 'tn:', len(tn), 'nrc:', len(nrc), 'nrp:', len(nrp))
    print('not_reached:', len([x for x in out if x['final_result'] == 'not_reached']))


def get_length_of_functions():
    with open(ANNOTATED_CHANGES, 'r', encoding='utf-8') as f:
        changes = json.load(f)
    sha_to_change = {change['sha']: change for change in changes}

    with open(r'accuracy/std_out.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    reached_lens = []
    for result in results:
        if result['final_result'] != 'not_reached':
            change = sha_to_change[result['sha']]
            lines = change['old_clean_function'].splitlines()
            reached_lens.append(len(lines))
    print('Reached Average:', sum(reached_lens)/len(reached_lens))

    not_reached_lens = []
    for result in results:
        if result['final_result'] == 'not_reached':
            change = sha_to_change[result['sha']]
            lines = change['old_clean_function'].splitlines()
            not_reached_lens.append(len(lines))
    print('Not Reached Average:', sum(not_reached_lens)/len(not_reached_lens))
    return reached_lens, not_reached_lens


def create_functions_py():
    with open(ANNOTATED_CHANGES, 'r', encoding='utf-8') as f:
        changes = json.load(f)
    sha_to_change = {change['sha']: change for change in changes}
    with open(r'accuracy/std_out.json', 'r', encoding='utf-8') as f:
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


def get_complexity():
    with open('complexity/reached.txt', 'r') as f:
        lines = f.readlines()
    reached_complexity = [int(re.search('\\(([0-9]+)\\)', line).group(1)) for line in lines]
    print(sum(reached_complexity)/len(reached_complexity))
    with open('./complexity/not_reached.txt', 'r') as f:
        lines = f.readlines()
    not_reached_complexity = [int(re.search('\\(([0-9]+)\\)', line).group(1)) for line in lines]
    print(sum(not_reached_complexity) / len(not_reached_complexity))
    return reached_complexity, not_reached_complexity


def get_complexity_boxplots():
    reached_lens, not_reached_lens = get_length_of_functions()
    reached_complexity, not_reached_complexity = get_complexity()
    fig, axs = plt.subplots(2, 2, figsize=(8, 8))
    axs[0, 0].boxplot([reached_lens, not_reached_lens], showfliers=False, showmeans=True, meanline=True, vert=True)
    axs[0, 0].set_title('Without Outliers', fontsize=16)
    axs[0, 0].set_ylabel("Number of Lines", fontsize=14, labelpad=9)
    axs[0, 0].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    axs[0, 1].boxplot([reached_lens, not_reached_lens], showfliers=True, showmeans=True, meanline=True, vert=True)
    axs[0, 1].set_title('With Outliers', fontsize=16)
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


def draw_robustness_plot():
    bars = [122, 257]
    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.5, 0.5])
    axes.spines['top'].set_visible(False)
    axes.spines['right'].set_visible(False)
    axes.spines['left'].set_visible(False)

    axes.spines['bottom'].set_color('#DDDDDD')
    axes.set_axisbelow(True)
    axes.yaxis.grid(True, color='#CCCCCC')
    axes.xaxis.grid(False)
    axes.tick_params(axis='y', color='#CCCCCC')
    axes.tick_params(bottom=False)
    bs = axes.bar([1, 2], bars, color='#00689d')
    for bar in bs:
        axes.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 3.9,
            round(bar.get_height(), 1),
            horizontalalignment='center',
            color='#00689d',
            weight='bold'
        )
    axes.set_xlim(0.5, 2.5)
    axes.plot([0, 3], [299, 299], '--', color=(0., 0., 0.))
    axes.set_xticks([1, 2], ['Baseline', 'LExecutorCC'])
    axes.tick_params(axis='x', labelsize=12)
    axes.set_yticks([0, 50, 100, 150, 200, 250, 299])
    axes.set_ylabel('Number of successful code changes', fontsize=10.5)
    fig.savefig('./coverage/robustness.pdf', bbox_inches='tight', dpi=1200)
    fig.show()


def get_coverage():
    with open(r'coverage/std_out_baseline.json', 'r', encoding='utf-8') as f:
        baseline = json.load(f)
    with open(r'coverage/std_out_approach.json', 'r', encoding='utf-8') as f:
        approach = json.load(f)
    with open(ANNOTATED_CHANGES, 'r', encoding='utf-8') as f:
        changes = json.load(f)
    sha_to_change = {change['sha']: change for change in changes}
    baseline_tot_covered = 0
    baseline_tot_lines = 0
    baseline_ratios = []
    approach_ratios = []
    for result in zip(baseline, approach):
        # comment out to obtain coverage across all code changes not just successful
        if not result[0]['successful']:
            continue
        change = sha_to_change[result[0]['sha']]
        lines = len(change['old_clean_function'].splitlines())
        print('all:', lines)
        approach_covered = len(set(result[1]['coverage']['old']['executed_lines']))
        baseline_covered = len(set(result[0]['old_tot_executed_lines']))
        print('covered:', baseline_covered, approach_covered)
        baseline_tot_covered += baseline_covered
        baseline_tot_lines += lines
        baseline_ratios.append(baseline_covered/lines)
        approach_ratios.append(approach_covered/lines)
    print(baseline_tot_covered)
    print('RATIO:', baseline_tot_covered/baseline_tot_lines)
    print('AVG', sum(baseline_ratios)/len(baseline_ratios))
    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.5, 0.5])
    bp = axes.boxplot([baseline_ratios, approach_ratios], showfliers=True, showmeans=True, meanline=True)
    axes.tick_params(axis='y', labelsize=12)
    axes.set_ylabel('Lines Covered (%)', fontsize=13, labelpad=9)
    axes.set_xticks([1, 2], ['Baseline', 'LExecutorCC'])
    axes.tick_params(axis='x', labelsize=12)
    axes.legend([bp['means'][0], bp['medians'][0], bp['fliers'][0]], ['Mean', 'Median', 'Outlier'], loc='upper center',
               shadow=False, ncol=3, fontsize=12 , bbox_to_anchor=(0.5, 1.2), )
    axes.tick_params(bottom=False)
    fig.show()
    fig.savefig('./coverage/coverage.pdf', bbox_inches='tight', dpi=1200)


def draw_box_plot(data, name, label):
    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.5, 0.5])
    bp = axes.boxplot(data, showfliers=False, showmeans=True, meanline=True)
    axes.tick_params(axis='y', labelsize=12)
    axes.set_ylabel(label, fontsize=14, labelpad=9)
    axes.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    axes.set_ylim([0,3.07])
    axes.legend([bp['means'][0], bp['medians'][0]], ['Mean', 'Median'], loc='upper center',
               shadow=False, ncol=3, fontsize=14 , bbox_to_anchor=(0.5, 1.2))
    fig.show()
    fig.savefig(f'./efficiency/{name}.pdf', bbox_inches='tight', dpi=1200)


def get_time_data():

    with open(r'efficiency/Instrumentation.log', 'r') as f:
        log = f.read().splitlines()
    times = [float(re.search('([0-9]+(?:.[0-9]+|))', line).group(1)) for line in log if 'took:' in line]
    print('MAX INSTRUMENTATION:', max(times))
    print('AVERAGE INSTRUMENTATION:', sum(times)/len(times))
    draw_box_plot(times, 'instrumentation_plot', 'Instrumentation Time (s)')

    with open(r'efficiency/Runner.log', 'r') as f:
        log = f.read().splitlines()

    first_iterations = [line for line in log if "iteration_1 " in line]
    first_iterations = [float(re.search('([0-9]+(?:.[0-9]+|)) seconds', line).group(1)) for line in first_iterations]
    first_iterations[0] -= 10  # adjust for time it takes for model server to start
    print('AVG FIRST:', sum(first_iterations)/len(first_iterations))
    draw_box_plot(first_iterations, 'first_iter_plot', 'Lexecution Time (s)')
    #print(sorted(first_iterations, reverse=True))
    remaining_iterations = [line for line in log if re.search('iteration_(?:[023456789]|1[0-9]+)', line)]
    remaining_iterations = [float(re.search('([0-9]+(?:.[0-9]+|)) seconds', line).group(1)) for line in remaining_iterations]
    print('AVG REMAINING:', sum(remaining_iterations)/len(remaining_iterations))
    #print(sorted(remaining_iterations, reverse=True))
    draw_box_plot(remaining_iterations, 'remaining_iter_plot', 'Lexecution Time (s)')
    totals = [line for line in log if "Total" in line]
    totals = [float(re.search('([0-9]+(?:.[0-9]+|))', line).group(1)) for line in totals]
    print('TOTAL TIME:', sum(totals))
    iterations = [line for line in log if "iteration_" in line]
    iterations = [float(re.search('([0-9]+(?:.[0-9]+|)) seconds', line).group(1)) for line in iterations]
    print('MAX ITERATION:', max(iterations))
    print('AVERAGE ITERATION:', sum(iterations)/len(iterations))
    print('PROPORTION ITERATION TO EVERYTHING:', sum(iterations)/sum(totals))
    before = 1
    total_nb = []
    total_total = []
    for idx, line in enumerate(log):
        if "Total" not in line:
            continue
        nb_of_iterations = idx - before - 1
        time = re.search('([0-9]+(?:.[0-9]+|))', line).group(1)
        before = idx + 1
        total_nb.append(nb_of_iterations)
        total_total.append(float(time))
    print('AVERAGE NB ITERATIONS:', sum(total_nb)/len(total_nb))
    exactly_one = len([number for number in total_nb if number == 1])
    less_than_ten = len([number for number in total_nb if 2 <= number < 10])
    less_than_twentyfive = len([number for number in total_nb if 10 <=number < 25])
    less_than_fifty = len([number for number in total_nb if 25 <= number < 50])
    less_than_onehundred = len([number for number in total_nb if 50 <= number < 100])
    less_than_twohundred = len([number for number in total_nb if 100 <= number < 200])
    less_than_threehundred = len([number for number in total_nb if 200 <= number < 300])
    exactly_three_hundred = len([number for number in total_nb if number == 300])
    bars = [exactly_one, less_than_ten, less_than_twentyfive, less_than_fifty, less_than_onehundred, less_than_twohundred, less_than_threehundred, exactly_three_hundred]

    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.5, 0.5])
    bs = axes.bar([i for i in range(len(bars))], bars, linewidth=1,
            edgecolor='black', color='#00689d')
    axes.set_xticks([0, 1, 2, 3, 4, 5, 6, 7], ['1', '2-9', '10-24', '25-49', '51-99', '100-199', '200-299', '300'], rotation=30)
    axes.tick_params(axis='x')
    axes.set_xlabel('Number of lexecutions', fontsize=13, labelpad=7)
    axes.set_ylabel('Frequency', fontsize=13, labelpad=7)
    axes.spines['top'].set_visible(False)
    axes.spines['right'].set_visible(False)
    axes.spines['left'].set_visible(False)
    axes.spines['bottom'].set_color('#DDDDDD')
    axes.set_axisbelow(True)
    axes.yaxis.grid(True, color='#CCCCCC')
    axes.xaxis.grid(False)
    axes.tick_params(axis='y', color='#CCCCCC')
    axes.tick_params(bottom=False)
    for bar in bs:
        axes.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.9,
            round(bar.get_height(), 1),
            horizontalalignment='center',
            color='#00689d',
            weight='bold'
        )
    fig.show()
    fig.savefig('./efficiency/nb_iterations.pdf', bbox_inches='tight', dpi=1200)


if __name__ == '__main__':
    ANNOTATED_CHANGES = r'../LExecutorCC/annotated_changes.json'
    # evaluate_annotated_changes()
    # get_final_results()
    # get_errors()
    # get_confusion_matrix()
    # get_length_of_functions()
    # create_functions_py()
    # get_complexity()
    # get_complexity_boxplots()
    # get_coverage()
    # get_time_data()
    # draw_robustness_plot()
