import json
import os
import re
import time
import ast

from collections import namedtuple

from git import Repo, NULL_TREE
from cst_utils import Extractor, CodeCleaner, code_to_node, node_to_code
from logger import get_logger

REFACTOR = True
# REFACTOR = False

log_info = ()  # global place holder for logging information
logger = get_logger(__name__, 'refactor' if REFACTOR else 'change')

REPO_PATH = r'../Repos'
REPOS = [(entry.name, entry.path) for entry in os.scandir(REPO_PATH) if entry.is_dir()]

KEYWORDS = ['refactor', 'simplify', 'cleanup', 'optimize']

Position = namedtuple('Position', 'start end')
ExtractedData = namedtuple('ExtractedData', 'function level line')
CleanedData = namedtuple('CleanedData', 'function start removed_lines')


def _early_stop(commit, idx):
    if REFACTOR and all(keyword not in commit.message.lower() for keyword in KEYWORDS):
        return True
    if not REFACTOR and any(keyword in commit.message.lower() for keyword in KEYWORDS):
        return True

    # commit contains more than one file (or no file)
    if len(commit.stats.files) != 1:
        logger.info(f'{log_info[0]}::{log_info[1]}::file_amount')
        return True
    # file is not a python file
    file, *_ = commit.stats.files.keys()
    if not file.endswith('.py') or 'test' in file:
        logger.info(f'{log_info[0]}::{log_info[1]}::file_type')
        return True
    return False


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


def _write_json(repo_name, content):
    commit_type = 'refactor' if REFACTOR else 'change'
    destination_directory = '../extracted_commits/'
    if not os.path.isdir(destination_directory):
        os.mkdir(destination_directory)
    with open(f'{destination_directory}{repo_name}_{commit_type}_commits.json', 'w') as f:
        json.dump(content, f, indent=2)


def _extract_function(code, lines, max_level=1_000_000):
    extractor = Extractor(lines, max_level)
    cst = code_to_node(code)  # returns None if something went wrong during parsing the node
    if not cst:
        logger.info(f'{log_info[0]}::{log_info[1]}::parse_error')
        return None
    cst.visit(extractor)
    changed_function = extractor.extracted_function
    if not changed_function:
        logger.info(f'{log_info[0]}::{log_info[1]}::change_outside_function')
        return None
    return ExtractedData(node_to_code(changed_function), extractor.level, extractor.fun_start)


def _clean_function(fun):
    cleaner = CodeCleaner()
    fun_cst = code_to_node(fun)
    return CleanedData(node_to_code(fun_cst.visit(cleaner)), cleaner.start, cleaner.removed_lines)


def _is_trivial_change(old, new):
    """
    Checks whether both functions parse to the same AST.
    """
    old_tree = ast.parse(old)
    new_tree = ast.parse(new)
    return ast.dump(old_tree) == ast.dump(new_tree)


def _extract_changed_line_numbers(code_start, changed_code_lines, fun_start, fun_removed_lines):
    """
    Extracts the line numbers of the changed lines for the provided function.
    """
    # compute the difference between the start of the function and the changed lines (context: whole code)
    changed_line_deltas = [(line.start - code_start, line.end - code_start) for line in changed_code_lines]
    # compute the difference between the start of the function and the removed lines (context: extracted function)
    removed_line_deltas = sorted([line - fun_start for line in fun_removed_lines if line > fun_start])
    # discard changes that haven been completely removed during cleaning
    changed_line_deltas = list(filter(lambda line: not all(change in removed_line_deltas for change in range(line[0], line[1]+1)), changed_line_deltas))
    changed_lines = []
    for changed_line_delta in changed_line_deltas:
        nb_skip = len([rem_line_del for rem_line_del in removed_line_deltas if rem_line_del < changed_line_delta[0]])
        start_line = changed_line_delta[0] - nb_skip + 1
        nb_skip = len([rem_line_del for rem_line_del in removed_line_deltas if rem_line_del <= changed_line_delta[1]])
        end_line = changed_line_delta[1] - nb_skip + 1
        changed_lines.append(Position(start_line, end_line))
    return changed_lines


def fetch_repo(repo_name, repo_path):
    global log_info
    repo = Repo(repo_path)
    repo_base_url = list(repo.remotes[0].urls)[0].replace('.git', '')
    found_commits = []
    commits = [commit for commit in repo.iter_commits(None) if commit.committed_date < 1698796800]  # 1. November 2023
    for idx, commit in enumerate(commits, start=1):
        print(f'\rCommits: {idx} / {len(commits)}', end='', flush=True)
        log_info = (repo_name, commit.hexsha)  # setting global log_info so that other functions can access it
        if _early_stop(commit, idx):
            continue
        if len(commit.parents) > 1:
            logger.info(f'{log_info[0]}::{log_info[1]}::merge_commit')
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
            logger.info(f'{log_info[0]}::{log_info[1]}::commit_type')
            continue

        diff_content = str(diff)
        diff_lines = [line for line in diff_content.splitlines() if '@@' in line]
        lines_to_check = []
        for diff_line in diff_lines:
            line = _extract_line_numbers(diff_line)
            if line:
                lines_to_check.append(line)
        old_code = repo.git.show(f'{parent.hexsha}:{diff.a_path}')
        old_lines = [entry['old'] for entry in lines_to_check]
        old_extracted = _extract_function(old_code, old_lines)
        if not old_extracted:
            continue
        new_lines = [entry['new'] for entry in lines_to_check]
        new_code = repo.git.show(f'{commit.hexsha}:{diff.b_path}')
        new_extracted = _extract_function(new_code, new_lines)
        if not new_extracted:
            continue
        if old_extracted.level != new_extracted.level:
            logger.info(f'{log_info[0]}::{log_info[1]}::unequal_level')
            # if nesting level does not match use outer one
            outer_level = min(old_extracted.level, new_extracted.level)
            old_extracted = _extract_function(old_code, old_lines,  max_level=outer_level)
            new_extracted = _extract_function(new_code, new_lines, max_level=outer_level)

        old_clean_extracted = _clean_function(old_extracted.function)
        new_clean_extracted = _clean_function(new_extracted.function)
        if _is_trivial_change(old_clean_extracted.function, new_clean_extracted.function):
            logger.info(f'{log_info[0]}::{log_info[1]}::trivial_change')
            continue

        old_changed_lines = _extract_changed_line_numbers(old_extracted.line, old_lines, old_clean_extracted.start, old_clean_extracted.removed_lines)
        new_changed_lines = _extract_changed_line_numbers(new_extracted.line, new_lines, new_clean_extracted.start, new_clean_extracted.removed_lines)
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
            'old_function': old_extracted.function,
            'new_function': new_extracted.function,
            'old_clean_function': old_clean_extracted.function,
            'new_clean_function': new_clean_extracted.function,
            'old_changed_lines': old_changed_lines,
            'new_changed_lines': new_changed_lines
        }
        found_commits.append(commit_json)
        if not REFACTOR and len(found_commits) == 15:
            break

    print(f'\nFound {len(found_commits)} commits')
    _write_json(repo_name, found_commits)


if __name__ == '__main__':
    start = time.time()
    for repo in REPOS:
        print(f'Fetching commits for {repo[0]}')
        fetch_repo(*repo)
    end = time.time()
    print(f'Finished fetching took: {end-start}s')
