def process_input(self, data, input_prompt, lineno):
    decorator, input, rest = data
    image_file = None
    image_directive = None
    is_verbatim = decorator=='@verbatim' or self.is_verbatim
    is_doctest = (decorator is not None and \
                     decorator.startswith('@doctest')) or self.is_doctest
    is_suppress = decorator=='@suppress' or self.is_suppress
    is_okexcept = decorator=='@okexcept' or self.is_okexcept
    is_okwarning = decorator=='@okwarning' or self.is_okwarning
    is_savefig = decorator is not None and \
                     decorator.startswith('@savefig')
    input_lines = input.split('\n')
    if len(input_lines) > 1:
       if input_lines[-1] != "":
           input_lines.append('') 
    continuation = '   %s:'%''.join(['.']*(len(str(lineno))+2))
    if is_savefig:
        image_file, image_directive = self.process_image(decorator)
    ret = []
    is_semicolon = False
    if is_suppress and self.hold_count:
        store_history = False
    else:
        store_history = True
    with warnings.catch_warnings(record=True) as ws:
        for i, line in enumerate(input_lines):
            if line.endswith(';'):
                is_semicolon = True
            if i == 0:
                if is_verbatim:
                    self.process_input_line('')
                    self.IP.execution_count += 1 
                else:
                    self.process_input_line(line, store_history=store_history)
                formatted_line = '%s %s'%(input_prompt, line)
            else:
                if not is_verbatim:
                    self.process_input_line(line, store_history=store_history)
                formatted_line = '%s %s'%(continuation, line)
            if not is_suppress:
                ret.append(formatted_line)
    if not is_suppress and len(rest.strip()) and is_verbatim:
        ret.append(rest)
    self.cout.seek(0)
    output = self.cout.read()
    if not is_suppress and not is_semicolon:
        ret.append(output)
    elif is_semicolon: 
        ret.append('')
    filename = self.state.document.current_source
    lineno = self.state.document.current_line
    if not is_okexcept and "Traceback" in output:
        s =  "\nException in %s at block ending on line %s\n" % (filename, lineno)
        s += "Specify :okexcept: as an option in the ipython:: block to suppress this message\n"
        sys.stdout.write('\n\n>>>' + ('-' * 73))
        sys.stdout.write(s)
        sys.stdout.write(output)
        sys.stdout.write('<<<' + ('-' * 73) + '\n\n')
    if not is_okwarning:
        for w in ws:
            s =  "\nWarning in %s at block ending on line %s\n" % (filename, lineno)
            s += "Specify :okwarning: as an option in the ipython:: block to suppress this message\n"
            sys.stdout.write('\n\n>>>' + ('-' * 73))
            sys.stdout.write(s)
            sys.stdout.write('-' * 76 + '\n')
            s=warnings.formatwarning(w.message, w.category,
                                     w.filename, w.lineno, w.line)
            sys.stdout.write(s)
            sys.stdout.write('<<<' + ('-' * 73) + '\n')
    self.cout.truncate(0)
    return (ret, input_lines, output, is_doctest, decorator, image_file,
                image_directive)
