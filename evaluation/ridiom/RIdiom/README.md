# Refactoring non-idiomatic Python code with Python idioms


## Install:
For command line use, the package is installed with 

    python3 -m pip install RefactoringIdioms

 ## Running:
1).  Default command is to save all refactored files for all Python Idioms in the current directory in ./RefactoringIdiomsOutputdir/. And it can get <non-idiomatic code, idiomatic code> code pairs for all Python files in the current directory for all Python idioms, and save these code pairs in result.json in the current directory: 
	
     RIdiom

2).  Options: 

**--filepath "your filepath" (e.g., main.py)** is to refactor "your filepath" file. The default path is the current directory. 

**--idiom "IdiomName" (e.g., List Comprehension)** is to refactor for the specified "IdiomName". Options are List Comprehension, Set Comprehension, Dict Comprehension, Chain Comparison, Truth Value Test, Assign Multiple Targets, For Multiple Targets, For Else, Star in Call, All. The default idiom is "All" that means all idioms.

**--outputdir "your output folder" (e.g.,RefactoringIdiomsOutputdir/ )** is to save all refactored files in "your output folder". The default directory is "./RefactoringIdiomsOutputdir".

**--output_codepair "your output path" (e.g.,result.json )** is to save all code pairs in "your output folder". The default path is "result.json".

**--flag_merge_allcodepair (e.g., 1 )** means whether to store a separate file for each code pair. The values are 0 and 1. The 1 means refactor a file with all code pairs. The 0 means refactor a file with each code pair individually. The default value is 1.

For example, if you want to refactor code for a Python idiom in the given directory and save the refactored files in the given directory, you can execute the following command:

    RIdiom --filepath "your filepath" --idiom "IdiomName" --outputdir "your output folder" --output_codepair  "your output path" --flag_merge_allcodepair 1
## Web application: 
We also develop a web application for the code refactoring, you could access the application through the url: 47.242.131.128:5000
	
Each time, you could click code area to refresh.
	