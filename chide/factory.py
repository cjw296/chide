from typing import TypeVar, Generic, Any, Self, Type, TYPE_CHECKING

from .typing import Attrs

if TYPE_CHECKING:
    from .collection import Collection

T = TypeVar("T")


class Factory(Generic[T]):
    def __init__(self, collection: 'Collection', type_: Type[T], attrs: dict[str, Any]) -> None:
        self.collection = collection
        self.type_ = type_
        self.attrs = attrs

    def _combine(self, attrs: Attrs) -> Attrs:
        attrs_ = self.attrs.copy()
        attrs_.update(attrs)
        return attrs_

    def attributes(self, **attrs: Any) -> Attrs:
        """
        Make the attributes for a sample object of the specified ``type_``
        using the default attributes for that type in this :class:`Collection`.

        The ``attrs`` mapping will be overlayed onto the sample attributes
        and returned as a :class:`dict`.
        """
        return self.collection.attributes(self.type_, **self._combine(attrs))

    def make(self, **attrs: Any) -> T:
        """
        Make a sample object of the specified ``type_`` using the default
        attributes for that type in this :class:`Collection`.

        The ``attrs`` mapping will be overlaid onto the sample attributes
        before being used with ``type_`` to instantiate and return a new
        sample object.
        """
        return self.collection.make(self.type_, **self._combine(attrs))

    def bind(self, **attrs: Any) -> Self:
        return type(self)(self.collection, self.type_, self._combine(attrs))
