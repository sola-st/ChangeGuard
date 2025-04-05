# ChangeGuard
ChangeGuard is an approach that automatically identifies for a function-level code change whether it is semantics-preserving or semantics-changing. To achieve this it uses LExecutor a learning-guided approach that makes it possible to execute arbitrary Python code.

Paper pre-print: https://arxiv.org/abs/2410.16092

This repository contains the implementation of the approach, as well as all scripts for data collection and experiments used for the evaluation.
Note: The code calls the project "LExecutorCC".

This file focuses on how to use our Approach LExecutorCC, instructions on how to repeat the evaluations are found in
[here](evaluation/README.md)

## LExecutorCC
LExecutorCC is an approach that automatically identifies for a function-level code change whether it is semantics-preserving
or semantics-changing. To achieve this it uses LExecutor a learning-guided approach that makes it possible to execute
arbitrary Python code.


### Installation
Since LExecutorCC contains its own version of LExecutor it is enough to install LExecutorCC.

Make sure you are in the `./LExecutorCC/` directory and that Python 3.8 is installed.

1. Create virtual environment
```
virtualenv -p /usr/bin/python3.8 myenv
```
2. Enter virtual environment
```
source myenv/bin/activate
```
3. Install requirements 
```
pip install -r requirements.txt
```
4. Install LExceutorCC (in editable mode)
```
pip install -e .
```
5. Download the newly trained model from [here](https://github.com/sola-st/master-thesis-lars-groeninger/releases/tag/model)
and store it in `./LExecutorCC/data/released_models/`
### Usage
The **input** of LExecutorCC is a list of code changes in JSON format. The format of a code change is as follows:
```json
{
   "repo": "Project from which the code change originates",
   "old_sha": "Identifier referencing old version of change",
   "new_sha": "Identifier referencing new version of change",
   "old_code": "Source code of old version",
   "new_code": "Source code of new version",
   "old_changed_lines": "List of line numbers where changes happen in old version",
   "new_changed_lines": "List of line numbers where changes happen in new version"
}
```
The changed lines provided as tuples containing the start line of the change and the end line of the change (inclusive).
For example: 
```json
[
   [2, 5],
   [8, 8]
]
```
indicates that 2 changes happen one from line 2 to 5 and one at line 8.

We provide a list of 299 annotated code changes that we used for our evaluation in `annotated_changes.json`.

To run LExecutorCC one needs to execute the `Runner` module this works in two steps:

1. The compare scripts are created and instrumented
```
python -m lexecutor.Runner --commits annotated_changes.json --action instrument
```
2. The compare scripts are executed using LExecutor
```
python -m lexecutor.Runner --commits annotated_changes.json --action run
```
The results are stored in the file `std_out.json`.




---
Below are instructions on how to repeat the data collection steps used to obtain the code changes in `annotated_changes.json`:

### Data Collection
> [!IMPORTANT]
> Git must be installed 
1. Starting from the root directory, navigate to the repos directory `cd repos`.
2. Clone all repositories for which you want to collect data, alternatively you can execute the clone_repos script `python clone_repos.py` to use the same repositories as we did.
3. Navigate to the scripts directory `cd ../scripts`.
4. Execute the fetch_commits script `python fetch_commits.py`.
    - To switch from collecting refactor commits to change commits, simply set the *REFACTOR* flag at top of the `fetch_commit.py` script to **False**.
    - After the script is finished executing the collected code changes are stored in a newly created directory called `extracted_commits` in JSON format.
    - Information about which commits have been skipped and for which reasons can be found in the `logs` directory.


### Annotating Code Changes
0. Make sure all the data Collection steps have been completed.
1. Navigate to the scripts directory `cd scripts`.
2. execute the `open_commits.py` script `python open_commits.py`.
   - To switch from opening refactor commits to change commits, simply set the *TYPE* flag at top of the open_commits script to **'change'**.
   - After executing the script you are asked to enter the repository that you would like to annotate.
   - Now the first commit is opened in a new tab in your browser.
   - Look at the commit and as soon as you have decided on whether the code change is semantics preserving or not, go back to the terminal and enter either **y** for semantics preserving, **n** for semantics changing, or **x** for unclear and hit enter.
   - The next commit opens and the process repeats until all the extracted commits of the repository have been processed.
   - If you want to stop early, simply press `ctrl + c` to interrupt the process. The script stores the index so the next time you execute it, you can continue where you left off.

