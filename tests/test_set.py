from typing import Type, Any
from unittest import TestCase

from testfixtures import compare, ShouldRaise, ShouldAssert

from chide import Collection, Set
from chide.typing import Attrs


class TestSet(TestCase):

    def setUp(self) -> None:
        self.collection = Collection({dict: {}})

    def test_no_identify(self) -> None:
        with ShouldRaise(TypeError('No identify callable supplied')):
            Set(self.collection)

    def test_identity_supplied(self) -> None:
        def identify(type_: Type[Any], attrs: Attrs) -> int:
            key = attrs['x']
            assert isinstance(key, int)
            return key
        samples = Set(self.collection, identify)
        obj1 = samples.get(dict, x=1)
        obj2 = samples.get(dict, x=1)
        self.assertTrue(obj1 is obj2)

    def test_identity_subclass(self) -> None:
        class MySet(Set):
            def identify(self, type_: Type[Any], attrs: Attrs) -> int:
                key = attrs['x']
                assert isinstance(key, int)
                return key
        samples = MySet(self.collection)
        obj1 = samples.get(dict, x=1)
        obj2 = samples.get(dict, x=1)
        self.assertTrue(obj1 is obj2)

    def test_identity_supplied_trumps_subclass(self) -> None:

        class MySet(Set):
            def identify(self, type_: Type[Any], attrs: Attrs) -> int:
                raise AssertionError('should not be called')

        unusable = MySet(self.collection)
        with ShouldAssert('should not be called'):
            unusable.get(dict, x=1, y=1)

        def identify(type_: Type[Any], attrs: Attrs) -> int:
            key = attrs['y']
            assert isinstance(key, int)
            return key

        samples = MySet(self.collection, identify)
        obj1 = samples.get(dict, x=1, y=1)
        compare(obj1, expected={'x': 1, 'y': 1})
        obj2 = samples.get(dict, x=1, y=2)
        compare(obj2, expected={'x': 1, 'y': 2})
        obj3 = samples.get(dict, x=2, y=3)
        compare(obj3, expected={'x': 2, 'y': 3})
        obj4 = samples.get(dict, x=3, y=3)
        compare(obj4, expected={'x': 2, 'y': 3})
        self.assertTrue(obj3 is obj4)

    def test_identify_returns_none(self) -> None:
        def identify(type_: Type[Any], attrs: Attrs) -> int | None:
            key = attrs['x']
            if not key:
                return None
            assert isinstance(key, int)
            return key
        samples = Set(self.collection, identify)
        obj1 = samples.get(dict, x=1)
        compare(obj1, expected={'x': 1})
        obj2 = samples.get(dict, x=1)
        compare(obj2, expected={'x': 1})
        obj3 = samples.get(dict, x=None)
        compare(obj3, expected={'x': None})
        obj4 = samples.get(dict, x=None)
        compare(obj4, expected={'x': None})
        self.assertTrue(obj1 is obj2)
        self.assertFalse(obj3 is obj4)
