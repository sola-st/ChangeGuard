def tokenize(string):
    backslash , tokens , characters  = '\\', [''], iter(string)
    for char in characters:
        if char == backslash:
            next_char = next(characters, '')
            if next_char in self.special_characters:
                tokens.extend([Escaped(next_char), ''])
            else:
                tokens[-1] += char + next_char
        else:
            tokens[-1] += char
    return tokens
