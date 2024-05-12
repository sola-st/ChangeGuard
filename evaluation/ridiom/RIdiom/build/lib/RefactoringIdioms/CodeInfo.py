class CodeInfo():
    def __init__(self, file_path="" ,idiom="",cl="",me="",
                 compli_code="", simple_cod="",lineno=[]):
        self.file_path = file_path
        self.cl = cl
        self.me = me
        self.idiom = idiom
        self.compli_code = compli_code
        self.simple_code = simple_cod
        self.lineno=lineno
        self.keyno=None
    # def lineno_str(self):
    #     linestr=""
    #     line_list=[]
    #     for e_lineno_start,e_lineno_end in self.lineno:
    #         if not line_list:
    #             line_list.append([e_lineno_start,e_lineno_end])
    #         else:
    #             if e_lineno_start-line_list[-1][-1]<=1:
    #                 line_list[-1][-1]=e_lineno_end
    #             else:
    #                 line_list.append([e_lineno_start, e_lineno_end])
    #     linestr=[]
    #     for start,end in line_list:
    #         linestr.append(f"lines {start} to {end}")
    #     return ", ".join(linestr)
    # def get_key_lineno(self):
    #     return float(f'{self.lineno.e_lineno_start}.{e_col_start}'),float(f'{e_lineno_end}.{e_col_end}')
    #
    def lineno_str(self):
        linestr=""
        line_list=[]
        for (e_lineno_start,e_col_start),(e_lineno_end,e_col_end) in self.lineno:
            # print("(e_lineno_start,e_col_start),(e_lineno_end,e_col_end): ",(e_lineno_start,e_col_start),(e_lineno_end,e_col_end))
            # linestr.append(f"lines {e_lineno_start}:{e_col_start}, {end}")
            line_list.append([[e_lineno_start, e_col_start], [e_lineno_end, e_col_end]])

            # if not line_list:
            #     line_list.append([[e_lineno_start,e_col_start],[e_lineno_end,e_col_end]])
            # else:
            #     if e_lineno_start-line_list[-1][-1][0]<=1:
            #         line_list[-1][-1][0]=e_lineno_end
            #     else:
            #         line_list.append([[e_lineno_start,e_col_start],[e_lineno_end,e_col_end]])

        linestr=[]
        for (start_lineno,start_colno),(end_lineno,end_colno) in line_list:
            linestr.append(f"lines {start_lineno}:{start_colno} to {end_lineno}:{end_colno}")
        return ", ".join(linestr)

    def full_info(self):
        return "***".join(["Filepath: "+self.file_path, "Class: "+self.cl if self.cl else '', "Method: "+self.me if self.me else '',"Idiom: "+self.idiom,self.code_str()])

    def code_str(self):
        # print("linenolist: ",self.lineno)
        # print("complicated code: ", self.compli_code)
        # print("simple code: ", self.simple_code)

        lineno_str=self.lineno_str()

        # if '' in self.compli_code:
        #     self.compli_code.remove('')
        # if '' in self.simple_code:
        #     self.simple_code.remove('')
        compli_code_list=[e for e in self.compli_code if e!='']
        simple_code_list=[e for e in self.simple_code if e!='']
        codestr=f"***{lineno_str}\n"
        return "".join([codestr,"\n".join(compli_code_list),"\n-----is refactored into----->\n","\n".join(simple_code_list)])
        # return "".join([codestr,"".join(self.compli_code),"\n-----is refactored into----->\n","".join(self.simple_code)])


