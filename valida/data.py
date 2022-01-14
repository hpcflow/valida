import enum
import operator


class TestResultDescription(enum.Enum):

    PRE_PROCESSING_ERROR = "Condition pre-processing raised an exception on invocation."
    CALLABLE_FALSE = "Condition callable returned `False`"
    CALLABLE_ERROR = "Condition callable raised an exception on invocation"
    BINARY_OP_FALSE = "Binary combination of two conditions callables returned `False`"
    BINARY_OP_ERROR = (
        "At least one of the child conditions raised an exception on invocation"
    )
    NULL = None


class Data:
    def __init__(self, data):

        if not isinstance(data, (list, dict)):
            raise TypeError(f'Data is not filterable: "{data!r}"')

        try:
            keys, values = zip(*data.items())
            is_list = False
        except AttributeError:
            keys, values = range(len(data)), data
            is_list = True

        # Generate child `Data` objects for nested lists/dicts:
        data_values = []
        for i in values:
            if isinstance(i, (list, dict)):
                data_values.append(Data(i))
            else:
                data_values.append(i)

        self._keys = keys
        self._values = data_values
        self._is_list = is_list

    def __len__(self):
        return len(self.keys())

    def __eq__(self, other):
        if not isinstance(other, Data):
            other = Data(other)
        if self.is_list != other.is_list:
            return False
        if self.keys() != other.keys():
            return False
        if self.values() != other.values():
            return False
        return True

    @property
    def is_list(self):
        return self._is_list

    def keys(self):
        return self._keys

    def values(self):
        return self._values

    def items(self):
        return iter(zip(self.keys(), self.values()))

    def filter(self, condition_like):
        return condition_like.filter(self)


class FilteredDataLike:
    def get_data(self):
        return [i for idx, i in enumerate(self.data.values()) if self.result[idx]]

    def __and__(self, other):
        return FilteredDataAnd(self, other)

    def __or__(self, other):
        return FilteredDataOr(self, other)

    def __xor__(self, other):
        return FilteredDataXor(self, other)


class FilteredData(FilteredDataLike):
    def __init__(self, condition, data, processed, result, failure):
        self.condition = condition
        self.data = data
        self.processed = processed
        self.result = result
        self.failure = failure

    @property
    def truth_table(self):
        return [
            (
                f"{self.condition.callable_name}({self.condition.callable_kwargs})",
                self.result,
            )
        ]


class FilteredDataBinaryOp(FilteredDataLike):
    def __init__(self, fd1, fd2, binary_op):

        if fd1.data is not fd2.data:
            raise RuntimeError(
                f"The two Data objects in a `{self.__class__.__name__}` must be identical."
            )

        self.data = fd1.data
        self.children = [fd1, fd2]
        self.result = [binary_op(i, j) for i, j in zip(fd1.result, fd2.result)]

        failure = []
        for idx in range(len(self.data)):
            if any(
                i.failure[idx]
                in (
                    TestResultDescription.PRE_PROCESSING_ERROR,
                    TestResultDescription.CALLABLE_ERROR,
                    TestResultDescription.BINARY_OP_ERROR,
                )
                for i in self.children
            ):
                failure_i = TestResultDescription.BINARY_OP_ERROR
            elif not self.result[idx]:
                failure_i = TestResultDescription.BINARY_OP_FALSE
            else:
                failure_i = TestResultDescription.NULL
            failure.append(failure_i)

        self.failure = failure

    @property
    def truth_table(self):
        return (
            self.children[0].truth_table
            + self.children[1].truth_table
            + [(self.TRUTH_TABLE_SYMBOL, self.result)]
        )


class FilteredDataAnd(FilteredDataBinaryOp):
    TRUTH_TABLE_SYMBOL = "and"

    def __init__(self, fd1, fd2):
        super().__init__(fd1, fd2, operator.and_)


class FilteredDataOr(FilteredDataBinaryOp):
    TRUTH_TABLE_SYMBOL = "or"

    def __init__(self, fd1, fd2):
        super().__init__(fd1, fd2, operator.or_)


class FilteredDataXor(FilteredDataBinaryOp):
    TRUTH_TABLE_SYMBOL = "xor"

    def __init__(self, fd1, fd2):
        super().__init__(fd1, fd2, operator.xor)
