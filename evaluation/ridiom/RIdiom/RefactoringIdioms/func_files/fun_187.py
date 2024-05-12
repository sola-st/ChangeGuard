def tokenize(string):
    tokens = ['']
    characters = iter(string)
    for char in characters:
        if char == '\\':
            char = next(characters, '')
            if char not in self.special_characters:
                tokens[-1] += '\\' + char
            else:
                tokens.extend([Escaped(char), ''])
        else:
            tokens[-1] += char
    return tokens
