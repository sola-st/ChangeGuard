# Evaluation

Most results of the experiments can be found in their corresponding directories.
However, as some of the data is too large we added it as a release. All results from the experiments can be found [here](https://github.com/sola-st/master-thesis-lars-groeninger/releases/tag/evaluation).

> [!IMPORTANT]
> In order to repeat the evaluation steps the results from the experiments (corresponding `std_out.json` file) are required.
> Extract the files and copy them into the directory corresponding to their experiment. Note that some files need to be renamed, refer to `evaluation.py` to see how to name the files.

Alternatively one can repeat the experiments by following the steps at the bottom.

### Setup
To run `evaluation.py` one needs to install the matplotlib library.
```
pip install matplotlib
```

Everything required for the evaluation is part of the `evaluation.py` script.
Assuming that all the results of the experiments are copied in their respective directory,
the evaluation can simply be run by uncommenting the desired function and executing the
`evaluation.py` script.
```
python3 evaluation.py
```
Information about all manual inspections are stored in `manual_inspection.txt`.

To evaluate the results of the derived datasets, i.e., RIdiom, gpt-3.5, and gpt-4, either analyze them manually by looking at their respective `std_out.json` or use the functions in `evaluation.py` by adjusting the paths.

---
# Experiments
If you want to repeat the experiments you can follow the steps below. For some steps functionality is provided in `evaluation.py`.
> [!IMPORTANT]
> Make sure Git is installed since it is used to obtain the changed lines.
## RQ1 Effectiveness

### Base Dataset
Run LExecutorCC on collected and annotated dataset `annotated.json`.

### Complexity
* For the line length simply count the number of lines of the old version of the code changes in `annotated_changes.json` (make sure to use the field `old_clean_function` to disregard empty lines and comments).
* For the cyclomatic complexity we use [Radon](https://pypi.org/project/radon/). 
  1. We add the old versions of the functions in `annotated_changes.json` into a single file (once for all functions
  for which LExecutorCC did not reach the changed lines and once for functions for which LExecutorCC did).
  2. Analyze the created files by running:
      ```
      radon cc reached.py -s > reached.txt 
      ```
     (assuming all functions are stored in `reached.py`)
### LLM

0. Navigate to`./llm` directory.
1. Create file .secret and paste your API token (first line) and organization id (second line) into it.
2. Make sure the correct model in `llm_creator_api.py` is selected.
3. Run `python3 llm_creator_api.py`.
4. Clean the resulting `response.json`, e.g., by running the `remove_text.py` script. The cleaned version should only contain the changed function and no additional text from the model.
5. Run `python3 create_changes.py`.
6. Use resulting changes as input to LExecutorCC.

### Pythonic Transformations (RIdiom)

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


## RQ2: Retraining model

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

## RQ3: LExecutor Improvements (coverage)
1. For obtaining the results of the baseline run the baseline version of LExecutorCC `./coverage/Baseline_for_coverage/LExecutor/` on the `annotated_changes.json` dataset.
2. The baseline is executed in the same way as the regular LExceutorCC, i.e., `python -m lexecutor.Runner --commits annotated_changes.json --action [instrument|run]` (make sure to install the baseline in a separate virtual environment).
3. For obtaining the results of for LExecutorCC, simply run LExecutorCC on the `annotated_changes.json` dataset, but make sure to remove the condition
`result == 'changing'` from line 212 in `Runner.py` to make sure that the approach does not stop as soon as it detects a change in semantics.

## RQ4: Efficiency
The Results for RQ4 are obtained by analyzing the logs obtained from running LExecutorCC on `annotated_changes.json`.





