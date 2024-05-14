from typing import Type
from unittest import TestCase

from sqlalchemy import Column, String, create_engine, ForeignKey
from sqlalchemy import Integer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    sessionmaker, relationship, DeclarativeBase, Session, Mapped, mapped_column
)
from testfixtures import compare, ShouldRaise

from chide import Collection
from chide.sqlalchemy import Set
from .helpers import Comparable


class Base(DeclarativeBase): pass


class Model(Comparable, Base):
    __tablename__ = 'model'
    id: Mapped[int] = mapped_column('id_', primary_key=True)
    value: Mapped[str]


class TestSQLAlchemyCollection(TestCase):

    def make_session(self, base: Type[DeclarativeBase]) -> Session:
        engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=engine)
        base.metadata.create_all(engine)
        return Session()

    def make_all(self) -> tuple[Type['Model'], Collection, Session]:

        samples = Collection({Model: {'id': 1, 'value': 'two'}})
        session = self.make_session(Base)

        return Model, samples, session

    def test_simple_model(self) -> None:
        Model, samples, session = self.make_all()

        model1 = samples.make(Model)
        model2 = samples.make(Model)
        self.assertFalse(model1 is model2)

        session.add(samples.make(Model))
        session.commit()

        model = session.query(Model).one()
        compare(Model(id=1, value='two'), actual=model)

    def test_simple_model_with_session(self) -> None:
        Model, samples_, session = self.make_all()

        samples = Set(samples_)
        model1 = samples.get(Model)
        model2 = samples.get(Model)
        self.assertTrue(model1 is model2)

        session.add(samples.get(Model))
        session.add(samples.get(Model))
        session.commit()

        model = session.query(Model).one()
        compare(Model(id=1, value='two'), actual=model)

    def test_foreign_key_no_session(self) -> None:

        class Base(DeclarativeBase): pass

        class Parent(Comparable, Base):
            __tablename__ = 'parent'
            id = Column(Integer, primary_key=True)
            child_id = Column(Integer, ForeignKey('child.id'))
            child = relationship('Child')

        class Child(Comparable, Base):
            __tablename__ = 'child'
            id = Column(Integer, primary_key=True)
            value = Column(String)

        samples = Collection({
            Parent: {'id': 1, 'child': Child},
            Child: {'id': 3, 'value': 'Foo'}
        })

        parent1 = samples.make(Parent, id=1)
        parent2 = samples.make(Parent, id=2)
        session = self.make_session(Base)
        session.add(parent1)
        session.add(parent2)
        with ShouldRaise(IntegrityError):
            session.commit()

    def test_foreign_key_with_session(self) -> None:

        class Base(DeclarativeBase): pass

        class Parent(Comparable, Base):
            __tablename__ = 'parent'
            id = Column(Integer, primary_key=True)
            child_id = Column(Integer, ForeignKey('child.id'))
            child = relationship('Child')

        class Child(Comparable, Base):
            __tablename__ = 'child'
            id = Column(Integer, primary_key=True)
            value = Column(String)

        collection = Collection({
            Parent: {'id': 1, 'child': Child},
            Child: {'id': 3, 'value': 'Foo'}
        })

        samples = Set(collection)
        parent1 = samples.get(Parent, id=1)
        parent2 = samples.get(Parent, id=2)
        self.assertFalse(parent1 is parent2)
        session = self.make_session(Base)
        session.add(parent1)
        session.add(parent2)
        session.commit()

        model = session.query(Child).one()
        compare(Child(id=3, value='Foo'), actual=model)

    def test_null_primary_key(self) -> None:

        Model, _, session = self.make_all()

        samples = Collection({Model: {'value': 'two'}})

        model1 = samples.make(Model)
        model2 = samples.make(Model)
        self.assertFalse(model1 is model2)

        session.add(model1)
        session.add(model2)
        session.commit()

        models = session.query(Model).all()
        compare(len(set(m.id for m in models)), expected=2)
        compare(set(m.value for m in models), expected={'two'})

    def test_null_primary_key_with_set(self) -> None:

        Model, _, session = self.make_all()

        collection = Collection({Model: {'value': 'two'}})
        samples = Set(collection)

        model1 = samples.get(Model)
        model2 = samples.get(Model)
        self.assertFalse(model1 is model2)

        session.add(model1)
        session.add(model2)
        session.commit()

        models = session.query(Model).all()
        compare(len(set(m.id for m in models)), expected=2)
        compare(set(m.value for m in models), expected={'two'})

    def test_closed_session(self) -> None:

        Model, samples, session = self.make_all()

        obj1 = samples.make(Model)
        session.add(obj1)
        session.commit()
        session.close()

        obj2 = samples.make(Model)
        compare(obj2.value, expected='two')

    def test_closed_session_with_set(self) -> None:

        Model, collection, session = self.make_all()

        samples = Set(collection)
        obj1 = samples.get(Model)
        session.add(obj1)
        session.commit()
        session.close()

        obj2 = collection.make(Model)
        compare(obj2.value, expected='two')

    def test_relationship_with_backrefs(self) -> None:
        class Base(DeclarativeBase): pass

        class Bar(Base):
            __tablename__ = 'bar'
            id = Column(Integer, primary_key=True)
            value = Column(Integer)

        class Foo(Base):
            __tablename__ = 'foo'
            id = Column(Integer, primary_key=True)
            bar_id = Column(String, ForeignKey('bar.id'))
            bar = relationship('Bar', backref='foos')

        class Baz(Base):
            __tablename__ = 'baz'
            id = Column(Integer, primary_key=True)
            foo_id = Column(String, ForeignKey('foo.id'))
            foo = relationship('Foo')

        collection = Collection({
            Bar: {'id': 1, 'value': 2},
            Foo: {'id': 3, 'bar': Bar, 'bar_id': 1},
            Baz: {'id': 4, 'foo': Foo, 'foo_id': 3}
        })
        samples = Set(collection)

        session = self.make_session(Base)

        session.add(samples.get(Baz, id=5, foo=samples.get(Foo, id=7)))
        session.commit()

        compare(session.query(Foo.id).all(), expected=[(7, )])
