from typing import NoReturn
import sys,os,argparse
abs_path=os.path.abspath(os.path.dirname(__file__))

# abs_path=os.path.abspath(os.path.dirname(__file__))
# # print("abs_path: ",abs_path)
# pack_path="/".join(abs_path.split("/")[:-1])
# # print(pack_path)
# sys.path.append(pack_path)

from RefactoringIdioms import main
__all__ = ["run_main"]

def run_main():
    abs_path=os.getcwd()
    # print("hello: ",abs_path)
    parser = argparse.ArgumentParser(description='RefactoringIdioms')
    parser.add_argument('--envname', type=str,
                        help='envname', default="CartPole-v0")
    # parser.add_argument('--filepath', type=str,
    #                     help='filepath', default=abs_path + "/file.py")
    # parser.add_argument('--filepath', type=str,
    #                     help='filepath', default=abs_path + "/")
    parser.add_argument('--filepath', type=str,
                        help='filepath', default= "./")

    parser.add_argument('--idiom', type=str,
                        help='idiom', default="All")
    parser.add_argument('--outputdir', type=str,
                        help='outputdir', default="./RefactoringIdiomsOutputdir/")
    parser.add_argument('--flag_merge_allcodepair', type=int,
                        help='flag_merge_allcodepair', default=1)
    parser.add_argument('--output_codepair', type=str,
                        help='output_codepair', default="result.json")
    parser.add_argument('--flag_console_output', type=str,
                        help='flag_console_output', default=1)
    args = parser.parse_args()


    try:
        main.main(args)
    except KeyboardInterrupt:
        sys.exit(1)
# run_main()