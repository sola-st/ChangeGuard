import json
import os
import re

from git import Repo, NULL_TREE


# REFACTOR = True
REFACTOR = False

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
    if not file.endswith('.py'):
        return True
    return False


def _extract_line_numbers(diff_line):
    old_line = re.search('-[0-9]+', diff_line)
    if old_line:
        old_line = int(old_line.group()[1:])
    new_line = re.search('\+[0-9]+', diff_line)
    if new_line:
        new_line = int(new_line.group()[1:])
    return old_line, new_line


def _write_json(repo_name, content):
    commit_type = 'refactor' if REFACTOR else 'change'
    destination_directory = '../extracted_commits/'
    if not os.path.isdir(destination_directory):
        os.mkdir(destination_directory)
    with open(f'{destination_directory}{repo_name}_{commit_type}_commits.json', 'w') as f:
        json.dump(content, f, indent=4)


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
            # W=True makes hunks span whole function, make sure to set diff=python in gitattributes
            # to ensure correct hunk header is created as otherwise methods do not work correctly
            # unified=0 removes additional context from hunk
            diffs = parent.diff(commit, create_patch=True, W=True, unified=0)
        else:
            parent = None
            diffs = commit.diff(NULL_TREE, create_patch=True, W=True, unified=0)
        parent_hexsha = parent.hexsha if parent else None

        assert len(diffs) == 1  # since we only consider single file commits
        diff = diffs[0]
        # INFO: have to manually compute change type since change_type attribute of diff seems to always be None
        if not diff.a_blob and diff.b_blob and diff.a_blob != diff.b_blob:  # only care about modifying commits
            continue

        diff_content = str(diff)
        diff_lines = [line for line in diff_content.splitlines() if '@@' in line]
        if len(diff_lines) != 1:  # only care about single function changes
            continue
        diff_line = diff_lines[0]

        old_line, new_line = _extract_line_numbers(diff_line)

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
            'old_line': old_line,
            'new_line': new_line

        }
        found_commits.append(commit_json)

    print(f'\nFound {len(found_commits)} commits')
    _write_json(repo_name, found_commits)


if __name__ == '__main__':
    for repo in REPOS:
        print(f'Fetching commits for {repo[0]}')
        fetch_repo(*repo)
