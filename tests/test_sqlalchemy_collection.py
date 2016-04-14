from unittest import TestCase

from sqlalchemy import Column, String, create_engine, ForeignKey
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from testfixtures import compare

from chide.sqlalchemy import Collection
from .helpers import Comparable


class TestSQLAlchemyCollection(TestCase):

    def make_session(self, base):
        engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=engine)
        base.metadata.create_all(engine)
        return Session()

    def test_simple_model(self):

        Base = declarative_base()

        class Model(Comparable, Base):
            __tablename__ = 'model'
            id = Column('id_', Integer, primary_key=True)
            value = Column(String)

        samples = Collection({Model: {'id': 1, 'value': 'two'}})

        model1 = samples.make(Model)
        model2 = samples.make(Model)
        self.assertTrue(model1 is model2)

        session = self.make_session(Base)
        session.add(samples.make(Model))
        session.add(samples.make(Model))
        session.commit()

        model = session.query(Model).one()
        compare(Model(id=1, value='two'), actual=model)

    def test_foreign_key(self):

        Base = declarative_base()

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
        self.assertFalse(parent1 is parent2)
        session = self.make_session(Base)
        session.add(parent1)
        session.add(parent2)
        session.commit()

        model = session.query(Child).one()
        compare(Child(id=3, value='Foo'), actual=model)

    def test_null_primary_key(self):

        Base = declarative_base()

        class Model(Comparable, Base):
            __tablename__ = 'model'
            id = Column(Integer, primary_key=True)
            value = Column(String)

        samples = Collection({Model: {'value': 'two'}})

        model1 = samples.make(Model)
        model2 = samples.make(Model)
        self.assertFalse(model1 is model2)

        session = self.make_session(Base)
        session.add(model1)
        session.add(model2)
        session.commit()

        models = session.query(Model).all()
        compare(len(set(m.id for m in models)), expected=2)
        compare(set(m.value for m in models), expected={'two'})
