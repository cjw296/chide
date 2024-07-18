from typing import TypeVar, Generic, Any, Self, Type, TYPE_CHECKING, Callable

from .typing import Attrs

if TYPE_CHECKING:
    from .collection import Collection

T = TypeVar("T")


class Factory(Generic[T]):
    """
    A factory for objects of a particular type.
    These are created by either :meth:`chide.Collection.bind` or :meth:`chide.factory.Factory.bind`.
    """
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
        Make the attributes for a sample object of this factory's type
        using the default attributes for the type in this factory's :class:`Collection`
        overlaid with any attributes bound into the factory.

        The ``attrs`` mapping will be overlaid onto those attributes
        and returned as a :class:`dict`.
        """
        return self.collection.attributes(self.type_, **self._combine(attrs))

    def make(self, **attrs: Any) -> T:
        """
        Make a sample object of this factory's type using the default
        attributes for the type in this factory's :class:`Collection`
        overlaid with any attributes bound into the factory.

        The ``attrs`` mapping will be overlaid onto the sample attributes
        before being used to instantiate and return a new
        sample object of this factory's type.
        """
        return self.collection.make(self.type_, **self._combine(attrs))

    def bind(self, **attrs: Any) -> Self:
        """
        Bind the supplied attributes into a new :class:`~chide.factory.Factory`
        by overlaying them onto the sample attributes this factory would use.
        """
        return type(self)(self.collection, self.type_, self._combine(attrs))
