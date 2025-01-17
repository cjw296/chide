from dataclasses import dataclass

from testfixtures import compare, ShouldRaise

from chide.simplifiers import ObjectSimplifier


class TestObjectSimplifier:

    def test_simple(self) -> None:

        class MyClass:
            def __init__(self, value: int):
                self.value = value

        simplifier = ObjectSimplifier()

        obj = MyClass(value=1)
        actual = simplifier.one(obj)
        assert actual is not obj.__dict__
        compare(actual, expected={'value': 1})
        compare(
            simplifier.many([MyClass(value=1), MyClass(value=2)]),
            expected=[{'value': 1}, {'value': 2}],
        )

    def test_dataclass(self) -> None:

        @dataclass
        class MyClass:
            value: int

        simplifier = ObjectSimplifier()
        compare(
            simplifier.many([MyClass(value=1), MyClass(value=2)]),
            expected=[{'value': 1}, {'value': 2}],
        )

    def test_slots_and_dict(self) -> None:
        class Base:
            __slots__ = ['x']
            x: int

        class SubClass(Base):
            __slots__ = ['y']
            y: int

        class ActualClass(SubClass):
            def __init__(self, z: int):
                self.z = z

        simplifier = ObjectSimplifier()

        # Check some assumptions about how slots work:
        compare(SubClass.__slots__, expected=['y'])
        sub_instance = SubClass()
        sub_instance.x = 1
        sub_instance.y = 2
        with ShouldRaise(AttributeError):
            sub_instance.z = 3  # type: ignore
        assert not hasattr(sub_instance, '__dict__')

        # check "pure slots":
        compare(simplifier.one(sub_instance), expected={'x': 1, 'y': 2})

        # check the mess you can get with slots:
        actual_instance = ActualClass(3)
        actual_instance.x = 1
        actual_instance.y = 2
        compare(simplifier.one(actual_instance), expected={'x': 1, 'y': 2, 'z': 3})

    def test_slots_unset_or_none(self) -> None:

        class SampleClass:
            __slots__ = ['x']
            x: int | None

        obj1 = SampleClass()
        obj1.x = None
        obj2 = SampleClass()

        simplifier = ObjectSimplifier()

        compare(
            simplifier.many([obj1, obj2]), expected=[{'x': None}, {}],
        )

    def test_dict(self) -> None:
        simplifier = ObjectSimplifier()
        compare(simplifier.one({'x': 1}), expected={'x': 1}, strict=True)

    def test_dict_subclass(self) -> None:
        simplifier = ObjectSimplifier()

        class MyDict(dict[str, int]): pass

        compare(simplifier.one(MyDict(x=1)), expected={'x': 1}, strict=True)

    def test_int(self) -> None:
        simplifier = ObjectSimplifier()
        with ShouldRaise(TypeError("Can't simplify <class 'int'> 1")):
            simplifier.one(1)

    def test_list(self) -> None:
        simplifier = ObjectSimplifier()
        with ShouldRaise(TypeError("Can't simplify <class 'list'> [1]")):
            simplifier.one([1])
