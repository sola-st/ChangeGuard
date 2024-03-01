# master-thesis-lars-groeninger

---
## Data Collection

1. Starting from the root directory, navigate to the repos directory `cd repos`.
2. Clone all repositories for which you want to collect data, alternatively you can execute the clone_repos script `python clone_repos.py`.
3. Navigate to the scripts directory `cd ../scripts`.
4. Execute the fetch_commits script `python fetch_commits.py`.
    - To switch from collecting refactor commits to change commits, simply set the *REFACTOR* flag at top of the fetch_commit script to **False**.
    - After the script is finished executing the collected code changes are stored in a newly created directory called `extracted_commits` in JSON format.
    - Information about which commits have been skipped and for which reasons can be found in the `logs` directory.


## Annotating Code Changes
0. Make sure all the data Collection steps have been completed.
1. Navigate to the scripts directory `cd scripts`.
2. execute the open_commits script `python open_commits.py`.
   - To switch from opening refactor commits to change commits, simply set the *TYPE* flag at top of the open_commits script to **'change'**.
   - After executing the script you are asked to enter the repository that you would like to annotate.
   - Now the first commit is opened in a new tab in your browser.
   - Look at the commit and as soon as you have decided on whether the code change is semantics preserving or not, go back to the terminal and enter either **y** for semantics preserving, **n** for semantics changing, or **x** for unclear and hit enter.
   - The next commit opens and the process repeats until all the extracted commits of the repository have been processed.
   - If you want to stop early, simply press `ctrl + c` to interrupt the process. The script stores the index so the next time you execute it, you can continue where you left off.
---
