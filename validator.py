def is_valid_token(token):
    if token == ".":
        return True

    return len(token) == 2 and token[0] in "bw" and token[1] in "KQRBNP"
