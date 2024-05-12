import json
import os

with open('../../LExecutorCC/annotated_changes.json', encoding='utf-8') as f:
    changes = json.load(f)
directory = './func_files'
if not os.path.exists(directory):
    os.mkdir(directory)
for idx, change in enumerate(changes):
    code = change['new_clean_function']
    with open(f'./{directory}/fun_{idx}.py', 'w', encoding='utf-8') as f:
        f.write(code)
