import subprocess

repos = [
    'https://github.com/apache/airflow.git',
    'https://github.com/psf/black.git',
    'https://github.com/httpie/cli.git',
    'https://github.com/tiangolo/fastapi.git',
    'https://github.com/pallets/flask.git',
    'https://github.com/pandas-dev/pandas.git',
    'https://github.com/python-poetry/poetry.git'
    'https://github.com/TheAlgorithms/Python.git',
    'https://github.com/scikit-learn/scikit-learn.git',
    'https://github.com/scrapy/scrapy.git',
]

for repo in repos:
    subprocess.run(f'git clone {repo}')
