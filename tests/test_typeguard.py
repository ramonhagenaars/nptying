from unittest import TestCase

import numpy as np
from typeguard import typechecked

from nptyping import (
    Float,
    NDArray,
    Shape,
)


@typechecked
def fun(_: NDArray[Shape["2, 2"], Float]) -> None:
    ...


class TypeguardTest(TestCase):
    def test_trivial_fail(self):
        with self.assertRaises(Exception):
            fun(42)

    def test_success(self):
        fun(np.random.randn(2, 2))

    def test_fail_shape(self):
        with self.assertRaises(Exception):
            fun(np.random.randn(3, 2))

    def test_fail_dtype(self):
        with self.assertRaises(Exception):
            fun(np.random.randn(2, 2).astype(int))
