import os
file_path="./"
for path, dir_list, file_list in os.walk(file_path):
    for file_name in file_list:
        print(path, dir_list,file_name)