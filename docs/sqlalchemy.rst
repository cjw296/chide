SQLAlchemy
==========

One common use of :mod:`chide` is for creating sample objects and making assertions about
database table contents when using `SQLAlchemy`__. As a result, there are specialised
implementations included to make life easier that are described below.

__ https://www.sqlalchemy.org/

.. _sqlalchemy-set:

Sets
----

:mod:`chide` has a special :class:`~chide.Set` subclass that helps to make sure
only one sample object is created with a particular primary key in any
one table.

.. invisible-code-block: python

    from sqlalchemy import Column, String, create_engine, ForeignKey
    from sqlalchemy import Integer
    from sqlalchemy.orm import sessionmaker, relationship, declarative_base
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

.. _sqlalchemy-row-simplifier:

Row Simplifier
--------------

For a table such as this:

.. code-block:: python

    from sqlalchemy import MetaData, Table, Column, Integer, String
    
    metadata = MetaData()
    
    user_table = Table(
        "user_account",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(30)),
        Column("fullname", String),
    )
   
.. invisible-code-block: python

    from sqlalchemy import insert, select

    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)
    with engine.connect() as conn:
        result = conn.execute(
            insert(user_table),
            [
                {"name": "sandy", "fullname": "Sandy Cheeks"},
                {"name": "patrick", "fullname": "Patrick Star"},
            ],
        )
        conn.commit()

A :doc:`simplifier <simplifiers>` is included for the :class:`rows <sqlalchemy.engine.Row>` returned
by a query such as this:

.. code-block:: python

  with engine.connect() as conn:
      rows = conn.execute(select(user_table))
      
It is used as follows:

>>> from chide.sqlalchemy import RowSimplifier
>>> for attrs in RowSimplifier().many(rows):
...     print(attrs)
{'id': 1, 'name': 'sandy', 'fullname': 'Sandy Cheeks'}
{'id': 2, 'name': 'patrick', 'fullname': 'Patrick Star'}

.. _sqlalchemy-mapped-simplifier:

ORM-Mapped Object Simplifier
----------------------------

For an ORM-mapped objects such as this:

.. code-block:: python

    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
    
    class Base(DeclarativeBase):
        pass
        
    class User(Base):
        __tablename__ = "user_account"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str]
        fullname: Mapped[str | None]
   
.. invisible-code-block: python

    from sqlalchemy.orm import Session

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session, session.begin():
        session.add_all((
            User(name="squidward", fullname="Squidward Tentacles"),
            User(name="ehkrabs", fullname="Eugene H. Krabs")
        ))

A :doc:`simplifier <simplifiers>` is included that can be used to simplify the results of a query 
such as this:

.. code-block:: python

  with Session(engine) as session:
      objects = session.query(User)
      
It is used as follows:

>>> from chide.sqlalchemy import MappedSimplifier
>>> for attrs in MappedSimplifier().many(objects):
...     print(attrs)
{'id': 1, 'name': 'squidward', 'fullname': 'Squidward Tentacles'}
{'id': 2, 'name': 'ehkrabs', 'fullname': 'Eugene H. Krabs'}
