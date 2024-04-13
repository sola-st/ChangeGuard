import subprocess
import sys

for i in range(299):
    subprocess.run(f'python main.py --filepath ./func_files/fun_{i}.py --output_codepair ./RefactoringIdiomsOutputdir/result_{i}.json', stdout=sys.stdout, stderr=sys.stderr)
