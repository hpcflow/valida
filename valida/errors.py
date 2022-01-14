class ValidationFailure:
    def __init__(self, raise_error=False):
        # do some stuff

        if raise_error:
            raise ValidationError()  # pass some stuff


class DuplicateRule(Exception):
    pass


class IncompatibleRules(Exception):
    pass


class ValidationError(Exception):
    pass


class InvalidCallable(Exception):
    pass

