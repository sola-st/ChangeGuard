def password_generator(length=8):
    chars = ascii_letters + digits + punctuation
    return "".join(choice(chars) for x in range(length))
