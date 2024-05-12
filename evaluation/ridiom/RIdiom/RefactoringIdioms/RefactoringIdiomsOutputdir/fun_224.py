def _bool_method_SERIES(cls, op, special):
    op_name = _get_op_name(op, special)
    def na_op(x, y):
        try:
            result = op(x, y)
        except TypeError:
            assert not isinstance(y, (list, ABCSeries, ABCIndexClass))
            if isinstance(y, np.ndarray):
                assert not (is_bool_dtype(x.dtype) and is_bool_dtype(y.dtype))
                x , y  = ensure_object(x), ensure_object(y)
                result = libops.vec_binop(x, y, op)
            else:
                assert lib.is_scalar(y)
                if not isna(y):
                    y = bool(y)
                try:
                    result = libops.scalar_binop(x, y, op)
                except (
                    TypeError,
                    ValueError,
                    AttributeError,
                    OverflowError,
                    NotImplementedError,
                ):
                    raise TypeError(
                        "cannot compare a dtyped [{dtype}] array "
                        "with a scalar of type [{typ}]".format(
                            dtype=x.dtype, typ=type(y).__name__
                        )
                    )
        return result
    fill_int = lambda x: x
    def fill_bool(x, left=None):
        if x.dtype.kind in ["c", "f", "O"]:
            mask = isna(x)
            if mask.any():
                x = x.astype(object)
                x[mask] = False
        if left is None or is_bool_dtype(left.dtype):
            x = x.astype(bool)
        return x
    def wrapper(self, other):
        is_self_int_dtype = is_integer_dtype(self.dtype)
        self, other = _align_method_SERIES(self, other, align_asobject=True)
        res_name , finalizer  = get_op_result_name(self, other), lambda x: x.__finalize__(self) if not isinstance(other, (ABCSeries, ABCIndexClass)) else x
        if isinstance(other, ABCDataFrame):
            return NotImplemented
        other = lib.item_from_zerodim(other)
        if is_list_like(other) and not hasattr(other, "dtype"):
            other = construct_1d_object_array_from_listlike(other)
        lvalues , rvalues  = extract_array(self, extract_numpy=True), extract_array(other, extract_numpy=True)
        if should_extension_dispatch(self, rvalues):
            res_values = dispatch_to_extension_op(op, lvalues, rvalues)
        else:
            if isinstance(rvalues, (ABCSeries, ABCIndexClass, np.ndarray)):
                is_other_int_dtype = is_integer_dtype(rvalues.dtype)
                rvalues = rvalues if is_other_int_dtype else fill_bool(rvalues, lvalues)
            else:
                is_other_int_dtype = lib.is_integer(rvalues)
            filler , res_values  = fill_int if is_self_int_dtype and is_other_int_dtype else fill_bool, na_op(lvalues, rvalues)
            res_values = filler(res_values)
        result = self._constructor(res_values, index=self.index, name=res_name)
        return finalizer(result)
    wrapper.__name__ = op_name
    return wrapper
