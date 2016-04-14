from __future__ import absolute_import

from sqlalchemy import inspect

from .collection import Collection as BaseCollection


class Collection(BaseCollection):

    @staticmethod
    def identify(type_, attrs):
        mapper = inspect(type_)
        key = []
        for prop in mapper._identity_key_props:
            value = attrs.get(prop.key)
            if value is None:
                return None
            key.append(value)
        return tuple(key)
