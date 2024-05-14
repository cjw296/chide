from typing import Type, Any, TypeVar, Callable

from .typing import Attrs

T = TypeVar('T')


class Collection:
    """
    A collection of attributes to use to make sample objects.

    :param mapping:
        A dictionary mapping object types to a dictionary
        of attributes to make a sample object of that type.

    """

    def __init__(self, mapping: dict[Type[Any], Attrs]) -> None:
        self.mapping = mapping

    def _attrs(
            self,
            type_: Type[Any],
            attrs: Attrs,
            nest: Callable[[Type[T]], T]
    ) -> Attrs:
        computed_attrs = dict(self.mapping[type_])
        for key, value in computed_attrs.items():
            try:
                value_in_mapping = value in self.mapping
            except TypeError:
                value_in_mapping = False
            if value_in_mapping and key not in attrs:
                computed_attrs[key] = nest(value)
        computed_attrs.update(attrs)
        return computed_attrs

    def attributes(self, type_: Type[T], **attrs: Any) -> Attrs:
        """
        Make a sample object of the specified ``type_`` using the default
        attributes for that type in this :class:`Collection`.

        The ``attrs`` mapping will be overlaid onto the sample attributes
        before being used with ``type_`` to instantiate and return a new
        sample object.
        """
        return self._attrs(type_, attrs, self.make)

    def make(self, type_: Type[T], **attrs: Any) -> T:
        """
        Make the attributes for a sample object of the specified ``type_``
        using the default attributes for that type in this :class:`Collection`.

        The ``attrs`` mapping will be overlayed onto the sample attributes
        and returned as a :class:`dict`.
        """
        return type_(**self.attributes(type_, **attrs))
