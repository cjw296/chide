from dataclasses import dataclass

from testfixtures import compare

from .helpers import Comparable


class Sample(Comparable):
    def __init__(self) -> None:
        self.x = 1


def test_comparable_repr() -> None:
    compare(repr(Sample()), expected='<Sample: x=1>')
