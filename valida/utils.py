def make_pre_processing_mixin_class(pre_processing_class, base_class):
    class_name = f"{base_class.__name__}{pre_processing_class.__name__}"
    new_class = globals().get(class_name)
    if not new_class:
        new_class = type(class_name, (pre_processing_class, base_class), {})
        new_class.PRE_PROCESSOR = pre_processing_class
        globals()[class_name] = new_class
    return new_class


def null_condition_binary_check(cond_1, cond_2):
    """Get the non-null condition of two conditions if one is null, otherwise return
    None."""
    return cond_1 if cond_2.is_null else (cond_2 if cond_1.is_null else None)


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)
