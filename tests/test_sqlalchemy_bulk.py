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


class Weather(Base):
    __tablename__ = 'weather'
    city: Mapped[str] = mapped_column(primary_key=True)
    temp_lo: Mapped[int]
    temp_hi: Mapped[int]
    prcp: Mapped[Optional[float]]
    date: Mapped[date_type] = mapped_column(primary_key=True)


@pytest.fixture
def engine() -> Engine:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def table_insert(engine: Engine, type_: Type[Base], text: str) -> None:
    pretty = PrettyFormat(column_parse={
        'date': lambda text_: datetime.strptime(text_, '%Y-%m-%d').date()
    })
    with Session(engine) as session, session.begin():
        session.add_all(type_(**attrs) for attrs in pretty.parse(text))


def table_check_rows(engine: Engine, type_: Type[Base], text: str) -> None:
    pretty = PrettyFormat(
        column_parse={'date': lambda text_: datetime.strptime(text_, '%Y-%m-%d').date()},
        column_render={'date': lambda d: d.strftime('%Y-%m-%d')},
        padding=0,
    )
    with Session(engine) as session, session.begin():
        actual = MappedSimplifier().many(session.query(type_).all())
        expected = pretty.parse(text)
        compare(
            actual=actual,
            expected=expected,
            suffix='\nShould be:\n'+pretty.render(actual, ref=expected)
        )


def table_check_diff(engine: Engine, type_: Type[Base], text: str) -> None:
    pretty = PrettyFormat(
        column_parse={'date': lambda text_: datetime.strptime(text_, '%Y-%m-%d').date()},
        column_render={'date': lambda d: d.strftime('%Y-%m-%d')},
        padding=0,
    )
    with Session(engine) as session, session.begin():
        expected = pretty.parse(text)
        actual = MappedSimplifier().many(session.query(type_).all())
        actual_text = pretty.render(actual, ref=expected)
        compare(
            actual=actual_text,
            expected=pretty.render(expected, ref=pretty.parse(actual_text)),
        )


def test_insert(engine: Engine) -> None:
    table_insert(
        engine,
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
    compare(
        Session(engine).query(Weather).all(),
        expected=[
            Weather(city='San Francisco', temp_lo=4, temp_hi=5, prcp=0.25, date=date(1994, 11, 27)),
            Weather(city='San Francisco', temp_lo=43, temp_hi=57, prcp=0, date=date(1994, 11, 29)),
            Weather(city='Hayward', temp_lo=37, temp_hi=54, prcp=None, date=date(1994, 11, 29)),
        ],
        ignore_attributes=['_sa_instance_state']
    )


def test_render_pass(engine: Engine) -> None:
    with Session(engine) as session, session.begin():
        session.add_all((
            Weather(city='San Francisco', temp_lo=4, temp_hi=5, prcp=0.25, date=date(1994, 11, 27)),
            Weather(city='San Francisco', temp_lo=43, temp_hi=57, prcp=0, date=date(1994, 11, 29)),
            Weather(city='Hayward', temp_lo=37, temp_hi=54, prcp=None, date=date(1994, 11, 29)),
        ))
    table_check_rows(
        engine,
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


def test_render_fail(engine: Engine) -> None:
    # This is to check that column width are as expected during comparison,
    # even when substitution is used in building the expected value:
    sample_lo_temp = 4
    with Session(engine) as session, session.begin():
        session.add_all((
            Weather(city='San Francisco', temp_lo=4, temp_hi=5, prcp=0.25, date=date(1994, 11, 27)),
            Weather(city='San Francisco', temp_lo=-1, temp_hi=3, prcp=0.2, date=date(1994, 11, 20)),
            Weather(city='Hayward', temp_lo=37, temp_hi=54, prcp=None, date=date(1994, 11, 29)),
        ))
    with ShouldAssert(
        dedent("""\
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
            +-------------+----------------+-------+----+----------+
            |city         |temp_lo         |temp_hi|prcp|date      |
            +-------------+----------------+-------+----+----------+
            |San Francisco|4               |5      |0.25|1994-11-27|
            |San Francisco|-1              |3      |0.2 |1994-11-20|
            |Hayward      |37              |54     |None|1994-11-29|
            +-------------+----------------+-------+----+----------+
            """)
    ):
        table_check_rows(
            engine,
            Weather,
            f"""
            +-------------+----------------+-------+----+----------+
            |city         |temp_lo         |temp_hi|prcp|date      |
            +-------------+----------------+-------+----+----------+
            |San Francisco|{sample_lo_temp}|5      |0.25|1994-11-27|
            |San Francisco|43              |57     |0   |1994-11-29|
            |Hayward      |37              |54     |None|1994-11-29|
            +-------------+----------------+-------+----+----------+
            """
        )


def test_render_fail_unified_diff(engine: Engine) -> None:
    with Session(engine) as session, session.begin():
        session.add_all((
            Weather(city='wide in db', temp_lo=1, temp_hi=5, prcp=0.25, date=date(1994, 11, 27)),
        ))
    with ShouldAssert(
            dedent("""
                --- expected
                +++ actual
                @@ -1,6 +1,6 @@
                 +----------+---------+-------+----+----------+
                 |city      |temp_lo  |temp_hi|prcp|date      |
                 +----------+---------+-------+----+----------+
                -|narrow    |111111122|5      |0.25|1994-11-27|
                +|wide in db|1        |5      |0.25|1994-11-27|
                 +----------+---------+-------+----+----------+
                """)+' ',
    ):
        table_check_diff(
            engine,
            Weather,
            f"""
            +----------------+-------+----+----------+
            |city  |temp_lo  |temp_hi|prcp|date      |
            +------+---------+-------+----+----------+
            |narrow|111111122|5      |0.25|1994-11-27|
            +------+---------+-------+----+----------+
            """
        )
