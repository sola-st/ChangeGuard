def get_path_param_names(path):
    return set(re.findall("{(.*?)}", path))
