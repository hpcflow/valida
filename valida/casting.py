def cast_string_to_bool(s):
    if s.lower() == "true":
        return True
    elif s.lower() == "false":
        return False
    else:
        raise TypeError(f"Cannot cast {s!r} to a bool type.")


CAST_DTYPE_LOOKUP = {
    "str": str,
    "bool": bool,
    "int": int,
}
CAST_LOOKUP = {
    (str, bool): cast_string_to_bool,
    (str, int): int,
}
