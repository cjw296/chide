from datetime import date, time, datetime
from textwrap import dedent

from testfixtures import compare

from chide.formats import PrettyFormat, HEADER, ROW, CSVFormat


class TestPrettyFormat:

    def test_simple_parse_single_row(self) -> None:
        pretty = PrettyFormat()
        actual = pretty.parse(
            """
            +---+------+
            | x | y    |
            +---+------+
            | 1 | foo  |
            +---+------+
            """
        )
        compare(actual, expected=[
            {'x': 1, 'y': 'foo'},
        ])

    def test_simple_parse_multiple_rows(self) -> None:
        pretty = PrettyFormat()
        actual = pretty.parse(
            """
            +---+------+
            | x | y    |
            +---+------+
            | 1 | foo  |
            | 2 |" bar"|
            | 3 |'baz '|
            +---+------+
            """
        )
        compare(actual, expected=[
            {'x': 1, 'y': 'foo'},
            {'x': 2, 'y': ' bar'},
            {'x': 3, 'y': 'baz '},
        ])

    def test_parse_with_builtin_types(self) -> None:
        pretty = PrettyFormat(types_location=ROW)
        actual = pretty.parse(
            """
            +-----+------+
            | x   | y    |
            +-----+------+
            |float| str  |
            +-----+------+
            | 1   | foo  |
            | 2   | bar  |
            | 3   | baz  |
            +-----+------+
            """
        )
        compare(actual, expected=[
            {'x': 1.0, 'y': 'foo'},
            {'x': 2.0, 'y': 'bar'},
            {'x': 3.0, 'y': 'baz'},
        ])

    def test_parse_with_types_in_header(self) -> None:
        pretty = PrettyFormat(types_location=HEADER)
        actual = pretty.parse(
            """
            +-----------+-----------+
            | x (float) | y (str)   |
            +-----------+-----------+
            | 1         | foo       |
            | 2         | bar       |
            | 3         | baz       |
            +-----------+-----------+
            """
        )
        compare(actual, expected=[
            {'x': 1.0, 'y': 'foo'},
            {'x': 2.0, 'y': 'bar'},
            {'x': 3.0, 'y': 'baz'},
        ])

    def test_parse_with_explict_type_parsers(self) -> None:
        pretty = PrettyFormat(
            types_location=HEADER,
            type_parse={'bytes': lambda text: text.encode('utf-8')}
        )
        actual = pretty.parse(
            """
            +-+--------+
            |x|y(bytes)|
            +-+--------+
            |1| foo    |
            |2| bar    |
            |3| baz    |
            +-+--------+
            """
        )
        compare(actual, expected=[
            {'x': 1, 'y': b'foo'},
            {'x': 2, 'y': b'bar'},
            {'x': 3, 'y': b'baz'},
        ])

    def test_parse_with_explict_column_parsers(self) -> None:
        pretty = PrettyFormat(
            column_parse={
                'x': int,
                'y': lambda text: text.encode('utf-8')
            }
        )
        actual = pretty.parse(
            """
            +-----+------+
            | x   | y    |
            +-----+------+
            | 1   | foo  |
            | 2   | bar  |
            | 3   | baz  |
            +-----+------+
            """
        )
        compare(actual, expected=[
            {'x': 1, 'y': b'foo'},
            {'x': 2, 'y': b'bar'},
            {'x': 3, 'y': b'baz'},
        ])

    def test_parse_literal_eval_falls_back_to_string(self) -> None:
        pretty = PrettyFormat()
        actual = pretty.parse(
            """
            +----+
            | x  |
            +----+
            | 1 2|
            +----+
            """
        )
        compare(actual, expected=[
            {'x': '1 2'},
        ])

    def test_parse_returns_column_widths(self) -> None:
        pretty = PrettyFormat()
        sample_lo_temp = 4
        actual = pretty.parse(
            f"""
            +-------------+----------------+---------+
            |city         |temp_lo         | temp_hi |
            +-------------+----------------+---------+
            |San Francisco|{sample_lo_temp}| 5       |
            +-------------+----------------+---------+
            """
        )
        compare(actual, expected=[
            {'city': 'San Francisco', 'temp_lo': 4, 'temp_hi': 5},
        ])
        # temp_hi width has padding removed from 9, down to 7
        compare(actual.widths, expected={'city': 13, 'temp_lo': 16, 'temp_hi': 7})

    def test_render_simple_single_row(self) -> None:
        pretty = PrettyFormat()
        actual = pretty.render([
            {'x': 1, 'y': 'foo'},
        ])
        compare(
            actual,
            expected=dedent("""\
            +---+-----+
            | x | y   |
            +---+-----+
            | 1 | foo |
            +---+-----+
            """)
        )

    def test_render_no_padding(self) -> None:
        pretty = PrettyFormat(padding=0)
        actual = pretty.render([
            {'x': 1, 'y': 'foo'},
        ])
        compare(
            actual,
            expected=dedent("""\
            +-+---+
            |x|y  |
            +-+---+
            |1|foo|
            +-+---+
            """)
        )

    def test_render_moar_padding(self) -> None:
        pretty = PrettyFormat(padding=3)
        actual = pretty.render([
            {'x': 1, 'y': 'foo'},
        ])
        compare(
            actual,
            expected=dedent("""\
            +-------+---------+
            |   x   |   y     |
            +-------+---------+
            |   1   |   foo   |
            +-------+---------+
            """)
        )

    def test_render_simple_multiple_rows(self) -> None:
        pretty = PrettyFormat()
        actual = pretty.render([
            {'x': 1, 'y': 'foo'},
            {'x': 2, 'y': ' bar'},
            {'x': 3, 'y': 'baz '},
        ])
        compare(
            actual,
            expected=dedent("""\
            +---+--------+
            | x | y      |
            +---+--------+
            | 1 | foo    |
            | 2 | ' bar' |
            | 3 | 'baz ' |
            +---+--------+
            """)
        )

    def test_render_with_explict_type_renderers(self) -> None:
        pretty = PrettyFormat(type_render={bytes: lambda b: b.decode('utf-8')})
        actual = pretty.render([
            {'x': 1, 'y': b'foo'},
            {'x': 2, 'y': b'bar'},
            {'x': 3, 'y': b'baz'},
        ])
        compare(
            actual,
            expected=dedent("""\
            +---+-----+
            | x | y   |
            +---+-----+
            | 1 | foo |
            | 2 | bar |
            | 3 | baz |
            +---+-----+
            """)
        )

    def test_render_with_explict_column_renderers(self) -> None:
        pretty = PrettyFormat(
            column_render={
                'x': lambda f: f'{f:.0f}',
                'y': lambda b: b.decode('utf-8')
            }
        )
        actual = pretty.render([
            {'x': 1.1, 'y': b'foo'},
            {'x': 2.2, 'y': b'bar'},
            {'x': 3.3, 'y': b'baz'},
        ])
        compare(
            actual,
            expected=dedent("""\
            +---+-----+
            | x | y   |
            +---+-----+
            | 1 | foo |
            | 2 | bar |
            | 3 | baz |
            +---+-----+
            """)
        )

    def test_render_empty(self) -> None:
        pretty = PrettyFormat(types_location=ROW)
        actual = pretty.render([])
        compare(
            actual,
            expected=dedent("""\
            +
            +
            """)
        )

    def test_render_with_reference(self) -> None:
        pretty = PrettyFormat()
        ref = [{'z': 'X', 'y': 'XXXXX'}]
        actual = pretty.render([{'x': 1, 'y': 'foo'}], ref)
        compare(
            actual,
            expected=dedent("""\
            +------+-------+---+
            | z    | y     | x |
            +------+-------+---+
            | None | foo   | 1 |
            +------+-------+---+
            """)
        )

    def test_render_with_reference_and_padding(self) -> None:
        pretty = PrettyFormat(padding=3)
        ref = pretty.parse(dedent("""\
            +-------+---------+
            |   z   |   y     |
            +-------+---------+
            |   X   |   XXX   |
            +-------+---------+
            """))
        actual = pretty.render([{'y': 'foo'}], ref)
        compare(
            actual,
            expected=dedent("""\
            +----------+---------+
            |   z      |   y     |
            +----------+---------+
            |   None   |   foo   |
            +----------+---------+
            """)
        )

    def test_render_with_empty_reference(self) -> None:
        pretty = PrettyFormat()
        actual = pretty.render([{'x': 1, 'y': 'foo'}], ref=[])
        compare(
            actual,
            expected=dedent("""\
            +---+-----+
            | x | y   |
            +---+-----+
            | 1 | foo |
            +---+-----+
            """)
        )

    def test_round_trip_values_simple(self) -> None:
        expected = [
            {'x': 1, 'y': 'foo'},
        ]
        pretty = PrettyFormat()
        rendered = pretty.render(expected)
        actual = pretty.parse(rendered)
        compare(expected=expected, actual=actual)

    def test_round_trip_values_multiple_rows(self) -> None:
        expected = [
            {'x': 1, 'y': 'foo'},
            {'x': 2, 'y': ' bar'},
            {'x': 3, 'y': 'baz '},
        ]
        pretty = PrettyFormat()
        rendered = pretty.render(expected)
        actual = pretty.parse(rendered)
        compare(expected=expected, actual=actual)

    def test_round_trip_text_explicit_types_row(self) -> None:
        source = dedent("""\
            +-------+-----+
            | x     | y   |
            +-------+-----+
            | float | str |
            +-------+-----+
            | 1.0   | foo |
            | 2.0   | bar |
            | 3.0   | baz |
            +-------+-----+
            """)
        pretty = PrettyFormat(types_location=ROW)
        parsed = pretty.parse(source)
        rendered = pretty.render(parsed)
        compare(expected=source, actual=rendered)

    def test_round_trip_text_explicit_types_in_header(self) -> None:
        source = dedent("""\
            +-----------+---------+
            | x (float) | y (str) |
            +-----------+---------+
            | 1.1       | foo     |
            | 2.2       | bar     |
            | 3.3       | baz     |
            +-----------+---------+
            """)
        pretty = PrettyFormat(types_location=HEADER)
        parsed = pretty.parse(source)
        rendered = pretty.render(parsed)
        compare(expected=source, actual=rendered)

    def test_round_trip_explicit_parse_and_render(self) -> None:
        source = dedent("""\
            +--------------+-------------+------------+
            | start (date) | time of day | end (date) |
            +--------------+-------------+------------+
            | 27 May 04    | 09:00       | 01 Jun 04  |
            | 02 Jun 04    | 11:02       | 02 Jul 04  |
            +--------------+-------------+------------+
            """)
        pretty = PrettyFormat(
            type_parse={'date': lambda text: datetime.strptime(text, '%d %b %y').date()},
            column_parse={'time of day': lambda text: datetime.strptime(text, '%H:%M').time()},
            type_render={date: lambda d: d.strftime('%d %b %y')},
            type_names={date: 'date', time: None},
            column_render={'time of day': lambda t: t.strftime('%H:%M')},
            types_location=HEADER,
        )
        parsed = pretty.parse(source)
        compare(parsed, expected=[
            {'start': date(2004, 5, 27), 'time of day': time(9, 0), 'end': date(2004, 6, 1)},
            {'start': date(2004, 6, 2), 'time of day': time(11, 2), 'end': date(2004, 7, 2)},
        ])
        rendered = pretty.render(parsed)
        compare(expected=source, actual=rendered, show_whitespace=True)

    def test_roundtrip_types_in_row_explicit_none_name_mapping(self) -> None:
        source = dedent("""\
            +-----------+-------------+-----------+
            | start     | time of day | end       |
            +-----------+-------------+-----------+
            | date      |             | date      |
            +-----------+-------------+-----------+
            | 27 May 04 | 09:00       | 01 Jun 04 |
            | 02 Jun 04 | 11:02       | 02 Jul 04 |
            +-----------+-------------+-----------+
            """)
        pretty = PrettyFormat(
            type_parse={'date': lambda text: datetime.strptime(text, '%d %b %y').date()},
            column_parse={'time of day': lambda text: datetime.strptime(text, '%H:%M').time()},
            type_render={date: lambda d: d.strftime('%d %b %y')},
            type_names={date: 'date', time: None},
            column_render={'time of day': lambda t: t.strftime('%H:%M')},
            types_location=ROW,
        )
        parsed = pretty.parse(source)
        compare(parsed, expected=[
            {'start': date(2004, 5, 27), 'time of day': time(9, 0), 'end': date(2004, 6, 1)},
            {'start': date(2004, 6, 2), 'time of day': time(11, 2), 'end': date(2004, 7, 2)},
        ])
        rendered = pretty.render(parsed)
        compare(expected=source, actual=rendered, show_whitespace=True)

    def test_roundtrip_explicit_minimum_column_widths(self) -> None:
        source = dedent("""\
            +-------+------------+
            | x     | y          |
            +-------+------------+
            | 1.0   | foo        |
            | 2.0   | bar        |
            | 3.0   | baz        |
            +-------+------------+
            """)
        pretty = PrettyFormat(minimum_column_widths={'x': 5, 'y': 10})
        parsed = pretty.parse(source)
        rendered = pretty.render(parsed)
        compare(expected=source, actual=rendered)


class TestCSVFormat:

    def test_parse_minimal(self) -> None:
        format_ = CSVFormat()
        actual = format_.parse("".join((
            'x,y\n',
            '1,foo\n'
        )))
        compare(actual, expected=[
            {'x': 1, 'y': 'foo'},
        ])

    def test_render_minimal(self) -> None:
        format_ = CSVFormat()
        actual = format_.render([
            {'x': 1, 'y': 'foo'},
        ])
        expected = "".join((
            'x,y\r\n',
            '1,foo\r\n'
        ))
        compare(expected=expected, actual=actual, show_whitespace=True)

    def test_render_empty(self) -> None:
        format_ = CSVFormat(types_location=ROW)
        actual = format_.render([])
        compare(
            actual,
            expected=dedent("")
        )

    def test_render_with_reference(self) -> None:
        format_ = CSVFormat()
        ref = [{'z': 0, 'y': 0, 'x': 0}]
        actual = format_.render([{'x': 1, 'y': 'foo'}], ref)
        expected = "".join((
            'z,y,x\r\n',
            'None,foo,1\r\n'
        ))
        compare(expected=expected, actual=actual, show_whitespace=True)

    def test_render_with_empty_reference(self) -> None:
        format_ = CSVFormat()
        actual = format_.render([{'x': 1, 'y': 'foo'}], ref=[])
        expected = "".join((
            'x,y\r\n',
            '1,foo\r\n'
        ))
        compare(expected=expected, actual=actual, show_whitespace=True)

    def test_roundtrip_minimal(self) -> None:
        source = "".join((
            'x,y\r\n',
            '1,foo\r\n'
        ))
        format_ = CSVFormat()
        parsed = format_.parse(source)
        compare(parsed, expected=[
            {'x': 1, 'y': 'foo'},
        ])
        compare(expected=source, actual=format_.render(parsed), show_whitespace=True)

    def test_roundtrip_whitespace_in_values(self) -> None:
        source = "".join((
            'x,y\r\n',
            '1,foo\r\n',
            "2,' bar'\r\n",
            "3,'baz '\r\n",
        ))
        format_ = CSVFormat()
        parsed = format_.parse(source)
        compare(parsed, expected=[
            {'x': 1, 'y': 'foo'},
            {'x': 2, 'y': ' bar'},
            {'x': 3, 'y': 'baz '},
        ])
        rendered = format_.render(parsed)
        compare(expected=source, actual=rendered, show_whitespace=True)

    def test_roundtrip_maximal_types_in_row(self) -> None:
        source = "".join((
            'start,time of day,end\r\n',
            'date,,date\r\n',
            '27 May 04,09:00,01 Jun 04\r\n'
            '02 Jun 04,11:02,02 Jul 04\r\n'
        ))
        format_ = CSVFormat(
            type_parse={'date': lambda text: datetime.strptime(text, '%d %b %y').date()},
            column_parse={'time of day': lambda text: datetime.strptime(text, '%H:%M').time()},
            type_render={date: lambda d: d.strftime('%d %b %y')},
            type_names={date: 'date', time: None},
            column_render={'time of day': lambda t: t.strftime('%H:%M')},
            types_location=ROW,
        )
        parsed = format_.parse(source)
        compare(parsed, expected=[
            {'start': date(2004, 5, 27), 'time of day': time(9, 0), 'end': date(2004, 6, 1)},
            {'start': date(2004, 6, 2), 'time of day': time(11, 2), 'end': date(2004, 7, 2)},
        ])
        rendered = format_.render(parsed)
        compare(expected=source, actual=rendered, show_whitespace=True)

    def test_roundtrip_maximal_types_in_header(self) -> None:
        source = "".join((
            'start (date),time of day,end (date)\r\n',
            '27 May 04,09:00,01 Jun 04\r\n'
            '02 Jun 04,11:02,02 Jul 04\r\n'
        ))
        format_ = CSVFormat(
            type_parse={'date': lambda text: datetime.strptime(text, '%d %b %y').date()},
            column_parse={'time of day': lambda text: datetime.strptime(text, '%H:%M').time()},
            type_render={date: lambda d: d.strftime('%d %b %y')},
            type_names={date: 'date', time: None},
            column_render={'time of day': lambda t: t.strftime('%H:%M')},
            types_location=HEADER,
        )
        parsed = format_.parse(source)
        compare(parsed, expected=[
            {'start': date(2004, 5, 27), 'time of day': time(9, 0), 'end': date(2004, 6, 1)},
            {'start': date(2004, 6, 2), 'time of day': time(11, 2), 'end': date(2004, 7, 2)},
        ])
        rendered = format_.render(parsed)
        compare(expected=source, actual=rendered, show_whitespace=True)
