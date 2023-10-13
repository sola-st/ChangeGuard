import json
import os
import re

from git import Repo, NULL_TREE

REPO_PATH = r'../Repos'
REPOS = [(entry.name, entry.path) for entry in os.scandir(REPO_PATH) if entry.is_dir()]


def fetch_repo(repo_name, repo_path):
    repo = Repo(repo_path)
    repo_base_url = list(repo.remotes[0].urls)[0].rstrip('.git')
    refactor_commits = []
    commits = list(repo.iter_commits(None))
    for idx, commit in enumerate(commits, start=1):
        print(f'\rCommits: {idx} / {len(commits)}', end='', flush=True)
        if 'refactor' not in commit.message.lower():
            continue
        commit_stats = commit.stats.total
        if len(commit.parents) > 0:
            parent = commit.parents[0]
            diffs = parent.diff(commit, create_patch=True, unified=0)
        else:
            parent = None
            diffs = commit.diff(NULL_TREE, create_patch=True, unified=0)
        changes = []
        parent_hexsha = parent.hexsha if parent else None
        for diff in diffs.iter_change_type('M'):
            if not diff.a_path.endswith('.py'):
                continue
            diff_content = str(diff)
            hunks = []
            diff_lines = [line for line in diff_content.splitlines() if '@@' in line]
            for diff_line in diff_lines:
                start_lines = re.findall('[0-9]+,', diff_line)
                if len(start_lines) != 2:
                    continue
                old_line = int(start_lines[0][:-1])
                new_line = int(start_lines[1][:-1])
                hunks.append({'old_line': old_line, 'new_line': new_line})
            file_change = {'path': diff.a_path, 'prev': parent_hexsha, 'next': commit.hexsha,
                           'hunks': hunks}
            changes.append(file_change)
        commit_json = {
            'sha': commit.hexsha,
            'url': repo_base_url + '/commit/' + commit.hexsha,
            'message': commit.message,
            'insertions': commit_stats['insertions'],
            'deletions': commit_stats['deletions'],
            'changed_lines': commit_stats['lines'],
            'nb_of_files': commit_stats['files'],
            'changes': changes
        }
        refactor_commits.append(commit_json)
    print(f'\nFound {len(refactor_commits)} commits that contain \'refactor\'')
    destination_directory = '../extracted_commits/'
    if not os.path.isdir(destination_directory):
        os.mkdir(destination_directory)
    with open(f'{destination_directory}{repo_name}_refactor_commits.json', 'w') as f:
        json.dump(refactor_commits, f, indent=4)


if __name__ == '__main__':
    for repo in REPOS:
        print(f'Fetching commits for {repo[0]}')
        fetch_repo(*repo)
