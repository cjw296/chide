from unittest import TestCase

from testfixtures import compare, ShouldRaise

from chide import Collection, Set


class TestSet(TestCase):

    def setUp(self):
        self.collection = Collection({dict: {}})

    def test_no_identify(self):
        with ShouldRaise(TypeError('No identify callable supplied')):
            Set(self.collection)

    def test_identity_suppled(self):
        def identify(type_, attrs):
            return attrs['x']
        samples = Set(self.collection, identify)
        obj1 = samples.get(dict, x=1)
        obj2 = samples.get(dict, x=1)
        self.assertTrue(obj1 is obj2)

    def test_identity_subclass(self):
        class MySet(Set):
            def identify(self, type_, attrs):
                return attrs['x']
        samples = MySet(self.collection)
        obj1 = samples.get(dict, x=1)
        obj2 = samples.get(dict, x=1)
        self.assertTrue(obj1 is obj2)

    def test_identity_supplied_trumps_subclass(self):
        class MySet(Set):
            def identify(type_, attrs):
                return attrs['x']
        def identify(type_, attrs):
            return attrs['y']
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

    def test_identify_returns_none(self):
        def identify(type_, attrs):
            key = attrs['x']
            if not key:
                return None
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
