from typing import Protocol, TypeVar, Iterable

from chide.typing import Attrs

T = TypeVar('T', contravariant=True)


class Simplifier(Protocol[T]):
    """
    Protocol for :doc:`simplifiers <simplifiers>`.
    """

    def one(self, obj: T) -> Attrs:
        """
        Simplify one object into its :class:`~chide.typing.Attrs`.
        """

    def many(self, objs: Iterable[T]) -> list[Attrs]:
        """
        Simplify many objects into a list of their :class:`~chide.typing.Attrs`.
        """
        return [self.one(obj) for obj in objs]


_MARKER = object()


class ObjectSimplifier(Simplifier[object]):
    """
    A simplifier that can extract attributes from :class:`object`-based
    classes that have either a ``__dict__`` or ``__slots__``.
    """

    def one(self, obj: object) -> Attrs:
        if isinstance(obj, dict):
            return dict(obj)

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

        if not (attrs or slots):
            raise TypeError(f"Can't simplify {type(obj)} {obj!r}")

        return attrs
