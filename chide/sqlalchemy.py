from __future__ import absolute_import

from sqlalchemy import inspect

from .set import Set as BaseSet


class Set(BaseSet):
    """
    A specialised :class:`chide.Set` for getting sample declaratively
    mapped objects when using SQLAlchemy.
    """

    @staticmethod
    def identify(type_, attrs):
        """
        This method returns the primary key that will be used for the
        returned object, meaning that only one sample object will exist
        and be returned for each primary key in a table.

        If any element of the primary key is ``None``, a new object
        is always returned.
        """
        mapper = inspect(type_)
        key = [type_]
        for prop in mapper._identity_key_props:
            value = attrs.get(prop.key)
            if value is None:
                # no primary key, so we always get a new object...
                return None
            key.append(value)
        return tuple(key)
