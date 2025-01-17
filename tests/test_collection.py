from dataclasses import dataclass
from typing import Type, Annotated

from testfixtures import compare, ShouldRaise
from unittest import TestCase

from chide import Collection, Set
from chide.simplifiers import Simplifier
from chide.typing import Attrs
from .helpers import Comparable
from .test_helpers import Sample


class TypeA(Comparable, object):

    def __init__(self, x: int, y: 'int | TypeB | Type[TypeB]') -> None:
        self.x, self.y = x, y


class TypeB(Comparable):

    def __init__(self, a: int, b: int) -> None:
        self.a, self.b = a, b


class TypeC(Comparable, object):
    seen: set[int]

    def __init__(self, key: int) -> None:
        if key in self.seen:
            raise Exception(key)
        self.seen.add(key)
        self.key = key


def make_type_c() -> Type[TypeC]:

    class TypeC_(TypeC):
        seen = set()

    return TypeC_


class TestCollection(TestCase):

    def test_basic(self) -> None:
        samples = Collection({TypeA: {'x': 1, 'y': 2}})
        compare(TypeA(1, 2), actual=samples.make(TypeA))

    def test_override(self) -> None:
        samples = Collection({TypeA: {'x': 1, 'y': 2}})
        compare(TypeA(1, 3), actual=samples.make(TypeA, y=3))
        # check we don't mutate the sample data!
        compare(samples.make(TypeA), expected=TypeA(1, 2))

    def test_nested(self) -> None:
        samples = Collection({
            TypeA: {'x': 1, 'y': TypeB},
            TypeB: {'a': 3, 'b': 4},
        })
        compare(TypeA(1, TypeB(3, 4)), actual=samples.make(TypeA))

    def test_nested_leave_explicit_types(self) -> None:
        samples = Collection({TypeA: {'x': 1}, TypeB: {}})
        compare(TypeA(1, TypeB), actual=samples.make(TypeA, y=TypeB))

    def test_no_identity_okay(self) -> None:
        samples = Collection({TypeA: {'x': 1, 'y': 2}})
        sample1 = samples.make(TypeA)
        sample2 = samples.make(TypeA)
        compare(TypeA(1, 2), actual=sample1)
        compare(TypeA(1, 2), actual=sample2)
        self.assertFalse(sample1 is sample2)

    def test_no_identity_bad(self) -> None:
        TypeC = make_type_c()
        samples = Collection({TypeC: {'key': 1}})
        samples.make(TypeC)
        with ShouldRaise(Exception(1)):
            samples.make(TypeC)

    def test_identify_and_set(self) -> None:

        type_c = make_type_c()

        def identify_type_c(type_: Type[TypeC], attrs: Attrs) -> int:
            self.assertTrue(type_c is type_)
            key = attrs['key']
            assert isinstance(key, int)
            return key

        samples = Collection({type_c: {'key': 1}})
        set = Set(samples, identify_type_c)
        sample1 = set.get(type_c)
        sample2 = set.get(type_c)
        self.assertTrue(type(sample1), type_c)
        compare(sample1.key, expected=1)
        self.assertTrue(sample1 is sample2)

    def test_unhashable_attributes(self) -> None:
        unhashable: list[int] = []
        collection = Collection({dict: {'y': unhashable}})
        made = collection.make(dict)
        compare(made, expected={'y': []})
        assert made['y'] is unhashable

    def test_add_sample(self) -> None:

        @dataclass
        class Sample:
            x: int
            y: int

        sample = Sample(x=1, y=2)
        collection = Collection()
        collection.add(sample)

        compare(collection.attributes(Sample), expected={'x': 1, 'y': 2})
        assert collection.make(Sample) is not sample

    def test_with_explicit_simplifier(self) -> None:

        class Sample:
            pass

        class SampleSimplifier(Simplifier[Sample]):
            def one(self, obj: Sample) -> Attrs:
                return {'made': 'up'}

        collection = Collection()
        collection.add(Sample(), SampleSimplifier())

        compare(collection.attributes(Sample), expected={'made': 'up'})

    def test_annotated_data_to_constructor(self) -> None:

        SampleFooData = Annotated[dict, 'foo']
        SampleBarData = Annotated[dict, 'bar']

        collection = Collection({
            dict: {'type': 'dict'},
            SampleFooData: {'type': 'foo'},
            SampleBarData: {'type': 'bar'},
        })

        compare(collection.make(dict), strict=True, expected={'type': 'dict'})
        compare(collection.make(SampleFooData), strict=True, expected={'type': 'foo'})
        compare(collection.make(SampleBarData), strict=True, expected={'type': 'bar'})

    def test_annotated_data_to_add(self) -> None:

        SampleFooData = Annotated[dict, 'foo']
        SampleBarData = Annotated[dict, 'bar']

        collection = Collection()
        collection.add({'type': 'dict'})
        collection.add({'type': 'foo'}, annotated=SampleFooData)
        collection.add({'type': 'bar'}, annotated=SampleBarData)

        compare(collection.make(dict), strict=True, expected={'type': 'dict'})
        compare(collection.make(SampleFooData), strict=True, expected={'type': 'foo'})
        compare(collection.make(SampleBarData), strict=True, expected={'type': 'bar'})
