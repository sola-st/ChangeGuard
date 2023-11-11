import json
import sys
import webbrowser
import atexit
import os
import time

from logger import get_logger


# TYPE = 'refactor'
TYPE = 'change'

if len(sys.argv) > 1:
    repo = sys.argv[1]
else:
    repo = input('Enter repo: ')

if len(sys.argv) > 2:
    TYPE = sys.argv[2]

logger = get_logger(__name__, f'{TYPE}_annotation')

JSON_SUFFIX = f'_{TYPE}_commits.json'


name = repo + JSON_SUFFIX

directory = '../extracted_commits/'

counter_file_name = f'{directory}{repo}_{TYPE}_counter.txt'

if os.path.isfile(counter_file_name):
    with open(counter_file_name, 'r') as f:
        counter = int(f.read())
else:
    counter = 0

annotated_directory = '../annotated_changes/'
if not os.path.isdir(annotated_directory):
    os.mkdir(annotated_directory)

annotated_file_name = f'{annotated_directory}annotated_changes.json'

if os.path.isfile(annotated_file_name):
    with open(annotated_file_name, 'r') as f:
        annotated_changes = json.load(f)
else:
    annotated_changes = []

start = time.time()


def save():
    with open(counter_file_name, 'w') as f:
        f.write(str(counter))
    with open(annotated_file_name, 'w') as f:
        json.dump(annotated_changes, f, indent=2)
    end = time.time()
    print(f'Annotating took: {end - start}s')


atexit.register(save)
with open(f'{directory}{name}', 'r') as f:
    commits = json.load(f)

remaining_commits = commits[counter:]
for idx, commit in enumerate(remaining_commits, start=1):
    webbrowser.open(commit['url'], 2)
    print('----------------------------------------------------------')
    print(f'{idx}/{len(remaining_commits)}')
    inp = input()
    if inp == 'y':
        commit['annotation'] = 'semantics_preserving'
    elif inp == 'n':
        commit['annotation'] = 'semantics_changing'
    else:
        print('skipped')
        logger.info(f'{repo}::{commit["sha"]}::skipped')
        continue
    commit = {'repo': repo, 'source': TYPE, **commit}
    annotated_changes.append(commit)
    counter += 1
