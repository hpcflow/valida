
def null_condition_binary_check(cond_1, cond_2):
    """Get the non-null condition of two conditions if one is null, otherwise return
    None."""
    return cond_1 if cond_2.is_null else (cond_2 if cond_1.is_null else None)


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)
