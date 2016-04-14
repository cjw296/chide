from __future__ import absolute_import

from sqlalchemy import inspect

from .collection import Collection as BaseCollection


class Collection(BaseCollection):
    """
    A specialised :class:`chide.Collection` for make sample declaratively
    mapped objects when using SQLAlchemy.
    """

    @staticmethod
    def identify(type_, attrs):
        """
        This method returns the primary key that will be used for the
        returned object, meaning that only one sample object will exist
        and be returned for each primary key in a table.

        It's called internally, so you don't have to worry about it.
        """
        mapper = inspect(type_)
        key = []
        for prop in mapper._identity_key_props:
            value = attrs.get(prop.key)
            if value is None:
                return None
            key.append(value)
        return tuple(key)
