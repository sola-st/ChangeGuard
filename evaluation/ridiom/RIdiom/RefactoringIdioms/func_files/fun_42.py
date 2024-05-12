def get_filename_max_length(directory):
    max_len = 255
    try:
        pathconf = os.pathconf
    except AttributeError:
        pass  
    else:
        try:
            max_len = pathconf(directory, 'PC_NAME_MAX')
        except OSError as e:
            if e.errno != errno.EINVAL:
                raise
    return max_len
