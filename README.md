# ChangeGuard: Validating Code Changes via Pairwise Learning-Guided Execution 

**ChangeGuard** is an approach that automatically identifies for a function-level code change whether it is semantics-preserving or semantics-changing. To achieve this, it uses LExecutor which is a learning-guided approach that makes it possible to execute arbitrary Python code.

This repository includes artifacts for reuse and reproduction of experimental results presented in our [FSE'25 paper](https://arxiv.org/abs/2410.16092).

> [!IMPORTANT]
> The code calls the project "LExecutorCC".

**Table of Contents**
  * [Installation](#installation)
  * [How-to-use](#how-to-use)
    + [Input format](#input-format)
    + [Running](#running)
  * [Reproducibility](#reproducibility)
    + [Reproduce Dataset Creation](#reproduce-dataset-creation)
    + [Reproduce RQ1 - Effectiveness](#reproduce-rq1---effectiveness)
    + [Reproduce RQ2 - Comparison with Regression Testing](#reproduce-rq2---comparison-with-regression-testing)
    + [Reproduce RQ3 - Accuracy of the Neural Model](#reproduce-rq3---accuracy-of-the-neural-model)
    + [Reproduce RQ4 - Robustness and Coverage](#reproduce-rq4---robustness-and-coverage)
    + [Reproduce RQ5 - Efficiency](#reproduce-rq5---efficiency)
  * [Download Data](#download-data)

## Installation

Clone ChangeGuard from GitHub
> [!IMPORTANT]
> Git must be installed. 
```bash
git clone https://github.com/sola-st/ChangeGuard && cd ChangeGuard
```

Make sure you are in the `./LExecutorCC/` directory

```bash
cd LExecutorCC
```

Create a virtual environment
> [!IMPORTANT]
> Python 3.8 must be installed. 
```
virtualenv -p /usr/bin/python3.8 changeGuard_env
```

Enter the virtual environment

```
source changeGuard_env/bin/activate
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
python3 -m lexecutor.Runner --commits example.json --action instrument
```

Execute the compare scripts

```
python3 -m lexecutor.Runner --commits example.json --action run
```

The results are stored in the `std_out.json` file.

## Reproducibility

> [!IMPORTANT]
> The steps bellow can be skipped by inspecting the results given in the [released dataset](#download-data).

### Reproduce Dataset Creation

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
> To switch from collecting refactor commits to change commits, simply set the *REFACTOR* flag at top of the `fetch_commit.py` script to **False**.
```
python fetch_commits.py
```

After the script is finished executing, the collected code changes are stored in a newly created directory called `extracted_commits` in JSON format.
Information about which commits have been skipped and for which reasons can be found in the `logs` directory.

##### Annotating Code Changes

> [!IMPORTANT]
> Make sure all the Data Collection steps have been completed.

Navigate to the scripts directory 

```
cd scripts
```

Open the commits of interest
> [!IMPORTANT]
> To switch from opening refactor commits to change commits, simply set the *TYPE* flag at top of the open_commits script to **'change'**.

```
python open_commits.py
```

After executing the script, you are asked to enter the repository that you would like to annotate.
When you inform it, the first commit is opened in a new tab in your browser.

Look at the commit and as soon as you have decided on whether the code change is semantics preserving or not, go back to the terminal and enter either **y** for semantics preserving, **n** for semantics changing, or **x** for unclear and hit enter.

The next commit opens and the process repeats until all the extracted commits of the repository have been processed.
If you want to stop early, simply press `ctrl + c` to interrupt the process. The script stores the index so the next time you execute it, you can continue where you left off.

The results are stored in the `annotated_changes.json` file.

#### Rule-based refactorings

> [!IMPORTANT]
> For this we use [RIdiom](https://pypi.org/project/RefactoringIdioms/).
> Requires Python 3.9

Install RIdiom as module in the `./evaluation/ridiom/RIdiom` directory 
```
pip install .
```

Manually add missing dependencies (you can test if it works by running `python3 main.py` in `./evaluation/ridiom/RIdiom/RefactoringIdioms/`).
We needed to install pathos

```
pip install pathos
```

Create functions for transformations

```
python3 create_func_files.py
```

Copy `./func_files` directory into source directory of RIdiom (`RIdiom/RefactoringIdioms/`)

Transform the functions

```
python3 runner.py
```

Manually fix errors in transformed code in `./RefactoringIdioms/RefactoringIdiomsOutputdir/`. 
Function 34, 212, 220, 223, 224, 231, 262, 268, and 285 needs to be fixed.

Navigate back to the `ridiom` directory and create the changes

```
python3 create_changes.py
```

The results are stored in the `transformation_changes.json` file.

#### Refactorings created by GPT-3.5 and GPT-4

> [!IMPORTANT]
> For this you need and API token from OpenAI.
> The model can be selected in the `llm_creator_api.py` file.

From the `./llm` directory, create a `.secret` file and paste your API token (first line) and organization id (second line) into it.

Transform the functions

```
python3 llm_creator_api.py
```

Clean the resulting `response.json`
> [!IMPORTANT]
> The cleaned version should only contain the changed function and no additional text from the model.

```
python3 remove_text.py
```
```
python3 create_changes.py
```

The results are stored in the `llm_changes_gpt*.json` file.

### Reproduce RQ1 - Effectiveness

Run ChangeGuard on the above datasets using the steps described in [Running](#running).
> [!IMPORTANT]
> Replace the input file according to the used dataset, e.g. `annotated_changes.json` for the manually annotated dataset.

To evaluate the results of the manually annotated and derived datasets, i.e., RIdiom, gpt-3.5, and gpt-4, either analyze them manually by looking at their respective `std_out.json` or use the functions in `evaluation.py` by adjusting the paths.

Our [released dataset](#download-data) contains the `std_out.json` generated for each dataset in `evaluation_base_dataset.zip`, `evaluation_RIdiom.zip`, `evaluation_gpt35.zip`, and `evaluation_gpt4.zip`.

### Reproduce RQ2 - Comparison with Regression Testing

To check whether the existing regressions tests, of all 224 code changes that are manually annotated,
correctly identify a code change as semantics-preserving or semantics-changing, we proceed as follows:

1. Check whether the corresponding commit has any associated continuous integration logs on the GitHub Workflows platform:
    * Manually go through each annotation in `annotated_changes.json`. For each commit version, i.e. old and new, identify if they have associated continuous integration logs on the GitHub Workflows platform. If such logs exists, we compare the test execution results for the commits of the two versions and add the verdict to a file in `./evaluation/regression_tests/project_name_github_verdict.json`. Notice we save three fields for each code change: *repo*, *sha*, and *final_result*. E.g. `./evaluation/regression_tests/airflow_github_verdict.json`.

2. Try to run the tests locally:  
    * For each project with tests, execute its corresponding script
    ```
    python3 repos/evaluate_tests_project_name.py
    ```

    The results will be saved in `./evaluation/regression_tests/project_name_tests_verdict.json`.

Finally, summarize the results
```
python3 repos/summarize_tests_verdict.py
```

### Reproduce RQ3 - Accuracy of the Neural Model

1. Get DyPyBench [link](https://github.com/sola-st/DyPyBench)
> [!IMPORTANT]
> Follow instructions on how to set up DyPyBench, including adding the patches.

2. Exchange LExecutor files in `./retraining/files_to_replace` with corresponding files in DyPyBench container.

3. Copy `./retraining/all_files_test.txt` into container.

4. Collect traces:
> [!IMPORTANT]
> We used all projects available in DyPyBench, except 3 and 19 as those are already part of our evaluation data.
> If due to limited disk space it is not possible to run all projects at once, do them in batches and store the temp folder for later use.
   ```
   python3 dypybench.py --test 1 2 ... 50
   python3 dypybench.py --lex_instrument 1 2 ... 50 --lex_file all_files_test.txt
   python3 dypybench.py --lex_test 1 2 ... 50
   find ./temp -type f -name "trace_*.h5" > traces.txt
   ```

5. Obtain the training tensors
```
python3 -m lexecutor.predictors.codeT5.PrepareData --iids iids.json --traces traces.txt --output_dir .
```

6. Copy tensors (train.pt, validate.pt) to gpu machine and install [LExecutor](https://github.com/michaelpradel/LExecutor/) if necessary (make sure to also replace the necessary files see step 2).

7. Fine-tune the model
```
python3 -m lexecutor.predictors.codeT5.FineTune --train_tensors train.pt --validate_tensors validate.pt --output_dir . --stats_dir .
```

The model we fine-tuned is available [here](https://github.com/sola-st/master-thesis-lars-groeninger/releases/tag/model).

### Reproduce RQ4 - Robustness and Coverage

Run the baseline, i.e. original LExecutor, on the `annotated_changes.json` dataset
> [!IMPORTANT]
> Make sure to install the baseline in a separate virtual environment following [these install instructions](https://github.com/michaelpradel/LExecutor/blob/main/INSTALL.md).
```
cd evaluation/coverage/Baseline_for_coverage/LExecutor/
python -m lexecutor.Runner --commits annotated_changes.json --action [instrument|run]
```

Run ChangeGuard on the `annotated_changes.json` dataset using the steps described in [Running](#running)
> [!IMPORTANT]
> Remove the condition `result == 'changing'` from line 212 in `Runner.py` to make sure that the approach does not stop as soon as it detects a change in semantics.

Our [released dataset](#download-data) contains the `std_out.json` generated with each approach in `coverage_approach.zip` and `coverage_baseline.zip`.

### Reproduce RQ5 - Efficiency

The Results for RQ5 are obtained by analyzing the logs obtained from running ChangeGuard on the `annotated_changes.json` dataset.
We refer to [Reproduce RQ1 - Effectiveness](#reproduce-rq1---effectiveness).

## Download Data

Most results of our evaluation can be found in their corresponding directories.
However, as some of the data is too large, we added it as a release. 
All results from the experiments can be found [here](https://github.com/sola-st/master-thesis-lars-groeninger/releases/tag/evaluation).