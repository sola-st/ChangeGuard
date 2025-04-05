import subprocess

repos = [
    'https://github.com/pandas-dev/pandas.git'
]

for repo in repos:
    repo_name = repo.split('/')[-1].split('.')[0]
    subprocess.run(f'dpkg --list | grep compiler', shell=True)
    subprocess.run(f'git clone {repo}', shell=True)
    try:
        subprocess.run(f'cd {repo_name} && ' +
                    'git reset --hard b0a0c6851571016daf8f2fba24c0228bb224a712 && ' +
                    'python3 -m venv ~/virtualenvs/pandas-dev && ' +
                    f'. ~/virtualenvs/pandas-dev/bin/activate && ' +
                    f'python3 -m pip install -r requirements-dev.txt && ' +
                    'python setup.py develop && ' +
                    f'cd {repo_name}/tests && pytest', shell=True)
    except subprocess.CalledProcessError as e:
        print(e)
    