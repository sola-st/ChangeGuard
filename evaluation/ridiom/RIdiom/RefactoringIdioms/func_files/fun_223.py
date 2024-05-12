def _comp_method_SERIES(cls, op, special):
    op_name = _get_op_name(op, special)
    def wrapper(self, other):
        res_name = get_op_result_name(self, other)
        finalizer = (
            lambda x: x.__finalize__(self)
            if isinstance(other, (np.ndarray, ABCIndexClass))
            else x
        )
        if isinstance(other, ABCDataFrame):  
            return NotImplemented
        if isinstance(other, ABCSeries) and not self._indexed_same(other):
            raise ValueError("Can only compare identically-labeled Series objects")
        other = lib.item_from_zerodim(other)
        if isinstance(other, list):
            other = np.asarray(other)
        if isinstance(other, (np.ndarray, ABCExtensionArray, ABCIndexClass)):
            if len(self) != len(other):
                raise ValueError("Lengths must match to compare")
        lvalues = extract_array(self, extract_numpy=True)
        rvalues = extract_array(other, extract_numpy=True)
        if should_extension_dispatch(lvalues, rvalues):
            res_values = dispatch_to_extension_op(op, lvalues, rvalues)
        elif is_scalar(rvalues) and isna(rvalues):
            if op is operator.ne:
                res_values = np.ones(len(lvalues), dtype=bool)
            else:
                res_values = np.zeros(len(lvalues), dtype=bool)
        elif is_object_dtype(lvalues.dtype):
            res_values = comp_method_OBJECT_ARRAY(op, lvalues, rvalues)
        else:
            op_name = "__{op}__".format(op=op.__name__)
            method = getattr(lvalues, op_name)
            with np.errstate(all="ignore"):
                res_values = method(rvalues)
            if res_values is NotImplemented:
                res_values = invalid_comparison(lvalues, rvalues, op)
            if is_scalar(res_values):
                raise TypeError(
                    "Could not compare {typ} type with Series".format(typ=type(rvalues))
                )
        result = self._constructor(res_values, index=self.index)
        result = finalizer(result)
        result.name = res_name
        return result
    wrapper.__name__ = op_name
    return wrapper
