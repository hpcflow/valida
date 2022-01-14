from functools import partial
import enum
import operator


from valida import callables as call_funcs
from valida.data import Data, TestResultDescription, FilteredData
from valida.errors import InvalidCallable
from valida.utils import classproperty, null_condition_binary_check


class GeneralCallables:
    @classmethod
    def equal_to(cls, value):
        return cls(call_funcs.equal_to, value=value)

    @classmethod
    def not_equal_to(cls, value):
        return cls(call_funcs.not_equal_to, value=value)

    @classmethod
    def less_than(cls, value):
        return cls(call_funcs.less_than, value=value)

    @classmethod
    def greater_than(cls, value):
        return cls(call_funcs.greater_than, value=value)

    @classmethod
    def less_than_or_equal_to(cls, value):
        return cls(call_funcs.less_than_or_equal_to, value=value)

    @classmethod
    def greater_than_or_equal_to(cls, value):
        return cls(call_funcs.greater_than_or_equal_to, value=value)

    @classmethod
    def in_(cls, value):
        return cls(call_funcs.in_, value=value)

    @classmethod
    def not_in(cls, value):
        return cls(call_funcs.not_in, value=value)

    @classmethod
    def in_range(cls, value):
        return cls(call_funcs.in_range, value=value)

    @classmethod
    def not_in_range(cls, value):
        return cls(call_funcs.not_in_range, value=value)

    @classmethod
    def equal_to_approx(cls, value, tolerance=1e-8):
        return cls(call_funcs.equal_to_approx, value=value, tolerance=tolerance)

    @classmethod
    def truthy(cls):
        return cls(call_funcs.truthy)

    @classmethod
    def falsy(cls):
        return cls(call_funcs.falsy)

    @classmethod
    def null(cls):
        return cls(call_funcs.null)

    # Aliases for convenience:
    eq = equal_to
    lt = less_than
    gt = greater_than
    lte = less_than_or_equal_to
    gte = greater_than_or_equal_to

    OP_SYMBOL_MAP = {
        "==": equal_to,
        "<": less_than,
        ">": greater_than,
        "<=": less_than_or_equal_to,
        ">=": greater_than_or_equal_to,
    }


class MapCallables:
    @classmethod
    def keys_contain(cls, key):
        return cls(call_funcs.keys_contain, key=key)

    @classmethod
    def keys_contain_any_of(cls, *keys):
        return cls(call_funcs.keys_contain_any_of, keys=keys)

    @classmethod
    def keys_contain_all_of(cls, *keys):
        return cls(call_funcs.keys_contain_all_of, keys=keys)

    @classmethod
    def keys_contain_N_of(cls, N, keys):
        return cls(call_funcs.keys_contain_N_of, N=N, keys=keys)

    @classmethod
    def keys_contain_at_least_N_of(cls, N, keys):
        return cls(call_funcs.keys_contain_at_least_N_of, N=N, keys=keys)

    @classmethod
    def keys_contain_at_most_N_of(cls, N, keys):
        return cls(call_funcs.keys_contain_at_most_N_of, N=N, keys=keys)

    @classmethod
    def keys_contain_one_of(cls, keys):
        return cls(call_funcs.keys_contain_one_of, keys=keys)

    @classmethod
    def keys_contain_at_least_one_of(cls, keys):
        return cls(call_funcs.keys_contain_at_least_one_of, keys=keys)

    @classmethod
    def keys_contain_at_most_one_of(cls, keys):
        return cls(call_funcs.keys_contain_at_most_one_of, keys=keys)

    @classmethod
    def keys_equal_to(cls, *keys):
        return cls(call_funcs.keys_equal_to, keys=keys)

    @classmethod
    def items_contain(cls, **items):
        return cls(call_funcs.items_contain, **items)


class AllCallables(GeneralCallables, MapCallables):
    pass


class ConditionLike:
    def __or__(self, other):
        return ConditionOr(self, other)

    def __and__(self, other):
        return ConditionAnd(self, other)

    def __xor__(self, other):
        return ConditionXor(self, other)

    @property
    def is_null(self):
        return isinstance(self, NullCondition)

    @property
    def is_key_like(self):
        return all(isinstance(i, Key) for i in self.flatten()[0])

    @property
    def is_index_like(self):
        return all(isinstance(i, Index) for i in self.flatten()[0])

    @property
    def is_value_like(self):
        return all(isinstance(i, Value) for i in self.flatten()[0])

    def filter(self, data):
        if not isinstance(data, Data):
            data = Data(data)
        return self._filter(data)

    def test(self, datum):
        return self.filter([datum]).result[0]

    def test_all(self, data):
        return all(self.filter(data).result)

    def flatten(self):
        """Get a flattened list of all conditions."""
        all_cnds = []
        all_ops = []

        try:
            for idx, cnd_i in enumerate(self.children):
                flatten_i = cnd_i.flatten()
                all_cnds.extend(flatten_i[0])
                all_ops.extend(flatten_i[1])
                if idx == 0:
                    all_ops.append(self.FLATTEN_SYMBOL)

        except AttributeError:
            all_cnds.append(self)

        return all_cnds, all_ops


class Condition(ConditionLike):

    PRE_PROCESSOR = None

    def __init__(self, callable, **callable_kwargs):

        self.callable = partial(callable, **(callable_kwargs or {}))

        try:
            callable_name = self.callable.func.__name__
        except AttributeError:
            callable_name = self.callable.__name__  # if no partial arguments applied

        self.callable_name = callable_name
        self.callable_kwargs = self.callable.keywords

    def __repr__(self):

        out = f"{self.__class__.__name__}.{self.callable_name}"
        args = [f"{k}={v!r}" for k, v in self.callable_kwargs.items()]
        out += "(" + ", ".join(args) + ")"

        return out

    def __eq__(self, other):
        if type(other) is type(self) and self._members() == other._members():
            return True
        return False

    def _members(self):
        """Return data used in __eq__"""
        return (self.callable.func, self.callable_name, self.callable_kwargs)

    def _filter(self, data):

        processed = []
        result = []
        failure = []

        for datum in getattr(data, self.DATUM_TYPE.value)():

            failure_i = TestResultDescription.NULL
            try:
                processed_i = self.PRE_PROCESSOR(datum) if self.PRE_PROCESSOR else datum
                is_valid_i = True
                failure_i = None
            except TypeError:
                processed_i = None
                is_valid_i = False
                failure_i = TestResultDescription.PRE_PROCESSING_ERROR

            if is_valid_i:

                try:
                    result_i = self.callable(processed_i)

                    if not isinstance(result_i, bool):
                        raise InvalidCallable(
                            f"Callable {self.callable} did not return a boolean."
                        )
                    if not result_i:
                        failure_i = TestResultDescription.CALLABLE_FALSE

                except (TypeError, AttributeError):
                    result_i = False
                    failure_i = TestResultDescription.CALLABLE_ERROR

            else:
                result_i = False

            processed.append(processed_i)
            result.append(result_i)
            failure.append(failure_i)

        return FilteredData(self, data, processed, result, failure)


class FilterDatumType(enum.Enum):

    KEYS = "keys"
    VALUES = "values"


class NullCondition(Condition):
    """Class to represent a null condition that all data satisfies."""

    DATUM_TYPE = FilterDatumType.VALUES

    def __init__(self, *args, **kwargs):
        super().__init__(call_funcs.null)

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class ConditionBinaryOp(ConditionLike):
    def __new__(cls, *conditions):
        """If one of the conditions is a NullCondition, then abort object construction,
        and just return the non-null condition."""
        return null_condition_binary_check(*conditions) or super().__new__(cls)

    def __init__(self, *conditions):

        super().__init__()

        self.children = conditions

        # Nonsensical to combine key-like and index-like conditions:
        flattened_conds = self.flatten()[0]
        num_key_likes = sum(isinstance(i, KeyLike) for i in flattened_conds)
        num_index_likes = sum(isinstance(i, IndexLike) for i in flattened_conds)
        if num_key_likes > 0 and num_index_likes > 0:
            raise TypeError("Cannot combine `Key` and `Index` conditions.")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.children[0]}, {self.children[1]})"

    def __eq__(self, other):
        if type(self) is type(other) and (
            (
                self.children[0] == other.children[0]
                and self.children[1] == other.children[1]
            )
            or (
                self.children[0] == other.children[1]
                and self.children[1] == other.children[0]
            )
        ):
            return True
        return False

    def _filter(self, data, binary_op):
        return binary_op(*(i._filter(data) for i in self.children))


class ConditionAnd(ConditionBinaryOp):
    FLATTEN_SYMBOL = "and"

    def _filter(self, data):
        return super()._filter(data, operator.and_)


class ConditionOr(ConditionBinaryOp):
    FLATTEN_SYMBOL = "or"

    def _filter(self, data):
        return super()._filter(data, operator.or_)


class ConditionXor(ConditionBinaryOp):
    FLATTEN_SYMBOL = "xor"

    def _filter(self, data):
        return super()._filter(data, operator.xor)


class LengthPreProcessor:
    PRE_PROCESSOR = len


class DataTypePreProcessor:
    PRE_PROCESSOR = type


class ValueLike(Condition):
    DATUM_TYPE = FilterDatumType.VALUES


class KeyLike(Condition):
    DATUM_TYPE = FilterDatumType.KEYS

    def filter(self, data):

        if (isinstance(data, Data) and data.is_list) or not isinstance(
            data, (Data, dict)
        ):
            raise TypeError("`Key` condition can only filter a mapping (i.e. a dict).")

        return super().filter(data)

    def test(self, datum):
        """For testing a single-item mapping."""
        if len(datum) != 1:
            raise TypeError("Test can only be used to test a single-item mapping.")
        return self.filter(datum).result[0]


class IndexLike(Condition):
    DATUM_TYPE = FilterDatumType.KEYS

    def filter(self, data):

        if (isinstance(data, Data) and not data.is_list) or not isinstance(
            data, (Data, list)
        ):
            raise TypeError("`Index` condition can only filter a list.")
        return super().filter(data)

    def test(self, datum):
        """Not allowed, since the index of a list item is unknown to the item itself."""
        raise NotImplementedError


class Value(ValueLike, AllCallables):
    @classproperty
    def length(cls):
        return ValueLength

    @classproperty
    def dtype(cls):
        return ValueDataType


class ValueLength(LengthPreProcessor, ValueLike, GeneralCallables):
    pass


class ValueDataType(DataTypePreProcessor, ValueLike, GeneralCallables):
    pass


class Key(KeyLike, AllCallables):
    @classproperty
    def length(cls):
        return KeyLength

    @classproperty
    def dtype(cls):
        return KeyDataType


class KeyLength(LengthPreProcessor, KeyLike, GeneralCallables):
    pass


class KeyDataType(DataTypePreProcessor, KeyLike, GeneralCallables):
    pass


class Index(IndexLike, GeneralCallables):
    pass
