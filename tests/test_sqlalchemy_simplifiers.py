from datetime import date as date_type, date
from typing import Optional

import pytest
from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from testfixtures import compare

from chide.sqlalchemy import MappedSimplifier, RowSimplifier


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


def test_row_simplifier(engine: Engine) ->None:
    with Session(engine) as session, session.begin():
        session.add_all((
            Weather(city='San Francisco', temp_lo=4, temp_hi=5, prcp=0.25, date=date(1994, 11, 27)),
            Weather(city='San Francisco', temp_lo=43, temp_hi=57, prcp=0, date=date(1994, 11, 29)),
            Weather(city='Hayward', temp_lo=37, temp_hi=54, prcp=None, date=date(1994, 11, 29)),
        ))
        session.flush()
        actual = RowSimplifier().many(session.connection().execute(select(Weather.__table__)))
        compare(
            actual,
            expected=[
                {'city': 'San Francisco',
                 'date': date(1994, 11, 27),
                 'prcp': 0.25,
                 'temp_hi': 5,
                 'temp_lo': 4},
                {'city': 'San Francisco',
                 'date': date(1994, 11, 29),
                 'prcp': 0.0,
                 'temp_hi': 57,
                 'temp_lo': 43},
                {'city': 'Hayward',
                 'date': date(1994, 11, 29),
                 'prcp': None,
                 'temp_hi': 54,
                 'temp_lo': 37}
            ],
        )


def test_mapped_simplifier(engine: Engine) ->None:
    with Session(engine) as session, session.begin():
        session.add_all((
            Weather(city='San Francisco', temp_lo=4, temp_hi=5, prcp=0.25, date=date(1994, 11, 27)),
            Weather(city='San Francisco', temp_lo=43, temp_hi=57, prcp=0, date=date(1994, 11, 29)),
            Weather(city='Hayward', temp_lo=37, temp_hi=54, prcp=None, date=date(1994, 11, 29)),
        ))
        actual = MappedSimplifier().many(session.query(Weather).all())
        compare(
            actual,
            expected=[
                {'city': 'San Francisco',
                 'date': date(1994, 11, 27),
                 'prcp': 0.25,
                 'temp_hi': 5,
                 'temp_lo': 4},
                {'city': 'San Francisco',
                 'date': date(1994, 11, 29),
                 'prcp': 0.0,
                 'temp_hi': 57,
                 'temp_lo': 43},
                {'city': 'Hayward',
                 'date': date(1994, 11, 29),
                 'prcp': None,
                 'temp_hi': 54,
                 'temp_lo': 37}
            ],
        )
