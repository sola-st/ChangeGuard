# ChangeGuard: Validating Code Changes via Pairwise Learning-Guided Execution 

**ChangeGuard** is an approach that automatically identifies for a function-level code change whether it is semantics-preserving or semantics-changing. To achieve this, it uses LExecutor which is a learning-guided approach that makes it possible to execute arbitrary Python code.

Paper pre-print: https://arxiv.org/abs/2410.16092

This repository contains the implementation of the approach, as well as all scripts for data collection and experiments used for the evaluation.
Note: The code calls the project "LExecutorCC".

**Table of Contents**
  * [Installation](#installation)
  * [How-to-use](#how-to-use)
    + [Input format](#input-format)
    + [Running](#running)
  * [Reproducibility](#reproducibility)
    + [Reproduce Datasets Creation](#reproduce-datasets-creation)
    + [Reproduce RQ1 - Effectiveness](#reproduce-rq1---anomaly-detection-effectiveness)
    + [Reproduce RQ2 - Regression Testing](#reproduce-rq2---regression-testing)
    + [Reproduce RQ3 - Retraining model](#reproduce-rq3---retraining-model)
    + [Reproduce RQ4 - LExecutor Improvements (coverage)](#reproduce-rq4---lexecutor-improvements-(coverage))
    + [Reproduce RQ5 - Efficiency](#reproduce-rq4---efficiency)
  * [Download Data](#download-data)

## Installation

Clone ChangeGuard from GitHub
> [!IMPORTANT]
> Git must be installed 
```bash
git clone https://github.com/sola-st/ChangeGuard && cd ChangeGuard
```

Make sure you are in the `./LExecutorCC/` directory

```bash
cd LExecutorCC
```

Create a virtual environment
> [!IMPORTANT]
> Python 3.8 must be installed 
```
virtualenv -p /usr/bin/python3.8 myenv
```

Enter the virtual environment

```
source myenv/bin/activate
```

Install requirements 

```
pip install -r requirements.txt
```

Install LExceutorCC (in editable mode)

```
pip install -e .
```

Download the newly trained model from [here](https://github.com/sola-st/master-thesis-lars-groeninger/releases/tag/model)
and store it in `./LExecutorCC/data/released_models/`


## How-to-use

### Input format

The **input** of ChangeGuard is a list of code changes in JSON format. The format of a code change is as follows:
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

### Running

To run ChangeGuard, one needs to execute the `Runner` module. This works in two steps:

Create and instrument the compare scripts

```
python -m lexecutor.Runner --commits annotated_changes.json --action instrument
```

Execute the compare scripts using LExecutor

```
python -m lexecutor.Runner --commits annotated_changes.json --action run
```

The results are stored in the `std_out.json` file.

## Reproducibility

### Reproduce Datasets Creation

#### Manually annotated code changes

Below are instructions on how to repeat the data collection steps used to obtain the code changes in `annotated_changes.json`.

##### Data Collection

Starting from the root directory, navigate to the repos directory

```
cd repos
```

Clone all repositories for which we collect data

```
python clone_repos.py
```

Navigate to the scripts directory 

```
cd ../scripts
```

Fetch the commits of interest
> [!IMPORTANT]
> To switch from collecting refactor commits to change commits, simply set the *REFACTOR* flag at top of the `fetch_commit.py` script to **False**
```
python fetch_commits.py
```

After the script is finished executing, the collected code changes are stored in a newly created directory called `extracted_commits` in JSON format.
Information about which commits have been skipped and for which reasons can be found in the `logs` directory.

##### Annotating Code Changes
0. Make sure all the data Collection steps have been completed.
1. Navigate to the scripts directory `cd scripts`.
2. execute the `open_commits.py` script `python open_commits.py`.
   - To switch from opening refactor commits to change commits, simply set the *TYPE* flag at top of the open_commits script to **'change'**.
   - After executing the script you are asked to enter the repository that you would like to annotate.
   - Now the first commit is opened in a new tab in your browser.
   - Look at the commit and as soon as you have decided on whether the code change is semantics preserving or not, go back to the terminal and enter either **y** for semantics preserving, **n** for semantics changing, or **x** for unclear and hit enter.
   - The next commit opens and the process repeats until all the extracted commits of the repository have been processed.
   - If you want to stop early, simply press `ctrl + c` to interrupt the process. The script stores the index so the next time you execute it, you can continue where you left off.

#### Rule-based refactorings

1. For this we use [RIdiom](https://pypi.org/project/RefactoringIdioms/). However since it is difficult to set up we include our adjusted version in the `ridiom` directory.
2. Install RIdiom as module: in `./evaluation/ridiom/RIdiom` directory by executing `pip install .` (requires Python 3.9).
3. Manually add missing dependencies (you can test if it works by running `python3 main.py` in `./evaluation/ridiom/RIdiom/RefactoringIdioms/`).
We needed to install pathos: `pip install pathos`
5. Run `python3 create_func_files.py` to create functions for transformations.
6. Copy `./func_files` directory into source directory of RIdiom (same directory as main.py).
7. In the same directory run `python3 runner.py`.
8. Manually fix errors in transformed code in `./RefactoringIdioms/RefactoringIdiomsOutputdir/`. Function 34, 212, 220, 223, 224, 231, 262, 268, and 285 needs to be fixed.
9. Navigate back to the `ridiom` directory and run `python3 create_changes.py`.
10. Use the resulting `transformation_changes.json` file as input to LExecutorCC.

#### Refactorings created by GPT-3.5 and GPT-4

0. Navigate to`./llm` directory.
1. Create file .secret and paste your API token (first line) and organization id (second line) into it.
2. Make sure the correct model in `llm_creator_api.py` is selected.
3. Run `python3 llm_creator_api.py`.
4. Clean the resulting `response.json`, e.g., by running the `remove_text.py` script. The cleaned version should only contain the changed function and no additional text from the model.
5. Run `python3 create_changes.py`.
6. Use resulting changes as input to LExecutorCC.

### Reproduce RQ1 - Effectiveness

### Reproduce RQ2 - Regression Testing

To check whether the existing regressions tests, of all 224 code changes that are manually annotated,
correctly identify a code change as semantics-preserving or semantics-changing, we proceed as follows:

1. Check whether the corresponding commit has any associated continuous integration logs on the GitHub Workflows platform:
    * Manually go through each annotation in `annotated_changes.json`. For each commit version, i.e. old and new, identify if they have associated continuous integration logs on the GitHub Workflows platform. If such logs exists, we compare the test execution results for the commits of the two versions and add the verdict to a file in `./evaluation/regression_tests/project_name_github_verdict.json`. Notice we save three filds for each code change: *repo*, *sha*, and *final_result*. E.g. `./evaluation/regression_tests/airflow_github_verdict.json`.

2. Try to run the tests locally:  
    * For each project with tests, execute its corresponding script in `python3 repos/evaluate_tests_project_name.py`.  The results will be saved in `./evaluation/regression_tests/project_name_tests_verdict.json`.

Finally, summarize the results running:
`python3 repos/summarize_tests_verdict.py`

### Reproduce RQ3 - Retraining model

1. Get DyPyBench [link](https://github.com/sola-st/DyPyBench)
   * Follow instructions on how to set up DyPyBench, including adding the patches.
2. Exchange LExecutor files in `./retraining/files_to_replace` with corresponding files in DyPyBench container.
3. Copy `./retraining/all_files_test.txt` into container.
4. Collect traces:
    * Note: we used all projects available in DyPyBench except 3 and 19 as those are already part of our evaluation data.
    * run `python3 dypybench.py --test 1 2 ... 50`
    * run `python3 dypybench.py --lex_instrument 1 2 ... 50 --lex_file all_files_test.txt`
    * run `python3 dypybench.py --lex_test 1 2 ... 50`
    * Note: if due to limited disk space it is not possible to run all projects at once, do them in batches and store the temp folder for later use.
    * run `find ./temp -type f -name "trace_*.h5" > traces.txt` to collect all paths to the traces.
5. run `python3 -m lexecutor.predictors.codeT5.PrepareData --iids iids.json --traces traces.txt --output_dir .` to obtain the training tensors.
6. Copy tensors (train.pt, validate.pt) to gpu machine and install [LExecutor](https://github.com/michaelpradel/LExecutor/) if necessary (make sure to also replace the necessary files see step 2).
7. run `python3 -m lexecutor.predictors.codeT5.FineTune --train_tensors train.pt --validate_tensors validate.pt --output_dir . --stats_dir .` to start the finetuning.

### Reproduce RQ4 - LExecutor Improvements (coverage)

1. For obtaining the results of the baseline run the baseline version of LExecutorCC `./coverage/Baseline_for_coverage/LExecutor/` on the `annotated_changes.json` dataset.
2. The baseline is executed in the same way as the regular LExceutorCC, i.e., `python -m lexecutor.Runner --commits annotated_changes.json --action [instrument|run]` (make sure to install the baseline in a separate virtual environment).
3. For obtaining the results of for LExecutorCC, simply run LExecutorCC on the `annotated_changes.json` dataset, but make sure to remove the condition
`result == 'changing'` from line 212 in `Runner.py` to make sure that the approach does not stop as soon as it detects a change in semantics.

### Reproduce RQ5 - Efficiency

The Results for RQ4 are obtained by analyzing the logs obtained from running LExecutorCC on `annotated_changes.json`.

## Download Data

Most results of our evaluation can be found in their corresponding directories.
However, as some of the data is too large, we added it as a release. 
All results from the experiments can be found [here](https://github.com/sola-st/master-thesis-lars-groeninger/releases/tag/evaluation).


