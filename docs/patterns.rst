Patterns of Use
===============

This section covers patterns that make use of more than one of the topics covered in 
other sections.

Inserting many SQLAlchemy objects
---------------------------------

.. invisible-code-block: python

    from textwrap import dedent
    from typing import Type, Optional
    
    import pytest
    from datetime import date as date_type, datetime, date
    from sqlalchemy import Engine, create_engine
    from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column
    from testfixtures import compare, ShouldAssert
    
    from chide.formats import PrettyFormat
    from chide.sqlalchemy import MappedSimplifier
    
    
    class Base(DeclarativeBase):
        pass

If you have an ORM-mapped class, such as the following one, that needs several rows to be
present in its table:

.. code-block:: python

    class Weather(Base):
        __tablename__ = 'weather'
        city: Mapped[str] = mapped_column(primary_key=True)
        temp_lo: Mapped[int]
        temp_hi: Mapped[int]
        prcp: Mapped[Optional[float]]
        date: Mapped[date_type] = mapped_column(primary_key=True)

You can construct a helper such as this:

.. code-block:: python

    class DatabaseHelper:
    
        def __init__(self) -> None:
            self.engine = create_engine("sqlite+pysqlite:///:memory:")
            Base.metadata.create_all(self.engine)
            
        def insert(self, type_: Type[Base], text: str) -> None:
            pretty = PrettyFormat(column_parse={
                'date': lambda text_: datetime.strptime(text_, '%Y-%m-%d').date()
            })
            with Session(self.engine) as session, session.begin():
                session.add_all(type_(**attrs) for attrs in pretty.parse(text))

This can be used as a pytest fixture as follows:

.. code-block:: python

    @pytest.fixture
    def database() -> DatabaseHelper:
        return DatabaseHelper()
        
Inside your test, you can then use the helper as follows:

.. code-block:: python

    def test_your_code(database: DatabaseHelper) -> None:
        database.insert(
            Weather,
            """
            +-------------+-------+-------+----+----------+
            |city         |temp_lo|temp_hi|prcp|date      |
            +-------------+-------+-------+----+----------+
            |San Francisco|4      |5      |0.25|1994-11-27|
            |San Francisco|43     |57     |0   |1994-11-29|
            |Hayward      |37     |54     |None|1994-11-29|
            +-------------+-------+-------+----+----------+
            """
        )
        
        ...  # You code under test here

.. invisible-code-block: python

    database = DatabaseHelper()
    test_your_code(database)
    compare(
        Session(database.engine).query(Weather).all(),
        expected=[
            Weather(city='San Francisco', temp_lo=4, temp_hi=5, prcp=0.25, date=date(1994, 11, 27)),
            Weather(city='San Francisco', temp_lo=43, temp_hi=57, prcp=0, date=date(1994, 11, 29)),
            Weather(city='Hayward', temp_lo=37, temp_hi=54, prcp=None, date=date(1994, 11, 29)),
        ],
        ignore_attributes=['_sa_instance_state']
    )

Checking the contents of SQLAlchemy ORM-mapped tables
-----------------------------------------------------

Many database tables have a sufficient number of columns that when making assertions about
their contents by instantiating ORM-mapped objects and using a tool such as
:doc:`testfixtures.compare <testfixtures:comparing>` to make assertions about them,
the vertical space taken up can quickly make the tests much harder to read.

Given an example ORM-mapped class such as this:

.. invisible-code-block: python

    class Base(DeclarativeBase):
        pass

.. code-block:: python

    class Weather(Base):
        __tablename__ = 'weather'
        city: Mapped[str] = mapped_column(primary_key=True)
        temp_lo: Mapped[int]
        temp_hi: Mapped[int]
        prcp: Mapped[Optional[float]]
        date: Mapped[date_type] = mapped_column(primary_key=True)

Two possible patterns are presented below, which vary by the way in which failed 
assertions are reported:

Unified diff presented on failure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To make assertions about the contents of a table, and present any failures as a unified diff
you can construct a helper such as this, making using of text diffing provided by 
:func:`testfixtures:testfixtures.compare`:

.. code-block:: python

    class DatabaseHelper:
    
        def __init__(self) -> None:
            self.engine = create_engine("sqlite+pysqlite:///:memory:")
            Base.metadata.create_all(self.engine)
        
        def check(self, type_: Type[Base], text: str) -> None:
            pretty = PrettyFormat(
                column_parse={'date': lambda text_: datetime.strptime(text_, '%Y-%m-%d').date()},
                column_render={'date': lambda d: d.strftime('%Y-%m-%d')},
                padding=0,
            )
            with Session(self.engine) as session, session.begin():
                expected = pretty.parse(text)
                actual = MappedSimplifier().many(session.query(type_).all())
                actual_text = pretty.render(actual, ref=expected)
                compare(
                    actual=actual_text,
                    expected=pretty.render(expected, ref=pretty.parse(actual_text)),
                )


This can be used as a pytest fixture as follows:

.. code-block:: python

    @pytest.fixture
    def database() -> DatabaseHelper:
        return DatabaseHelper()

Inside your test, you can then use the helper as follows:

.. code-block:: python

    def test_your_code(database: DatabaseHelper) -> None:
        # Sample code under test:
        with Session(database.engine) as session, session.begin():
            session.add_all((
                Weather(city='San Francisco', temp_lo=4, temp_hi=5, prcp=0.25, date=date(1994, 11, 27)),
                Weather(city='San Francisco', temp_lo=-1, temp_hi=3, prcp=0.2, date=date(1994, 11, 20)),
                Weather(city='Hayward', temp_lo=37, temp_hi=54, prcp=None, date=date(1994, 11, 29)),
            ))

        database.check(
            Weather,
            """
            +-------------+-------+-------+----+----------+
            |city         |temp_lo|temp_hi|prcp|date      |
            +-------------+-------+-------+----+----------+
            |San Francisco|4      |5      |0.25|1994-11-27|
            |San Francisco|43     |57     |0   |1994-11-29|
            |Hayward      |37     |54     |None|1994-11-29|
            +-------------+-------+-------+----+----------+
            """
        )

Since the test fails, we get the following :class:`AssertionError`::

    --- expected
    +++ actual
    @@ -2,7 +2,7 @@
     |city         |temp_lo|temp_hi|prcp|date      |
     +-------------+-------+-------+----+----------+
     |San Francisco|4      |5      |0.25|1994-11-27|
    -|San Francisco|43     |57     |0   |1994-11-29|
    +|San Francisco|-1     |3      |0.2 |1994-11-20|
     |Hayward      |37     |54     |None|1994-11-29|
     +-------------+-------+-------+----+----------+
 
.. -> expected_assertion

.. invisible-code-block: python

    with ShouldAssert('\n'+expected_assertion+' '):
        test_your_code(DatabaseHelper())

Detailed explanation and expected content on failure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


To make assertions about the contents of a table, and present an explanation of any failures, 
as well as what the expected content should have looked like for easy copy and paste into
the failing test, you can construct a helper such as this, making using of 
:func:`testfixtures:testfixtures.compare`'s features:

.. code-block:: python

    class DatabaseHelper:
    
        def __init__(self) -> None:
            self.engine = create_engine("sqlite+pysqlite:///:memory:")
            Base.metadata.create_all(self.engine)
        
        def check(self, type_: Type[Base], text: str) -> None:
            pretty = PrettyFormat(
                column_parse={'date': lambda text_: datetime.strptime(text_, '%Y-%m-%d').date()},
                column_render={'date': lambda d: d.strftime('%Y-%m-%d')},
                padding=0,
            )
            with Session(self.engine) as session, session.begin():
                actual = MappedSimplifier().many(session.query(type_).all())
                expected = pretty.parse(text)
                compare(
                    actual=actual,
                    expected=expected,
                    suffix='\nShould be:\n'+pretty.render(actual, ref=expected)
                )


This can be used as a pytest fixture as follows:

.. code-block:: python

    @pytest.fixture
    def database() -> DatabaseHelper:
        return DatabaseHelper()

Inside your test, you can then use the helper as follows:

.. code-block:: python

    def test_your_code(database: DatabaseHelper) -> None:
        # Sample code under test:
        with Session(database.engine) as session, session.begin():
            session.add_all((
                Weather(city='San Francisco', temp_lo=4, temp_hi=5, prcp=0.25, date=date(1994, 11, 27)),
                Weather(city='San Francisco', temp_lo=-1, temp_hi=3, prcp=0.2, date=date(1994, 11, 20)),
                Weather(city='Hayward', temp_lo=37, temp_hi=54, prcp=None, date=date(1994, 11, 29)),
            ))

        database.check(
            Weather,
            """
            +-------------+-------+-------+----+----------+
            |city         |temp_lo|temp_hi|prcp|date      |
            +-------------+-------+-------+----+----------+
            |San Francisco|4      |5      |0.25|1994-11-27|
            |San Francisco|43     |57     |0   |1994-11-29|
            |Hayward      |37     |54     |None|1994-11-29|
            +-------------+-------+-------+----+----------+
            """
        )

Since the test fails, we get the following extensive :class:`AssertionError`::

    sequence not as expected:

    same:
    [{'city': 'San Francisco',
      'date': datetime.date(1994, 11, 27),
      'prcp': 0.25,
      'temp_hi': 5,
      'temp_lo': 4}]

    expected:
    [{'city': 'San Francisco',
      'date': datetime.date(1994, 11, 29),
      'prcp': 0,
      'temp_hi': 57,
      'temp_lo': 43},
     {'city': 'Hayward',
      'date': datetime.date(1994, 11, 29),
      'prcp': None,
      'temp_hi': 54,
      'temp_lo': 37}]

    actual:
    [{'city': 'San Francisco',
      'date': datetime.date(1994, 11, 20),
      'prcp': 0.2,
      'temp_hi': 3,
      'temp_lo': -1},
     {'city': 'Hayward',
      'date': datetime.date(1994, 11, 29),
      'prcp': None,
      'temp_hi': 54,
      'temp_lo': 37}]

    While comparing [1]: dict not as expected:

    same:
    ['city']

    values differ:
    'date': datetime.date(1994, 11, 29) (expected) != datetime.date(1994, 11, 20) (actual)
    'prcp': 0 (expected) != 0.2 (actual)
    'temp_hi': 57 (expected) != 3 (actual)
    'temp_lo': 43 (expected) != -1 (actual)

    While comparing [1]['date']: datetime.date(1994, 11, 29) (expected) != datetime.date(1994, 11, 20) (actual)

    While comparing [1]['prcp']: 0 (expected) != 0.2 (actual)

    Should be:
    +-------------+-------+-------+----+----------+
    |city         |temp_lo|temp_hi|prcp|date      |
    +-------------+-------+-------+----+----------+
    |San Francisco|4      |5      |0.25|1994-11-27|
    |San Francisco|-1     |3      |0.2 |1994-11-20|
    |Hayward      |37     |54     |None|1994-11-29|
    +-------------+-------+-------+----+----------+
 
.. -> expected_assertion

.. invisible-code-block: python

    with ShouldAssert(expected_assertion):
        test_your_code(DatabaseHelper())


Make different sample objects of the same type
----------------------------------------------

Some sample objects are not differentiated by type but by their attributes.
For example, when generating sample JSON data from simple data types, you may
have people:

.. code-block:: python

  person = {'name': 'John Doe'}

You may also have addresses:

.. code-block:: python

  address = {'value': 'Somewhere in the clouds'}

In order to store these in a :class:`Collection`, annotated types can be used:

.. code-block:: python

    from typing import Annotated
    from chide import Collection

    Person = Annotated[dict[str, str], 'Person']
    Address = Annotated[dict[str, str], 'Address']

    samples = Collection({Person: {'name': 'John Doe', 'address': Address}})

To add this kind of sample to an existing collection, the type must be supplied:

.. code-block:: python

    samples.add({'value': 'Somewhere in the clouds'}, annotated=Address)

Samples of these types can now be created as normal:

>>> samples.make(Person)
{'name': 'John Doe', 'address': {'value': 'Somewhere in the clouds'}}

Note that no sample is available for the un-annotated type:

>>> samples.make(dict)
Traceback (most recent call last):
...
KeyError: <class 'dict'>
