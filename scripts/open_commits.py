import json
import sys
import webbrowser

JSON_SUFFIX = '_refactor_commits.json'

repo = sys.argv[1]

name = repo + JSON_SUFFIX

with open(name, 'r') as f:
    commits = json.loads(f.read())
for idx, commit in enumerate(commits):

    if len(sys.argv) > 2 and idx % 10 == 9:
        input('Press \'Enter\' to open next batch of commits')
    webbrowser.open(commit['url'], 2)
