# Steps to reproduce evaluation

## RQ1: Retraining model

1. Get DyPyBench [link](https://github.com/sola-st/DyPyBench)
   * Follow instructions on how to set up DyPyBench, including adding the patches.
2. Exchange LExecutor files in `./retraining/files_to_replace` with corresponding files in DyPyBench container.
3. Copy `./retraining/all_files_test.txt` into container.
4. Collect traces:
    * run `python3 dypybench.py --test 1 2 3 ... 50`
    * run `python3 dypybench.py --lex_instrument 1 2 3 ... 50 --lex_file all_files_test.txt`
    * run `python3 dypybench.py --lex_test 1 2 3 ... 50`
    * Note: if due to limited disk space it is not possible to run all projects at once, do them in batches and store the temp folder for later use.
    * run `find ./temp -type f -name "trace_*.h5" > traces.txt` to collect all paths to the traces.
5. run `python3 -m lexecutor.predictors.codeT5.PrepareData --iids iids.json --traces traces.txt --output_dir .` to obtain the training tensors.
6. Copy tensors (train.pt, validate.pt) to gpu machine and install [LExecutor](https://github.com/michaelpradel/LExecutor/) if necessary (make sure to also replace the necessary files see step 2).
7. run `python3 -m lexecutor.predictors.codeT5.FineTune --train_tensors train.pt --validate_tensors validate.pt --output_dir . --stats_dir .` to start the finetuning.

## RQ2: Accuracy

## RQ3: Automated Tools

### LLM

0. Assuming you are in `./llm`
1. Create file .secret and paste your API token into it
2. Run `python3 llm_creator_api.py`
3. Run `python3 create_changes.py`
4. Use resulting changes as input to LExecutorCC

### Pythonic Transformations

1. Download artifact from PyPy [link](https://pypi.org/project/RefactoringIdioms/)
2. Remove all dependencies from `pyproject.toml` and install project (`pip install .`)
3. Manually add missing dependencies (you can test if it works by running `python3 main.py`).
4. Run `python3 create_func_files.py` to create functions for transformations.
5. Copy `func_files` directory and `runner.py` into source directory of RefactoringIdioms (same directory as main.py)
6. In `main.py` comment out or delete all lines that delete "output_dir" (521, 522, 557, 558, 573, 574)
7. Execute `python3 runner.py`.
8. Manually fix syntax errors in created files
9. Copy the `RefactoringIdiomsOutputdir` and `func_files` folder to `./python_idiomatic_transformation`.
10. Run `python3 create_changes.py`
11. Manually fix indentation errors in resulting transformations.
12. Use the resulting `transformation_changes.json` file as input to LExecutorCC.
