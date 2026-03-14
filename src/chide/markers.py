from typing import TypeVar, Callable, Generic

__all__ = ['nest', 'call']

T = TypeVar('T')


class Nested(Generic[T]):
    """Marker produced by :func:`nest`. Resolved to a sample object at make-time."""

    def __init__(self, type_: type[T]) -> None:
        self.type_ = type_


class Dynamic(Generic[T]):
    """Marker produced by :func:`call`. Invoked fresh on each make-time."""

    def __init__(self, factory: Callable[[], T]) -> None:
        self.factory = factory


def nest(type_: type[T]) -> T:
    """
    Mark a registered type so that it is resolved to a sample object when an
    enclosing sample is made via :meth:`~chide.Collection.make`.

    :param type_: The type to resolve via the collection at make-time.
    :returns: A marker object typed as ``T`` so that mypy accepts it at call sites.
    """
    return Nested(type_)  # type: ignore[return-value]


def call(factory: Callable[[], T]) -> T:
    """
    Mark a zero-argument callable so that it is invoked fresh each time a sample
    object is made via :meth:`~chide.Collection.make`.

    :param factory: A zero-argument callable returning ``T``.
    :returns: A marker object typed as ``T`` so that mypy accepts it at call sites.
    """
    return Dynamic(factory)  # type: ignore[return-value]
