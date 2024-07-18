from typing import Protocol, TypeVar, Iterable

from chide.typing import Attrs

T = TypeVar('T', contravariant=True)


class Simplifier(Protocol[T]):

    def one(self, obj: T) -> Attrs:
        ...

    def many(self, objs: Iterable[T]) -> list[Attrs]:
        return [self.one(obj) for obj in objs]


_MARKER = object()


class ObjectSimplifier(Simplifier[object]):

    def one(self, obj: object) -> Attrs:
        attrs = {}
        slots = set()
        for class_ in type(obj).__mro__:
            class_slots = getattr(class_, '__slots__', None)
            if class_slots is not None:
                slots.update(class_slots)
        for attr in sorted(slots):
            value = getattr(obj, attr, _MARKER)
            if value is not _MARKER:
                attrs[attr] = value
        try:
            attrs.update(vars(obj))
        except TypeError:
            pass
        return attrs
