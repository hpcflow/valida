from abc import ABC, abstractmethod
import operator


class FilteredData(ABC):
    def __init__(
        self,
        all_data,
        keep_bool,
        conditions,
        truth_table=None,
    ):

        self.all_data = all_data
        self.keep_bool = keep_bool
        self.conditions = conditions
        self.truth_table = truth_table or [self.get_truth_table_entry()]

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def get_one(self):
        pass

    @abstractmethod
    def _get_binary_op_keep_bool(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    def __and__(self, other):
        return self._get_binary_op_object(other, operator.and_)

    def __or__(self, other):
        return self._get_binary_op_object(other, operator.or_)

    def __xor__(self, other):
        return self._get_binary_op_object(other, operator.xor)

    def _get_binary_op_object(self, other, op_callable):

        if not isinstance(other, type(self)):
            raise TypeError(
                f"Cannot combine {self.__class__.__name__} "
                f"with object of type: {type(other)}"
            )
        if self.all_data is not other.all_data:
            raise ValueError(
                "Cannot combine `FilteredData` objects that filter different data"
            )

        keep_bool = self._get_binary_op_keep_bool(other, op_callable)

        conditions = self.conditions + other.conditions
        truth_table = self.truth_table + other.truth_table

        if len(other.conditions) > 1:
            conditions = other.conditions + self.conditions
            truth_table = other.truth_table + self.truth_table

        truth_table.append((op_callable.__name__.strip("_"), keep_bool))
        obj = self.__class__(self.all_data, keep_bool, conditions, truth_table)

        return obj

    def get_truth_table_entry(self):
        condition_str = (
            f"{self.conditions[0].callable_name}({self.conditions[0].callable_kwargs})"
        )
        return (condition_str, self.keep_bool)


class FilteredListData(FilteredData):
    """Class to represent a subset of data, filtered according to a Condition."""

    def __len__(self):
        return sum(self.keep_bool)

    def _get_binary_op_keep_bool(self, other, op_callable):
        return [op_callable(i, j) for i, j in zip(self.keep_bool, other.keep_bool)]

    def get_data(self):
        return [datum for idx, datum in enumerate(self.all_data) if self.keep_bool[idx]]

    def get_one(self):
        if len(self) == 1:
            return self.all_data[self.keep_bool.index(True)]
        else:
            raise ValueError("Not exactly one datum was filtered.")


class FilteredMapData(FilteredData):
    def __len__(self):
        return sum(self.keep_bool.values())

    def _get_binary_op_keep_bool(self, other, op_callable):
        return {
            k: (op_callable(v, other.keep_bool[k])) for k, v in self.keep_bool.items()
        }

    def get_data(self):
        return [val for key, val in self.all_data.items() if self.keep_bool[key]]

    def get_one(self):
        if len(self) == 1:
            return self.data[0]
        else:
            raise ValueError("Not exactly one datum was filtered.")
