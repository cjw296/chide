Use with SQLAlchemy
===================

:mod:`chide` has a special :class:`~chide.Set` subclass that helps to make sure
only one sample object is created with a particular primary key in any
one table.

.. invisible-code-block: python

    from sqlalchemy import Column, String, create_engine, ForeignKey
    from sqlalchemy import Integer
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, relationship
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    Base = declarative_base()

For example, given these two models:

.. code-block:: python

    class Parent(Base):
        __tablename__ = 'parent'
        id = Column(Integer, primary_key=True)
        child_id = Column(Integer, ForeignKey('child.id'))
        child = relationship('Child')

    class Child(Base):
        __tablename__ = 'child'
        id = Column(Integer, primary_key=True)
        value = Column(Integer)

.. invisible-code-block: python

    Base.metadata.create_all(engine)

We can set up a collection of sample values as follows:

.. code-block:: python

    from chide import Collection

    samples = Collection({
        Parent: {'id': 1, 'child': Child},
        Child: {'id': 3, 'value': 42}
    })

Now we can quickly make sample objects and add them to a session:

>>> session = Session()
>>> session.add(samples.make(Parent))
>>> session.commit()

This gives us a parent and a child:

>>> session.query(Parent).one()
<Parent ...>
>>> _.child
<Child ...>

.. invisible-code-block: python

    session = Session()
    session.query(Parent).delete()
    session.query(Child).delete()
    session.commit()

If we create multiple parent objects and don't want to have to worry about
clashing children being created by mistake, we can use a
:class:`chide.sqlalchemy.Set` to make sure that we only have one sample
object with a given primary key at any time:

>>> from chide.sqlalchemy import Set
>>> current_samples = Set(samples)
>>> session = Session()
>>> session.add(current_samples.get(Parent, id=1))
>>> session.add(current_samples.get(Parent, id=2))
>>> session.commit()

This gives us two parents that both point to the same child:

>>> parent1 = session.query(Parent).filter_by(id=1).one()
>>> parent2 = session.query(Parent).filter_by(id=2).one()
>>> parent1.child is parent2.child
True

.. invisible-code-block: python

    session = Session()
    session.query(Parent).delete()
    session.query(Child).delete()
    session.commit()

Of course, if we want different children, that's easy too:

>>> session = Session()
>>> session.add(current_samples.get(Parent, id=3, child=Child(value=6)))
>>> session.add(current_samples.get(Parent, id=4, child=Child(value=7)))
>>> session.commit()

The children's primary keys will be created by the database, but the values are
as we need them:

>>> parent3 = session.query(Parent).filter_by(id=3).one()
>>> parent3.child.value
6
>>> parent4 = session.query(Parent).filter_by(id=4).one()
>>> parent4.child.value
7
