class TestResultDescription(enum.Enum):

    PRE_PROCESSING_RAISED = (
        "Condition pre-processing raised an exception on invocation."
    )
    CALLABLE_FALSE = "Condition callable returned `False`"
    CALLABLE_RAISED = "Condition callable raised an exception on invocation"
    BINARY_OP_FALSE = "Binary combination of two conditions callables returned `False`"
    NULL = None


class ConditionTest:
    """Class to represent the result of a condition test."""

    def __init__(self, condition, datum, raise_on_error, pre_processing=None):

        result = False
        failure_reason = TestResultDescription.NULL

        if pre_processing:
            try:
                datum = pre_processing(datum)
            except Exception:
                if raise_on_error:
                    raise
                failure_reason = TestResultDescription.PRE_PROCESSING_RAISED

        if failure_reason == TestResultDescription.NULL:
            try:
                result = condition.callable(datum)
            except AttributeError:
                if raise_on_error:
                    raise
                failure_reason = TestResultDescription.CALLABLE_RAISED

            if not isinstance(result, bool):
                raise InvalidCallable(
                    f"Callable {condition.callable} did not return a boolean."
                )
            elif not result:
                failure_reason = TestResultDescription.CALLABLE_FALSE

        self.condition = condition
        self.datum = datum
        self.raise_on_error = raise_on_error
        self._result = result
        self.failure_reason = {failure_reason: condition}

    def __repr__(self):
        return f"{self.__class__.__name__}(result={self.result!r}, failure={self.failure_reason.name!r})"

    @property
    def result(self):
        return self._result


class ConditionTestBinary:
    def __init__(self, condition_tests):
        self.condition_tests = condition_tests
        self.failure_reason = [c.failure_reason for c in condition_tests]
        self.all_results = [c.result for c in self.condition_tests]


class ConditionTestAnd(ConditionTestBinary):
    def __init__(self, condition_tests):
        super().__init__(condition_tests)
        self._result = all(self.all_results)

    @property
    def result(self):
        return self._result


class ConditionTestOr(ConditionTestBinary):
    def __init__(self, condition_tests):
        super().__init__(condition_tests)
        self._result = any(self.all_results)

    @property
    def result(self):
        return self._result


class ConditionTestXor(ConditionTestBinary):
    def __init__(self, condition_tests):
        super().__init__(condition_tests)
        self._result = sum(self.all_results) == 1

    @property
    def result(self):
        return self._result

