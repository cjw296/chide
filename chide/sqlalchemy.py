from typing import Any, Type

from sqlalchemy import inspect, Row
from sqlalchemy.orm import DeclarativeBase

from .simplifiers import Simplifier, T, ObjectSimplifier
from .set import Set as BaseSet
from .typing import Attrs


class Set(BaseSet):
    """
    A specialised :class:`chide.Set` for getting sample declaratively
    mapped objects when using SQLAlchemy.
    """

    @staticmethod
    def identify(type_: Type[Any], attrs: Attrs) -> tuple[Any, ...] | None:
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


class RowSimplifier(Simplifier[Row[Any]]):

    def one(self, row: Row[Any]) -> Attrs:
        return row._asdict()


class MappedSimplifier(Simplifier[DeclarativeBase]):

    def __init__(self) -> None:
        self._obj_simplifier = ObjectSimplifier()

    def one(self, obj: DeclarativeBase) -> Attrs:
        attrs = self._obj_simplifier.one(obj)
        attrs.pop('_sa_instance_state')
        return attrs
