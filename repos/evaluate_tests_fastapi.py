import json
import re
import subprocess


def execute_tests_fastapi(url, commit):
    repo_name = url.split('/')[-1].split('.')[0]
    subprocess.run(f'rm -rf {repo_name}', shell=True)
    subprocess.run(f'git clone {url}', shell=True)
    try:
        out = subprocess.run(f'cd {repo_name} && ' +
                    f'git reset --hard {commit} && ' +
                    f'python3 -m venv ~/virtualenvs/{repo_name}-env && ' +
                    f'. ~/virtualenvs/{repo_name}-env/bin/activate && ' +
                    #f'pip install -r requirements.txt && ' +
                    'pip install -e ."[dev,doc,test]" && ' +
                    #f'cd tests && pytest', 
                    'set -e && set -x && export PYTHONPATH=./docs_src && pytest tests -W ignore::DeprecationWarning', capture_output=True, text=True, shell=True)
        print(out.stderr)
        out = out.stdout
        
    except subprocess.CalledProcessError as e:
        print(e)
        out = ""
    print(out)
    return out

def get_test_results(repo, commit):
    if repo == "fastapi":
        url = 'https://github.com/tiangolo/fastapi.git'
    execution_results = execute_tests_fastapi(url, commit)

    passed = re.search(r' (\d+) passed', execution_results)
    if passed:
        value = int(passed.group(1))
        return value
    
    return None

if __name__ == '__main__':
    results = []
    ANNOTATED_CHANGES = r'../LExecutorCC/annotated_changes.json'
    with open(ANNOTATED_CHANGES, 'r', encoding='utf-8') as f:
        changes = json.load(f)
        for change in changes:
            if change["repo"] == "fastapi":
                old_commit_results = get_test_results(change["repo"], change["old_commit"])
                new_commit_results = get_test_results(change["repo"], change["new_commit"])
                succesful_execution = type(old_commit_results) == type(new_commit_results) == isinstance(new_commit_results, int)

                if old_commit_results == new_commit_results:
                    verdict = "preserving"
                else:
                    verdict = "changing"

                results.append(
                    {
                        'repo': change["repo"],
                        'sha': change["sha"],
                        'old_commit_passing': old_commit_results,
                        'new_commit_passing': new_commit_results,
                        'succesful_execution': succesful_execution,
                        'final_result': verdict
                    }
                )

    with open('../evaluation/regression_tests/fastapi_tests_verdict.json', 'w') as f:
        json.dump(results, f, indent=4)

