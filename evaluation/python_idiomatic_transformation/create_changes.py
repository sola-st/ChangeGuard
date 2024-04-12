import json
import subprocess
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


idioms = {}
results = []
for i in range(299):
    try:
        with open(f'RefactoringIdiomsOutputdir/result_{i}.json', encoding='utf-8') as f:
            data = json.load(f)
        changed_lines_old = []
        changed_lines_new = []
        for d in data:
            idioms[d['idiom']] = idioms.get(d['idiom'], 0) + 1
            #lines = d['lineno']
            #changed_lines.append((lines[0][0][0], lines[0][-1][0]))
        if data:
            with open(f'func_files/fun_{i}.py', encoding='utf-8') as f:
                old_code = f.read()
            with open(f'RefactoringIdiomsOutputdir/fun_{i}.py', encoding='utf-8') as f:
                new_code = f.read()
            process = subprocess.run(f'git diff --no-index --unified=0 -p func_files/fun_{i}.py RefactoringIdiomsOutputdir/fun_{i}.py', capture_output=True)
            diffs = process.stdout.decode('utf-8')
            diff_lines = [line for line in diffs.splitlines() if '@@' in line]
            for diff_line in diff_lines:
                line = _extract_line_numbers(diff_line)
                if line:
                    changed_lines_old.append(line['old'])
                    changed_lines_new.append(line['new'])
            obj = {
                'repo': 'transformations',
                'old_commit': 0,
                'new_commit': i,
                'old_clean_function': old_code,
                'new_clean_function': new_code,
                'old_changed_lines': changed_lines_old,
                'new_changed_lines': changed_lines_new
            }
            results.append(obj)
    except FileNotFoundError:
        pass
with open('transformation_changes.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4)
print(idioms)
