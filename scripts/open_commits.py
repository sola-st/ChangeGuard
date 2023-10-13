import json
import sys
import webbrowser
import atexit
import os


JSON_SUFFIX = '_refactor_commits.json'

repo = sys.argv[1]

name = repo + JSON_SUFFIX

directory = '../extracted_commits/'

counter_file_name = f'{directory}{repo}_counter.txt'

if os.path.isfile(counter_file_name):
    with open(counter_file_name, 'r') as f:
        counter = int(f.read())
else:
    counter = 0

saved_commits_file_name = f'{directory}{repo}_saved.json'

if os.path.isfile(saved_commits_file_name):
    with open(saved_commits_file_name, 'r') as f:
        saved_commits = json.load(f)
else:
    saved_commits = []


def save():
    with open(counter_file_name, 'w') as f:
        f.write(str(counter))
    with open(saved_commits_file_name, 'w') as f:
        json.dump(saved_commits, f, indent=4)


atexit.register(save)
with open(f'{directory}{name}', 'r') as f:
    commits = json.load(f)
for idx, commit in enumerate(commits[counter:]):
    webbrowser.open(commit['url'], 2)
    print('--------------------------------------------------')
    for change in commit['changes']:
        print(f'Keep file: {change["path"].split("/")[-1]}?', end=' ')
        inp = input()
        if inp != '':
            try:
                old_line, new_line = inp.split(' ')
                commit = {
                    'repo': repo,
                    'old_commit': change['prev'],
                    'new_commit': change['next'],
                    'file': change['path'],
                    'old_line': old_line,
                    'new_line': new_line
                 }
                saved_commits.append(commit)
            except Exception:
                pass
    counter += 1
