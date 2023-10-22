import json
import sys
import webbrowser
import atexit
import os


TYPE = 'refactor'
# TYPE = 'change'
repo = sys.argv[1]

if len(sys.argv) > 2:
    TYPE = sys.argv[2]


JSON_SUFFIX = f'_{TYPE}_commits.json'



name = repo + JSON_SUFFIX

directory = '../extracted_commits/'

counter_file_name = f'{directory}{repo}_{TYPE}_counter.txt'

if os.path.isfile(counter_file_name):
    with open(counter_file_name, 'r') as f:
        counter = int(f.read())
else:
    counter = 0


def save():
    with open(counter_file_name, 'w') as f:
        f.write(str(counter))


atexit.register(save)
with open(f'{directory}{name}', 'r') as f:
    commits = json.load(f)
for idx, commit in enumerate(commits[counter:]):
    webbrowser.open(commit['url'], 2)
    # print('Commit:', commit['sha'])
    print('URL:', commit['url'])
    # print('File:', commit['old_file'])
    print('----------------------------------------------------------')
    input()
    counter += 1
