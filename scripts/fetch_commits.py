import json
import os
import re

from git import Repo, NULL_TREE
from cst_utils import Extractor, code_to_node, node_to_code

REFACTOR = True
# REFACTOR = False

REPO_PATH = r'../Repos'
REPOS = [(entry.name, entry.path) for entry in os.scandir(REPO_PATH) if entry.is_dir()]


def _early_stop(commit, idx):
    # stopping criteria differs for refactor and non-refactor commits
    if REFACTOR:
        if 'refactor' not in commit.message.lower():
            return True
    else:
        # if idx > 100:
        #     return True
        if 'refactor' in commit.message.lower():
            return True
    # commit contains more than one file (or no file)
    if len(commit.stats.files) != 1:
        return True
    # file is not a python file
    file, *_ = commit.stats.files.keys()
    if not file.endswith('.py') or 'test' in file:
        return True
    return False


def _extract_line_numbers(diff_line):
    old_line_pos = re.search('-([0-9]+)(?:,([0-9])+)?', diff_line)
    new_line_pos = re.search('\+([0-9]+)(?:,([0-9])+)?', diff_line)
    if not (old_line_pos and new_line_pos):
        return None
    old_line_start = int(old_line_pos.group(1))
    old_line_end = old_line_start if not old_line_pos.group(2) else old_line_start + int(old_line_pos.group(2)) - 1
    new_line_start = int(new_line_pos.group(1))
    new_line_end = new_line_start if not new_line_pos.group(2) else new_line_start + int(new_line_pos.group(2)) - 1
    return {'old': (old_line_start, old_line_end), 'new': (new_line_start, new_line_end)}


def _write_json(repo_name, content):
    commit_type = 'refactor' if REFACTOR else 'change'
    destination_directory = '../extracted_commits/'
    if not os.path.isdir(destination_directory):
        os.mkdir(destination_directory)
    with open(f'{destination_directory}{repo_name}_{commit_type}_commits.json', 'w') as f:
        json.dump(content, f, indent=4)


def _extract_functions(code, lines):
    extractor = Extractor(lines)
    cst = code_to_node(code)  # returns None if something went wrong during parsing the node
    if not cst:
        return set()
    cst.visit(extractor)
    # TODO if we remove lines that have been covered in functions we need to store the initial length to still be able to perfom this check
    if extractor.changes_to_comments == len(extractor.lines):
        return set()
    return extractor.extracted_functions


def fetch_repo(repo_name, repo_path):
    repo = Repo(repo_path)
    repo_base_url = list(repo.remotes[0].urls)[0].replace('.git', '')
    found_commits = []
    commits = list(repo.iter_commits(None))
    for idx, commit in enumerate(commits, start=1):
        print(f'\rCommits: {idx} / {len(commits)}', end='', flush=True)
        if _early_stop(commit, idx):
            continue

        if len(commit.parents) > 0:
            parent = commit.parents[0]
            # unified=0 removes additional context from hunk
            diffs = parent.diff(commit, create_patch=True, unified=0)
        else:
            parent = None
            diffs = commit.diff(NULL_TREE, create_patch=True, unified=0)
        parent_hexsha = parent.hexsha if parent else None

        assert len(diffs) == 1  # since we only consider single file commits
        diff = diffs[0]
        # INFO: have to manually compute change type since change_type attribute of diff seems to always be None
        if not diff.a_blob and diff.b_blob and diff.a_blob != diff.b_blob:  # only care about modifying commits
            continue

        diff_content = str(diff)
        diff_lines = [line for line in diff_content.splitlines() if '@@' in line]
        lines_to_check = []
        for diff_line in diff_lines:
            line = _extract_line_numbers(diff_line)
            if line:
                lines_to_check.append(line)

        old_code = repo.git.show(f'{parent.hexsha}:{diff.a_path}')
        changed_functions = _extract_functions(old_code, [entry['old'] for entry in lines_to_check])
        if len(changed_functions) != 1:
            continue
        old_function = node_to_code(changed_functions.pop())

        new_code = repo.git.show(f'{commit.hexsha}:{diff.b_path}')
        changed_functions = _extract_functions(new_code, [entry['new'] for entry in lines_to_check])
        if len(changed_functions) != 1:
            continue
        new_function = node_to_code(changed_functions.pop())

        commit_stats = commit.stats.total
        commit_json = {
            'sha': commit.hexsha,
            'url': repo_base_url + '/commit/' + commit.hexsha,
            'message': commit.message,
            'insertions': commit_stats['insertions'],
            'deletions': commit_stats['deletions'],
            'changed_lines': commit_stats['lines'],
            'old_commit': parent_hexsha,
            'new_commit': commit.hexsha,
            'old_file': diff.a_path,
            'new_file': diff.b_path,
            'old_function': old_function,
            'new_function': new_function

        }
        found_commits.append(commit_json)
        if not REFACTOR and len(found_commits) == 20:
            break

    print(f'\nFound {len(found_commits)} commits')
    _write_json(repo_name, found_commits)


if __name__ == '__main__':
    for repo in REPOS:
        print(f'Fetching commits for {repo[0]}')
        fetch_repo(*repo)
