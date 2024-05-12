import argparse,os,sys,ast
import copy,shutil

abs_path=os.path.abspath(os.path.dirname(__file__))
# print("abs_path_1: ",abs_path)
pack_path="/".join(abs_path.split("/")[:-1])
# print(pack_path)
# sys.path.append(pack_path)
sys.path.append("/".join(abs_path.split("/")[:-1]))
# sys.path.append("/".join(abs_path.split("/")[:-2]))
from RefactoringIdioms.extract_transform_complicate_code_new import \
    transform_for_else_compli_to_simple_improve_copy_result_csv, extract_compli_var_unpack_for_target_improve_new, \
    extract_compli_multiple_assign_code_improve_complete_improve
from RefactoringIdioms.extract_transform_complicate_code_new.comprehension import \
    extract_compli_for_comprehension_only_one_stmt_improve, extract_compli_for_comprehension_dict_only_one_stmt_new, \
    extract_compli_for_comprehension_set_only_one_stmt
from RefactoringIdioms.extract_transform_complicate_code_new import extract_compli_var_unpack_star_call_improve, \
    extract_compli_truth_value_test_code_remove_is_isnot, transform_chained_comparison_compli_to_simple
import util
import CodeInfo
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
def save_output(outputpath):
    result=dict()
    util.save_file_path(outputpath,result)
def format_code_list(code_pair_list,filepath=''):
    dict_code_pair=dict()
    format_code_list=[]
    for  ind_idiom,(idiom,cl, me, oldcode, new_code,lineno_list) in enumerate(code_pair_list):
        code_info_cla = CodeInfo.CodeInfo(filepath, idiom,cl, me, oldcode, new_code,lineno_list)
        # print(code_info_cla.__dict__)
        print(f">>>Result{ind_idiom+1}",code_info_cla.full_info())
        format_code_list.append(code_info_cla)
        if idiom in dict_code_pair:
            dict_code_pair[ idiom].append(code_info_cla)
        else:
            dict_code_pair[idiom]=[code_info_cla]


        # format_code_list.append(code_info_cla.__dict__)
    return format_code_list,dict_code_pair
    # return code_dict
def get_list_comprehension(code_frag):
    print(">>>>>>>>>Checking List Comprehension")
    code_pair_list = extract_compli_for_comprehension_only_one_stmt_improve.get_list_compreh(code_frag)
    for e in code_pair_list:
        e.insert(0, "List Comprehension")
    return code_pair_list

def get_set_comprehension(code_frag):
    print(">>>>>>>>>Checking Set Comprehension")
    code_pair_list = extract_compli_for_comprehension_set_only_one_stmt.get_set_compreh(code_frag)

    for e in code_pair_list:
        e.insert(0, "Set Comprehension")
    return code_pair_list
def get_dict_comprehension(code_frag):
    print(">>>>>>>>>Checking Dict Comprehension")

    code_pair_list = extract_compli_for_comprehension_dict_only_one_stmt_new.get_dict_compreh(code_frag)
    for e in code_pair_list:
        e.insert(0, "Dict Comprehension")
    return code_pair_list
def get_chain_compare(code_frag):
    print(">>>>>>>>>Checking Chain Comparison")
    code_pair_list_chain_compare = transform_chained_comparison_compli_to_simple.get_chain_compare(code_frag)
    # code_pair_list.extend([e.insert(0,"Chain Compare") for e in code_pair_list_chain_compare])
    for e in code_pair_list_chain_compare:
        e.insert(0, "Chain Compare")
    return code_pair_list_chain_compare

def get_truth_value_test(code_frag):
    print(">>>>>>>>>Checking Truth Value Test")
    code_pair_list_truth_value = extract_compli_truth_value_test_code_remove_is_isnot.get_truth_value_test_code(
        code_frag)
    # code_pair_list.extend([e.insert(0,"Truth Value Test") for e in code_pair_list_truth_value])
    for e in code_pair_list_truth_value:
        e.insert(0, "Truth Value Test")
    return code_pair_list_truth_value


def get_ass_multi_targets(code_frag):
    print(">>>>>>>>>Checking Assign Multiple Targets")

    code_pair_list_assign_multi_targets = extract_compli_multiple_assign_code_improve_complete_improve.transform_multiple_assign_code(
        code_frag)
    # code_pair_list.extend([e.insert(0,"Assign Multi Targets") for e in code_pair_list_assign_multi_targets])
    for e in code_pair_list_assign_multi_targets:
        e.insert(0, "Assign Multi Targets")
    return code_pair_list_assign_multi_targets


def get_for_multi_targets(code_frag):
    print(">>>>>>>>>Checking For Multiple Targets")

    code_pair_list_for_multi_target = extract_compli_var_unpack_for_target_improve_new.transform_for_multiple_targets_code(
        code_frag)
    # code_pair_list.extend([e.insert(0,"For Multi Targets") for e in code_pair_list_for_multi_target])
    for e in code_pair_list_for_multi_target:
        e.insert(0, "For Multi Targets")
    return code_pair_list_for_multi_target


def get_for_else(code_frag):
    print(">>>>>>>>>Checking For Else")

    code_pair_listfor_else = transform_for_else_compli_to_simple_improve_copy_result_csv.transform_for_else_code(
        code_frag)
    for e in code_pair_listfor_else:
        e.insert(0, "For Else")
        # code_pair_list.append(e)
    return code_pair_listfor_else


def get_star_call(code_frag):
    # code_pair_list.extend([e.insert(0,"For Else") for e in code_pair_listfor_else])
    print(">>>>>>>>>Checking Star in Function Call")

    code_pair_list_call_star = extract_compli_var_unpack_star_call_improve.transform_star_call_code(
        code_frag)
    for e in code_pair_list_call_star:
        e.insert(0, "Call Star")
        # code_pair_list.append(e)
    return code_pair_list_call_star

def get_refactoring(idiom,code_frag,filepath):
    # print(f"************For File {filepath.split('/')[-1]}, begin to find refactorable non-idiomatic code with Python idioms************")
    #
    code_pair_list=[]
    # code_frag=util.load_file_path(file_path=filepath)
    if idiom == 'List Comprehension':
        code_pair_list = get_list_comprehension(code_frag)
        if code_pair_list:
            pass
            # print("code_list: ",code_pair_list,jsonify(code_pair_list).json[0][0])

        # return jsonify(code_pair_list)
        pass
    elif idiom == 'Set Comprehension':

        code_pair_list = get_set_comprehension(code_frag)
        if code_pair_list:
            pass
            # print("code_list: ", code_pair_list, jsonify(code_pair_list).json[0][0])

        # return jsonify(code_pair_list)
        pass
    elif idiom == 'Dict Comprehension':

        code_pair_list = get_dict_comprehension(code_frag)
        # return jsonify(code_pair_list)

        pass
    elif idiom == 'Chain Comparison':

        code_pair_list =get_chain_compare(code_frag)
        # return jsonify(code_pair_list)

        pass
    elif idiom == 'Truth Value Test':

        code_pair_list = get_truth_value_test(code_frag)
        # return jsonify(code_pair_list)

        pass
    elif idiom == 'Assign Multiple Targets':

        code_pair_list = get_ass_multi_targets(
            code_frag)
        # return jsonify(code_pair_list)

        pass
    elif idiom == 'For Multiple Targets':

        code_pair_list = get_for_multi_targets(
            code_frag)

        # return jsonify(code_pair_list)
        pass
    elif idiom == 'For Else':

        code_pair_list = get_for_else(
            code_frag)
        # return jsonify(code_pair_list)

        pass
    elif idiom == 'Star in Call':

        code_pair_list = get_star_call(
            code_frag)
        # return jsonify(code_pair_list)


        pass
    elif idiom == 'All':
        # idioms = ['All','List Comprehension', 'Set Comprehension', 'Dict Comprehension','Chain Comparison',
        # 'Truth Value Test','Assign Multiple Targets','For Multiple Targets','For Else'
        # ,'Star in Call']
        code_pair_list = []
        # print("code_frag")
        # print(code_frag)
        code_pair_list_compre = get_list_comprehension(code_frag)
        code_pair_list.extend(code_pair_list_compre)

        code_pair_set_compre=get_set_comprehension(code_frag)
        code_pair_list.extend(code_pair_set_compre)

        code_pair_dict_compre=get_dict_comprehension(code_frag)
        code_pair_list.extend(code_pair_dict_compre)

        code_pair_chain_compare = get_chain_compare(code_frag)
        code_pair_list.extend(code_pair_chain_compare)

        code_pair_truth_test = get_truth_value_test(code_frag)
        code_pair_list.extend(code_pair_truth_test)

        code_pair_multi_ass = get_ass_multi_targets(code_frag)
        code_pair_list.extend(code_pair_multi_ass)

        code_pair_for_multi_target=get_for_multi_targets(code_frag)
        code_pair_list.extend(code_pair_for_multi_target)

        code_pair_for_else = get_for_else(code_frag)
        code_pair_list.extend(code_pair_for_else)

        code_pair_star_call = get_star_call(code_frag)

        code_pair_list.extend(code_pair_star_call)

    new_code_list,dict_code_pair = format_code_list(code_pair_list,filepath)
    return new_code_list,dict_code_pair
def transform_line_no(code_list):
    dict_file_lineno_code=dict()
    new_code_list=[]

    for code in code_list:
        new_code_list.append(
            [code.lineno[0][0][0], code.lineno[-1][-1][0], code.compli_code,code.simple_code,code.idiom,code.lineno])
        #
        # for (e_lineno_start,e_col_start),(e_lineno_end,e_col_end) in code.lineno:
        #     # start_key=e_lineno_start+e_col_startj
        #     # end_key=float(f'{e_lineno_end}.{e_col_end}')
        #
        #     # key=(float(f'{e_lineno_start}.{e_col_start}'),float(f'{e_lineno_end}.{e_col_end}'))
        #     new_code_list.append([e_lineno_start,e_col_start,e_lineno_end,e_col_end,code.compli_code,code.simple_code,code.idiom])
        #     # dict_file_lineno_code[key]=[code.compli_code,code.simple_code,code.idiom]
    # sorted_new_code_list=sorted(new_code_list, key=lambda i: (i[0],i[1],-i[2], -i[3]))
    sorted_new_code_list=sorted(new_code_list, key=lambda i: (i[0],-i[1]))

    # print("sorted_new_code_list")
    # for e in sorted_new_code_list:
    #     print(e)
    return sorted_new_code_list
def replace_code(lineno_list,simp_code, code_fragment_list, bias=0):
    # lineno_list = chain_compare_code[-1]
    # # compli_code=chain_compare_code[-4]
    # simp_code = chain_compare_code[-3]
    new_code_fragment_list = []
    # print("simp_code: ", simp_code, code_fragment_list,lineno_list)
    pre_lineno = None
    for ind, ((star_row, star_col), (end_row, end_col)) in enumerate(lineno_list):
        star_row_new = star_row - bias - 1
        end_row_new = end_row - bias - 1
        replace_code = simp_code[ind]
        # print('replace_code: ',replace_code,star_row,star_col,end_row, end_col,code_fragment_list,star_row_new,end_row_new)
        if pre_lineno and pre_lineno[1] < star_row_new:  # len(new_code_fragment_list) < star_row_new:
            new_code_fragment_list += code_fragment_list[pre_lineno[1]+1:star_row_new]
        elif not pre_lineno and star_row_new>=1:
            new_code_fragment_list += code_fragment_list[:star_row_new]
        if pre_lineno:
            pre_lineno=max(star_row_new,pre_lineno[0]), max(end_row_new,pre_lineno[1])
        else:
            pre_lineno=star_row_new, end_row_new
        # pre_lineno=star_row_new,end_row_new
        if not replace_code:
            # new_code_fragment_list.append('')
            # print("each new_code_fragment_list: ", new_code_fragment_list,code_fragment_list[end_row_new + 1:])
            if ind == len(lineno_list) - 1:
                new_code_fragment_list += code_fragment_list[end_row_new + 1:]
            # print("each new_code_fragment_list: ", new_code_fragment_list,code_fragment_list[end_row_new + 1:])
            continue
        code_str = code_fragment_list[star_row_new][:star_col] + replace_code + code_fragment_list[end_row_new][
                                                                                end_col:]
        # print("each code_str: ",code_str)
        new_code_fragment_list.append(code_str)
        if ind == len(lineno_list) - 1:
            new_code_fragment_list += code_fragment_list[end_row_new + 1:]

    # print("each new_code_fragment_list: ", new_code_fragment_list)
    return new_code_fragment_list
def file_replace(abs_path, each_file_code_list):


    new_content=[]
    new_sorted_code_list=transform_line_no(each_file_code_list)
    group_new_sorted_code_list=[]
    prelineno=None
    for ind_group, (start_row, end_row, compli_code,simple_code,idiom,lineno) \
        in enumerate(new_sorted_code_list):
        if not prelineno:
            group_new_sorted_code_list.append([[start_row, end_row,compli_code,simple_code,idiom,lineno]])
            prelineno = start_row, end_row
            continue
        if start_row<=prelineno[1]:# if start_row <>>= group_new_sorted_code_list[-1][0][0] and end_row <= group_new_sorted_code_list[-1][0][1]:
            group_new_sorted_code_list[-1].append([start_row, end_row,compli_code,simple_code,idiom,lineno])
        else:
            group_new_sorted_code_list.append([[start_row, end_row,compli_code,simple_code,idiom,lineno]])
        if not prelineno:
            prelineno=start_row, end_row
        else:
            prelineno = min(start_row,prelineno[0]), max(end_row,prelineno[1])

    with open(abs_path) as f:
        lines=f.readlines()
        # print("lines: ",lines)
        # return None
        pre_lineno=None
        if not group_new_sorted_code_list:
            return "".join(lines)
        for ind_group,each_group_code in  enumerate(group_new_sorted_code_list):
            # print("1. each_group_code: ",each_group_code,len(each_group_code))
            bias=each_group_code[0][0]-1
            code_fragment_list = lines[each_group_code[0][0]-1:each_group_code[0][1]]
            # print("2. code_fragment_list: ",code_fragment_list)
            code_fragment_list_copy=copy.deepcopy(code_fragment_list)
            count_space = 0
            for e in code_fragment_list[0]:
                if e == " ":
                    count_space += 1
                else:
                    break

            for ind_each_code,each_code in enumerate(each_group_code):
                start_row, end_row, compli_code, simple_code, idiom, lineno = each_code
                if not pre_lineno and start_row-1 > 0:
                    new_content.extend(lines[len(new_content):start_row-1])
                    # print("add some extra*********new_content:\n",start_row,"".join(new_content),"*******")

                elif pre_lineno and pre_lineno[1]<start_row-1:
                    new_content.extend(lines[pre_lineno[1]:start_row - 1])
                    # print("add some extra*********new_content:\n",pre_lineno[1], start_row,"".join(new_content),"*******")

                if len(each_group_code)==1:
                    lineno_list = each_code[-1]
                    # compli_code=chain_compare_code[-4]
                    simp_code = each_code[-3]
                    # print(lineno_list,simp_code,code_fragment_list)

                    code_fragment_list = replace_code(lineno_list,simp_code, code_fragment_list,bias)
                    # print("old_content: ","".join(new_content),pre_lineno,start_row, end_row)
                    new_content.extend(code_fragment_list)
                    # print("new_content: ",code_fragment_list,"".join(new_content))
                else:
                    # break
                    # if ind_each_code==0:
                    # print("count_space: ",count_space)
                    for ind_code_frag,e in enumerate(code_fragment_list):
                        if e!="\n":
                            code_fragment_list[ind_code_frag] = code_fragment_list[ind_code_frag][count_space:]
                    # print(">>>>>>>>>>>>>Idiom: ",ind_each_code,idiom,code_fragment_list,"\n","".join(code_fragment_list),count_space)

                    if idiom == 'List Comprehension':

                        # print(">>>List Comprehension code_fragment:\n","".join(code_fragment_list))
                        # print(">>>compli_code:\n","\n".join(compli_code))

                        code_pair_list = extract_compli_for_comprehension_only_one_stmt_improve.get_list_compreh_part_fragment("".join(code_fragment_list))

                        pass
                    elif idiom == 'Set Comprehension':
                        code_pair_list = extract_compli_for_comprehension_set_only_one_stmt.get_part_set_compreh("".join(code_fragment_list))
                        pass
                    elif idiom == 'Dict Comprehension':
                        code_pair_list = extract_compli_for_comprehension_dict_only_one_stmt_new.get_part_dict_compreh(
                            "".join(code_fragment_list))
                        pass
                    elif idiom == 'For Multi Targets':
                        # print(" Come For Multiple Targets")
                        code_pair_list = extract_compli_var_unpack_for_target_improve_new.get_for_multi_tar_part_fragment\
                            ("".join(code_fragment_list))
                    elif idiom == 'For Else':
                        # print("For Else code_fragment_list: \n",code_fragment_list,"".join(code_fragment_list))
                        code_pair_list = transform_for_else_compli_to_simple_improve_copy_result_csv.transform_part_for_else_code(
                            "".join(code_fragment_list))
                        # return jsonify(code_pair_list)

                        pass
                    elif idiom == 'Assign Multi Targets':
                        # print(" Come Assign Multiple Targets",code_fragment_list)
                        code_pair_list = extract_compli_multiple_assign_code_improve_complete_improve.transform_part_multiple_assign_code(
                            "".join(code_fragment_list))

                    elif idiom == "Truth Value Test":
                        k = 0
                        while 1:
                            try:
                                # print(" Come Truth Value Test", code_fragment_list)
                                tree = ast.parse("".join(code_fragment_list))
                                code_pair_list = extract_compli_truth_value_test_code_remove_is_isnot.get_part_truth_value_test_code("".join(code_fragment_list))
                                break
                            except:
                                k += 1
                                code_fragment_list.append(lines[each_group_code[0][1]][count_space:])
                        if k:
                            code_fragment_list=code_fragment_list[:-k]

                        # code_pair_list = extract_compli_multiple_assign_code_improve_complete_improve.transform_part_multiple_assign_code(
                        #     "".join(code_fragment_list))
                    elif idiom == "Chain Compare":
                        k = 0
                        while 1:
                            try:
                                tree = ast.parse("".join(code_fragment_list))
                                # print(" Come Chain Compare", code_fragment_list)
                                code_pair_list = transform_chained_comparison_compli_to_simple.get_part_chain_compare("".join(code_fragment_list))
                                break
                            except:
                                k += 1
                                code_fragment_list.append(lines[each_group_code[0][1]][count_space:])
                        if k:
                                code_fragment_list = code_fragment_list[:-k]
                            # code_pair_list = extract_compli_truth_value_test_code_remove_is_isnot.get_part_truth_value_test_code("".join(code_fragment_list))
                    elif idiom == "Call Star":
                        k=0
                        while 1:
                            try:
                                # print(" Come Call Star", code_fragment_list)
                                tree = ast.parse("".join(code_fragment_list))
                                code_pair_list = extract_compli_var_unpack_star_call_improve.get_info_from_code_fragment(
                                    "".join(code_fragment_list))
                                break
                            except:
                                k+=1
                                code_fragment_list.append(lines[each_group_code[0][1]][count_space:])
                        if k:
                                code_fragment_list = code_fragment_list[:-k]


                    #     new_lineno_list = code_pair_list[0][-1]
                    # # compli_code=chain_compare_code[-4]
                    #     simp_code = code_pair_list[0][-2]
                    else:
                        # print(" Come other ",idiom)
                        for ind_code_frag, e in enumerate(code_fragment_list):
                            if e != "\n":
                                code_fragment_list[ind_code_frag] = " " * count_space +code_fragment_list[ind_code_frag]
                        if ind_each_code == len(each_group_code) - 1:
                            new_content.extend(code_fragment_list)
                            # print(">>>*********new_content:\n", "".join(new_content))
                        if pre_lineno:
                            pre_lineno = max(start_row, pre_lineno[0]), max(end_row, pre_lineno[1])
                        else:
                            pre_lineno = start_row, end_row
                        continue
                    if not code_pair_list:
                        for ind_code_frag, e in enumerate(code_fragment_list):
                            if e != "\n":
                                code_fragment_list[ind_code_frag] = " " * count_space +code_fragment_list[ind_code_frag]
                        if ind_each_code == len(each_group_code) - 1:
                            new_content.extend(code_fragment_list)
                            # print(">>>*********new_content:\n", "".join(new_content))
                        if pre_lineno:
                            pre_lineno = max(start_row, pre_lineno[0]), max(end_row, pre_lineno[1])
                        else:
                            pre_lineno = start_row, end_row
                        continue
                    # print("code_pair_list: ",code_pair_list)
                    new_lineno_list = code_pair_list[0][-1]
                    # # compli_code=chain_compare_code[-4]
                    simp_code = code_pair_list[0][-2]
                    code_fragment_list = replace_code(new_lineno_list, simp_code, code_fragment_list)
                    # print(">>>new replace code_fragment_list: ", code_fragment_list)
                    # code_fragment_list[0] = " " * count_space + code_fragment_list[0]
                    code_fragment_list=''.join(code_fragment_list)
                    code_fragment_list=code_fragment_list.split("\n")

                    for ind_trans, e in enumerate(code_fragment_list):
                        if e != "":
                            code_fragment_list[ind_trans] = " " * count_space + code_fragment_list[ind_trans]
                        if ind_trans!=len(code_fragment_list)-1:
                                code_fragment_list[ind_trans]+='\n'

                    # print(">>>*********new new replace code_fragment_list:\n", ''.join(code_fragment_list))

                    if ind_each_code==len(each_group_code)-1:
                        new_content.extend(code_fragment_list)
                        # print(">>>*********new_content:\n", "".join(new_content))

                # print("each_time_code: ",new_content,start_row, end_row)
                # print(">>>>>each code\n","".join(new_content))
                if pre_lineno:
                    pre_lineno=max(start_row,pre_lineno[0]), max(end_row,pre_lineno[1])
                else:
                    pre_lineno=start_row, end_row
            if ind_group==len(group_new_sorted_code_list)-1:
                    new_content.extend(lines[pre_lineno[1]:])



    return "".join(new_content)

def main(args):
    # args = parser.parse_args()
    filepath = args.filepath
    idiom = args.idiom
    # outputpath = args.outputpath
    outputpath = args.output_codepair
    output_dir= args.outputdir
    flag_outputdir_mergeallcodepair=args.flag_merge_allcodepair
    flag_console_output=args.flag_console_output
    # outputpath = args.codepair_ouputpath

    format_code_list=[]
    a = []
    for i in range(1):
        a.append(i)
    # envname = args.envname
    if os.path.isdir(filepath):
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        for path,dir_list,file_list in os.walk(filepath):
            for file_name in file_list:
                abs_path=os.path.join(path,file_name)
                save_dir=path[len(filepath):]
                # print(">>>>>save_dir: ",save_dir)
                if abs_path.endswith(".py"):
                    print(f"************For File {abs_path.split('/')[-1]}, begin to find refactorable non-idiomatic code with Python idioms************")

                    code_frag=util.load_file_path(file_path=abs_path)
                    each_file_code_list,dict_code_pair=get_refactoring(idiom, code_frag,abs_path)
                    # print(code_pair_list)
                    if not flag_outputdir_mergeallcodepair:

                        for ind_save,each_code_pair in enumerate(each_file_code_list):
                            new_content=file_replace(abs_path,[each_code_pair])
                            # print(">>>>>output_dir: ", output_dir,save_dir)
                            util.save_file_path("".join([output_dir,save_dir,"/",file_name[:-3],'_',str(ind_save+len(format_code_list)),'.py']),new_content)

                    else:
                        new_content=file_replace(abs_path,each_file_code_list)

                        util.save_file_path("".join([output_dir,save_dir,"/",file_name]),new_content)
                    print(f"************Result of {abs_path.split('/')[-1]} End************")

                    format_code_list.extend(each_file_code_list)
    else:
        file_name=filepath.split("/")[-1]
        print(
            f"************For File {filepath.split('/')[-1]}, begin to find refactorable non-idiomatic code with Python idioms************")
        code_frag = util.load_file_path(file_path=filepath)

        format_code_list,dict_code_pair=get_refactoring(idiom, code_frag,filepath)

        if not flag_outputdir_mergeallcodepair:
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            for ind_save, each_code_pair in enumerate(format_code_list):
                # print("come here")
                new_content = file_replace(filepath, [each_code_pair])
                # print("new_content: ",new_content)
                util.save_file_path("".join([output_dir, "/", file_name[:-3], '_', str(ind_save), '.py']),
                                    new_content)



                # util.save_file_path()

        else:
            new_content = file_replace(filepath, format_code_list)
            # print("new_content: ", new_content)
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            # print("new_content: ", new_content)
            util.save_file_path("".join([output_dir, "/",file_name] ), new_content)

            # util.save_file_path()
        print(f"************Result of {filepath.split('/')[-1]} End************")

    print(f"************Result is saved in {outputpath}************", )
    util.save_json_file_path(outputpath, [e.__dict__ for e in format_code_list])
    # print(args)
    # print("main.py main() finished!")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RefactoringIdioms')
    parser.add_argument('--envname', type=str,
                        help='envname', default="CartPole-v0")
    parser.add_argument('--filepath', type=str,
                        help='filepath', default=abs_path+"/file.py")
    # parser.add_argument('--filepath', type=str,
    #                     help='filepath', default=abs_path + "/")
    # parser.add_argument('--filepath', type=str,
    #                     help='filepath', default= "./")
    # parser.add_argument('--filepath', type=str,
    #                     help='filepath', default="/Users/zhangzejunzhangzejun/PycharmProjects/code")
    #
    parser.add_argument('--idiom', type=str,
                        help='idiom', default="All")
    # parser.add_argument('--idiom', type=str,
    #                     help='idiom', default="List Comprehension")
    parser.add_argument('--outputdir', type=str,
                        help='outputdir', default="./RefactoringIdiomsOutputdir/")
    # parser.add_argument('--outputdir', type=str,
    #                     help='outputdir', default="/Users/zhangzejunzhangzejun/PycharmProjects/code/RefactoringIdiomsOutputdir/")
    #
    # parser.add_argument('--flag_merge_allcodepair', type=str,
    #                     help='flag_merge_allcodepair', default=1)
    parser.add_argument('--flag_merge_allcodepair', type=int,
                        help='flag_merge_allcodepair', default=1)
    parser.add_argument('--output_codepair', type=str,
                        help='output_codepair', default="result.json")
    parser.add_argument('--flag_console_output', type=str,
                        help='flag_console_output', default=1)

    # parser.add_argument('--codepair_ouputpath', type=str,
    #                     help='codepair_ouputpath', default="result.json")
    # parser.add_argument('--outputdir', type=str,
    #                     help='outputdir', default="./RIdioms_dir/")

    args = parser.parse_args()
    print(args)
    main(args)
    filepath = args.filepath

    idiom = args.idiom
    # outputpath = args.codepair_ouputpath

    a=[]
    for i in range(1):
        a.append(i)
    # envname = args.envname
    # get_refactoring(idiom,filepath,outputpath)
    print(args)
    print("finished!")
    #    envname='MountainCar-v0'
    # env = gym.make(envname)
    # print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
