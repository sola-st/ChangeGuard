import atexit
import json
import subprocess
import pyperclip
import re
from collections import namedtuple

Position = namedtuple('Position', 'start end')


# copied from fetch_commits.py
def _extract_line_numbers(diff_line):
    old_line_pos = re.search('-([0-9]+)(?:,([0-9]+))?', diff_line)
    new_line_pos = re.search('\+([0-9]+)(?:,([0-9]+))?', diff_line)
    if not (old_line_pos and new_line_pos):
        return None
    old_line_start = int(old_line_pos.group(1))
    old_line_end = old_line_start if not old_line_pos.group(2) else old_line_start + max(int(old_line_pos.group(2)) - 1, 0)
    new_line_start = int(new_line_pos.group(1))
    new_line_end = new_line_start if not new_line_pos.group(2) else new_line_start + max(int(new_line_pos.group(2)) - 1, 0)
    return {'old': Position(old_line_start, old_line_end), 'new': Position(new_line_start, new_line_end)}


try:
    with open('llm_changes.json', 'r', encoding='utf-8') as f:
        changes = json.load(f)
except (json.decoder.JSONDecodeError, FileNotFoundError):
    changes = []


def save():
    with open('llm_changes.json', 'w', encoding='utf-8') as f:
        json.dump(changes, f, indent=4)



atexit.register(save)

with open('../../LExecutorCC/annotated_changes.json', 'r', encoding='utf-8') as f:
    functions = json.load(f)
functions = [entry['new_clean_function'] for entry in functions]

prompt = 'You are a Python expert, improve the quality of this Python code while preserving its behavior and without renaming variables, adding comments, adding a docstring, or adding imports:'
for idx, function in enumerate(functions[len(changes):], start=len(changes)):

    text = prompt + '\n' + function
    pyperclip.copy(text)
    input(f'{idx} - paste text in prompt')
    response = pyperclip.paste().replace('\r\n', '\n').replace('\n\n', '\n')
    response = '\n'.join([line for line in response.split('\n') if not line.strip().startswith('#')])
    changed_lines_old = []
    changed_lines_new = []
    with open('old.py', 'w', encoding='utf-8') as f:
        f.write(function)
    with open('new.py', 'w', encoding='utf-8') as f:
        f.write(response)
    process = subprocess.run(f'git diff --no-index --unified=0 -p old.py new.py', capture_output=True)
    diffs = process.stdout.decode('utf-8')
    print(diffs)
    diff_lines = [line for line in diffs.splitlines() if '@@' in line]
    for diff_line in diff_lines:
        line = _extract_line_numbers(diff_line)
        if line:
            changed_lines_old.append(line['old'])
            changed_lines_new.append(line['new'])

    changes.append({
        'repo': 'llm',
        'old_commit': 0,
        'new_commit': idx,
        'old_clean_function': function,
        'new_clean_function': response,
        'old_changed_lines': changed_lines_old,
        'new_changed_lines': changed_lines_new
    })

