from typing import TypeVar, Generic, Any, Self, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .collection import Collection

T = TypeVar("T")


class Factory(Generic[T]):
    def __init__(self, collection: 'Collection', type_: Type[T], attrs: dict[str, Any]) -> None:
        self.collection = collection
        self.type_ = type_
        self.attrs = attrs

    def make(self, **attrs: Any) -> T:
        """
        Make a sample object of the specified ``type_`` using the default
        attributes for that type in this :class:`Collection`.

        The ``attrs`` mapping will be overlaid onto the sample attributes
        before being used with ``type_`` to instantiate and return a new
        sample object.
        """
        attrs_ = self.attrs.copy()
        attrs_.update(attrs)
        return self.collection.make(self.type_, **attrs_)

    def bind(self, **attrs: Any) -> Self:
        attrs_ = self.attrs.copy()
        attrs_.update(attrs)
        return type(self)(self.collection, self.type_, attrs_)
