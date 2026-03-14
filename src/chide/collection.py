from typing import Type, Any, TypeVar, Callable, cast

from .factory import Factory
from .markers import Nested, Dynamic
from .simplifiers import ObjectSimplifier, Simplifier
from .typing import Attrs

T = TypeVar('T')


class Collection:
    """
    A collection of attributes to use to make sample objects.

    :param mapping:
        A dictionary mapping object types to a dictionary
        of attributes to make a sample object of that type.

    """

    def __init__(self, mapping: dict[Type[Any], Attrs] | None = None) -> None:
        self.mapping = mapping or {}
        self.constructors: dict[Type[Any], Type[Any]] = {}

    def _attrs(self, type_: Type[Any], attrs: Attrs, nest: Callable[[Type[T]], T]) -> Attrs:
        computed_attrs = dict(self.mapping[type_])
        for key, value in computed_attrs.items():
            if key in attrs:
                continue
            if isinstance(value, Nested):
                computed_attrs[key] = nest(value.type_)
            elif isinstance(value, Dynamic):
                computed_attrs[key] = value.factory()
        computed_attrs.update(attrs)
        return computed_attrs

    def add(
        self,
        obj: T,
        simplifier: Simplifier[T] = ObjectSimplifier(),
        annotated: Type[T] | None = None,
        constructor: Type[T] | None = None,
    ) -> None:
        """
        Add the attributes from the supplied object to this collection and
        use them when samples of the type of that object are required.

        :param obj: The sample object from which to extract attributes.

        :param simplifier:
          The :class:`~chide.simplifiers.Simplifier` to use to extract attributes
          from ``obj``.

        :param annotated:
          If ``obj`` is an instance of a simple type such as a :class:`dict`,
          it may be necessary to provided the annotated type for data instance
          such that it can be correctly added to the collection with that type.

        :param constructor:
          The class to use when constructing objects of this type. This is useful
          when the type is a parameterized generic but you want to construct using
          the origin class to avoid ``__orig_class__`` being set.
        """
        attrs = simplifier.one(obj)
        orig_class = attrs.pop("__orig_class__", None)
        key = annotated or orig_class or type(obj)
        self.mapping[key] = attrs
        if constructor is not None:
            self.constructors[key] = constructor

    def attributes(self, type_: Type[T], **attrs: Any) -> Attrs:
        """
        Make the attributes for a sample object of the specified ``type_``
        using the default attributes for that type in this :class:`Collection`.

        The ``attrs`` mapping will be overlaid onto the sample attributes
        and returned as a :class:`dict`.
        """
        return self._attrs(type_, attrs, self.make)

    def make(self, type_: Type[T], override: Type[T] | None = None, /, **attrs: Any) -> T:
        """
        Make a sample object of the specified ``type_`` using the default
        attributes for that type in this :class:`Collection`.

        The ``attrs`` mapping will be overlaid onto the sample attributes
        before being used with ``type_`` to instantiate and return a new
        sample object.

        If ``override`` is provided, it will be used to construct the object in place of the
        supplied type.
        """
        constructor = cast(Type[T], override or self.constructors.get(type_, type_))
        return constructor(**self.attributes(type_, **attrs))

    def bind(self, type_: Type[T], **attrs: Any) -> Factory[T]:
        """
        Bind the supplied attributes into a :class:`~chide.factory.Factory` for the
        requested ``type_`` by overlaying them onto the sample attributes
        for that ``type_`` in this :class:`Collection`.
        """
        return Factory[T](self, type_, attrs)
