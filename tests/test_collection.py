from testfixtures import compare, ShouldRaise
from unittest import TestCase

from chide import Collection, Set
from .helpers import Comparable


class TypeA(Comparable, object):

    def __init__(self, x, y):
        self.x, self.y = x, y


class TypeB(Comparable):

    def __init__(self, a, b):
        self.a, self.b = a, b


def make_type_c():

    class TypeC(Comparable, object):
        seen = set()
        def __init__(self, key):
            if key in self.seen:
                raise Exception(key)
            self.seen.add(key)
            self.key = key

    return TypeC


class TestCollection(TestCase):

    def test_basic(self):
        samples = Collection({TypeA: {'x': 1, 'y': 2}})
        compare(TypeA(1, 2), actual=samples.make(TypeA))

    def test_override(self):
        samples = Collection({TypeA: {'x': 1, 'y': 2}})
        compare(TypeA(1, 3), actual=samples.make(TypeA, y=3))
        # check we don't mutate the sample data!
        compare(samples.make(TypeA), expected=TypeA(1, 2))

    def test_nested(self):
        samples = Collection({
            TypeA: {'x': 1, 'y': TypeB},
            TypeB: {'a': 3, 'b': 4},
        })
        compare(TypeA(1, TypeB(3, 4)), actual=samples.make(TypeA))

    def test_nested_leave_explicit_types(self):
        samples = Collection({TypeA: {'x': 1}, TypeB: {}})
        compare(TypeA(1, TypeB), actual=samples.make(TypeA, y=TypeB))

    def test_no_identity_okay(self):
        samples = Collection({TypeA: {'x': 1, 'y': 2}})
        sample1 = samples.make(TypeA)
        sample2 = samples.make(TypeA)
        compare(TypeA(1, 2), actual=sample1)
        compare(TypeA(1, 2), actual=sample2)
        self.assertFalse(sample1 is sample2)

    def test_no_identity_bad(self):
        TypeC = make_type_c()
        samples = Collection({TypeC: {'key': 1}})
        samples.make(TypeC)
        with ShouldRaise(Exception(1)):
            samples.make(TypeC)

    def test_identify_and_set(self):

        TypeC = make_type_c()

        def identify_type_c(type_, attrs):
            self.assertTrue(TypeC is type_)
            return attrs['key']

        samples = Collection({TypeC: {'key': 1}})
        set = Set(samples, identify_type_c)
        sample1 = set.get(TypeC)
        sample2 = set.get(TypeC)
        self.assertTrue(type(sample1), TypeC)
        compare(sample1.key, expected=1)
        self.assertTrue(sample1 is sample2)

