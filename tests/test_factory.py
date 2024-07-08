from dataclasses import dataclass

from testfixtures import compare

from chide import Collection


@dataclass
class SampleClass:
    x: int
    y: int
    z: int


def test_simple() -> None:
    collection = Collection({SampleClass: {'x': 1}})
    factory = collection.bind(SampleClass, y=2)
    actual = factory.make(z=3)
    compare(actual, expected=SampleClass(x=1, y=2, z=3))


def test_rebind() -> None:
    collection = Collection({SampleClass: {'x': 1, 'y': 2, 'z': 3}})
    factory = collection.bind(SampleClass, x=4, y=5, z=6)
    rebound = factory.bind(x=7, y=8, z=9)
    compare(collection.make(SampleClass), expected=SampleClass(x=1, y=2, z=3))
    compare(factory.make(), expected=SampleClass(x=4, y=5, z=6))
    compare(rebound.make(), expected=SampleClass(x=7, y=8, z=9))


def test_attributes() -> None:
    collection = Collection({SampleClass: {'x': 1}})
    factory = collection.bind(SampleClass, y=2)
    actual = factory.attributes(z=3)
    compare(actual, expected=dict(x=1, y=2, z=3))
