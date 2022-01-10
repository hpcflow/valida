from valida.conditions import ConditionLike, NullCondition, Index, Value, Key


class DataPath:
    """Class to represent a path within a nested data structure.

    A DataPath locates nodes within a nested data structure. It comprises an
    address of nested data types (mapping values or list items) that can be further
    refined using one ore more conditions. Validation rules are applied (i.e. tested) at
    the nodes identified by a ContainerPath.

    """

    def __init__(self, *parts):
        self.parts = list(parts)
        for part_idx, part in enumerate(self.parts):
            if part is MapValue:
                self.parts[part_idx] = MapValue()
            elif part is ListValue:
                self.parts[part_idx] = ListValue()
        self.parts = tuple(self.parts)

    def __truediv__(self, other):
        """Concatenating with other DictValue, ListItem, AmbiguousItem or ContainerPaths."""
        if isinstance(other, (MapValue, ListValue)) or other in (
            MapValue,
            ListValue,
        ):
            return DataPath(*self.parts, other)
        elif isinstance(other, DataPath):
            return DataPath(*self.parts, *other.parts)

    def __rtruediv__(self, other):
        return self.__class__(other) / self

    def __iter__(self):
        for i in self.parts:
            yield i

    def __len__(self):
        return len(self.parts)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.parts[index]
        elif isinstance(index, slice):
            return self.__class__(*self.parts[index])

    def __repr__(self):
        return f'{self.__class__.__name__}({", ".join(f"{i!r}" for i in self.parts)})'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if len(self) == len(other):
                for i, j in zip(self.parts, other.parts):
                    if i != j:
                        return False
                return True
        return False

    def __hash__(self):
        return hash((i for i in self.parts))

    def get_data(self, data):
        """Get the data specified by this path."""

        data = [data]
        for part in self.parts:
            new_data = []
            for datum in data:
                filtered = part.filter(datum).get_data()
                new_data.extend(filtered)
            data = new_data

        return data


class ContainerItem:
    """Class for representing a container item (i.e. an item within either a list or a
    mapping). A container item can be filtered according to both its relationship to its
    parent container (i.e. position within the list for a list item, or key for a mapping
    item) and its value.

    """

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f'{f"({self.condition!r})" if not isinstance(self.condition, NullCondition) else ""}'
        )

    def __eq__(self, other):
        if (
            type(self) == type(other)
            and self.condition == other.condition
            and self.label == other.label
        ):
            return True
        return False

    def __truediv__(self, other):
        """Concatenating with other DictValue, ListValue or DataPath objects."""
        return DataPath(self, other)

    def __rtruediv__(self, other):
        return DataPath(other) / self

    def filter(self, data):
        return self.condition.filter(data)


class MapValue(ContainerItem):
    def __init__(self, key=None, value=None, condition=None, label=None):

        if condition is not None:
            if not isinstance(condition, ConditionLike):
                raise TypeError(
                    "If specified, `condition` must be a ConditionLike object."
                )
        else:
            condition = NullCondition()

        if key is not None:
            if not isinstance(key, ConditionLike):
                key = Key.equal_to(key)
            else:
                key = key.to_key_like()
            condition = condition & key

        if value is not None:
            if not isinstance(value, ConditionLike):
                value = Value.equal_to(value)
            condition = condition & value

        self.condition = condition
        self.label = label


class ListValue(ContainerItem):
    def __init__(self, index=None, value=None, condition=None, label=None):

        if condition is not None:
            if not isinstance(condition, ConditionLike):
                raise TypeError(
                    "If specified, `condition` must be a ConditionLike object."
                )
        else:
            condition = NullCondition()

        if index is not None:
            if not isinstance(index, ConditionLike):
                index = Index.equal_to(index)
            else:
                index = index.to_index_like()
            condition = condition & index

        if value is not None:
            if not isinstance(value, ConditionLike):
                value = Value.equal_to(value)
            condition = condition & value

        self.condition = condition
        self.label = label
