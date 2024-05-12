def _cat_compare_op(op):
    opname , fill_value  = f'__{op.__name__}__', True if op is operator.ne else False
    def func(self, other):
        if is_list_like(other) and len(other) != len(self):
            raise ValueError("Lengths must match.")
        if not self.ordered:
            if opname in ["__lt__", "__gt__", "__le__", "__ge__"]:
                raise TypeError(
                    "Unordered Categoricals can only compare equality or not"
                )
        if isinstance(other, Categorical):
            msg = "Categoricals can only be compared if 'categories' are the same."
            if len(self.categories) != len(other.categories):
                raise TypeError(msg + " Categories are different lengths")
            elif self.ordered and not (self.categories == other.categories).all():
                raise TypeError(msg)
            elif not set(self.categories) == set(other.categories):
                raise TypeError(msg)
            if not (self.ordered == other.ordered):
                raise TypeError(
                    "Categoricals can only be compared if 'ordered' is the same"
                )
            if not self.ordered and not self.categories.equals(other.categories):
                other_codes = _get_codes_for_values(other, self.categories)
            else:
                other_codes = other._codes
            ret , mask  = op(self._codes, other_codes), (self._codes == -1) | (other_codes == -1)
            if mask.any():
                ret[mask] = fill_value
            return ret
        if is_scalar(other):
            if other in self.categories:
                i = self.categories.get_loc(other)
                ret = op(self._codes, i)
                if opname not in {"__eq__", "__ge__", "__gt__"}:
                    mask = self._codes == -1
                    ret[mask] = fill_value
                return ret
            else:
                return ops.invalid_comparison(self, other, op)
        else:
            if opname not in ["__eq__", "__ne__"]:
                raise TypeError(
                    f"Cannot compare a Categorical for op {opname} with "
                    f"type {type(other)}.\nIf you want to compare values, "
                    "use 'np.asarray(cat) <op> other'."
                )
            if isinstance(other, ExtensionArray) and needs_i8_conversion(other.dtype):
                return op(other, self)
            return getattr(np.array(self), opname)(np.array(other))
    func.__name__ = opname
    return func
