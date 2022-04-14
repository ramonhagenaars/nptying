"""
MIT License

Copyright (c) 2022 Ramon Hagenaars

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from abc import ABC
from typing import Any, Tuple

import numpy as np

from nptyping.error import InvalidArgumentsError
from nptyping.nptyping_type import NPTypingType
from nptyping.shape import Shape
from nptyping.shape_expression import check_shape
from nptyping.subscriptable_meta import SubscriptableMeta
from nptyping.typing_ import (
    DType,
    name_per_dtype,
    validate_dtype,
)


class NDArrayMeta(SubscriptableMeta, cls_name="NDArray"):
    """
    Metaclass that is coupled to nptyping.NDArray. It contains all actual logic
    such as instance checking.
    """

    __args__: Tuple[Shape, DType]
    _parameterized: bool

    def _get_item(cls, item: Any) -> Tuple[Any, ...]:
        if not isinstance(item, tuple):
            raise InvalidArgumentsError(f"Unexpected argument of type {type(item)}.")
        shape, dtype = _get_from_tuple(item)
        validate_dtype(dtype)
        return shape, dtype

    def __instancecheck__(  # pylint: disable=bad-mcs-method-argument
        self, instance: Any
    ) -> bool:
        shape, dtype = self.__args__
        return (
            isinstance(instance, np.ndarray)
            and (shape is Any or check_shape(instance.shape, shape))
            and (dtype is Any or issubclass(instance.dtype.type, dtype))
        )

    def __str__(cls) -> str:
        shape, dtype = cls.__args__
        return (
            f"{cls.__name__}[{_shape_expression_to_str(shape)}, "
            f"{_dtype_to_str(dtype)}]"
        )

    def __repr__(cls) -> str:
        return str(cls)


def _is_literal_like(item: Any) -> bool:
    # item is a Literal or "Literal enough" (ducktyping).
    return hasattr(item, "__args__")


def _get_from_tuple(item: Tuple[Any, ...]) -> Tuple[Shape, DType]:
    # Return the Shape Expression and DType from a tuple.
    if len(item) > 2:
        raise InvalidArgumentsError(f"Unexpected argument '{item[2]}'.")

    dtype = item[1]
    if item[0] is Any or item[0] is Shape:
        shape = Any
    elif issubclass(item[0], Shape):
        shape = item[0]
    elif _is_literal_like(item[0]):
        shape_expression = item[0].__args__[0]
        shape = Shape[shape_expression]
    else:
        raise InvalidArgumentsError(
            f"Unexpected argument '{item[0]}', expecting"
            f" Shape[<ShapeExpression>] or"
            f" Literal[<ShapeExpression>]."
        )

    return shape, dtype


def _dtype_to_str(dtype: Any) -> str:
    if dtype is Any:
        return "Any"
    return name_per_dtype[dtype]


def _shape_expression_to_str(shape_expression: Any) -> str:
    return "Any" if shape_expression is Any else str(shape_expression)


class NDArray(NPTypingType, ABC, metaclass=NDArrayMeta):
    """
    An nptyping equivalent of numpy ndarray.

    ## No arguments means an NDArray with any DType and any shape.
    >>> NDArray
    NDArray[Any, Any]

    ## You can provide a DType and a Shape Expression.
    >>> from nptyping import Int32, Shape
    >>> NDArray[Shape["2, 2"], Int32]
    NDArray[Shape['2, 2'], Int]

    ## Instance checking can be done and the shape is also checked.
    >>> import numpy as np
    >>> isinstance(np.array([[1, 2], [3, 4]]), NDArray[Shape['2, 2'], Int32])
    True
    >>> isinstance(np.array([[1, 2], [3, 4], [5, 6]]), NDArray[Shape['2, 2'], Int32])
    False

    """

    __args__ = (Any, Any)
