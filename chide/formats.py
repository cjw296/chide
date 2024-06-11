import builtins
import re
from ast import literal_eval
from enum import Enum, auto
from io import StringIO
from textwrap import dedent
from typing import Protocol, Iterable, Type, Callable, Any, TypeVar, TypeAlias
import csv

from .typing import Attrs


T = TypeVar('T')


class Format(Protocol):

    def parse(self, text: str) -> list[Attrs]:
        ...

    def render(self, attrs: Iterable[Attrs]) -> str:
        ...


ValueParse = Callable[[str], Any]
ValueRender = Callable[[Any], str]


ParseMapping: TypeAlias = dict[str, ValueParse]
TypeRenderMapping: TypeAlias = dict[Type[Any], ValueRender]
TypeNameMapping: TypeAlias = dict[Type[Any], str | None]
ColumnRenderMapping: TypeAlias = dict[str, ValueRender]


class Widths(dict[str, int]):

    def handle(self, column: str, value: str) -> None:
        self[column] = max(len(value), self.get(column, 0))


class PrettyRenderedRows(list[str]):

    def __init__(self, widths: Widths) -> None:
        super().__init__()
        self.divider = ''.join('+'+'-'*(widths[column]+2) for column in widths)+'+\n'
        self.templates = {c: f'| {{:{w}}} ' for c, w in widths.items()}
        self.widths = widths

    def add_divider(self) -> None:
        self.append(self.divider)

    def add_row(self, row: dict[str, str]) -> None:
        parts = (self.templates[column].format(value) for column, value in row.items())
        self.append(''.join(parts) + '|\n')

    def text(self) -> str:
        return ''.join(self)


def default_parse(text: str) -> Any:
    try:
        return literal_eval(text)
    except SyntaxError:
        return text


NEEDS_REPR = re.compile(r'^(\s.+|.+\s)$')


def default_render(value: Any) -> str:
    rendered = str(value)
    if NEEDS_REPR.match(rendered):
        rendered = repr(rendered)
    return rendered


class TypeLocation(Enum):
    HEADER = auto()
    ROW = auto()


HEADER = TypeLocation.HEADER
ROW = TypeLocation.ROW


class TabularFormat(Format):

    header_type_pattern = re.compile(r'([^ (]+) *\((.+)\) *')

    def __init__(
            self,
            type_parse: ParseMapping | None = None,
            default_type_parse: ValueParse = default_parse,
            column_parse: ParseMapping | None = None,
            type_render: TypeRenderMapping | None = None,
            type_names: TypeNameMapping | None = None,
            default_type_render: ValueRender = default_render,
            column_render: ColumnRenderMapping | None = None,
            types_location: TypeLocation | None = None,
            minimum_column_widths: dict[str, int] | None = None,
    ) -> None:
        self.type_parse: ParseMapping = type_parse or {}
        self.column_parse: ParseMapping = column_parse or {}
        self.default_type_parse = default_type_parse
        self.type_render: TypeRenderMapping = type_render or {}
        self.type_names: TypeNameMapping = type_names or {}
        self.column_render: ColumnRenderMapping = column_render or {}
        self.default_type_render = default_type_render
        self.types_location = types_location
        self.minimum_column_widths: dict[str, int] = minimum_column_widths or {}

    def _resolve_type_names(self, type_names: dict[str, str]) -> None:
        for column, name in type_names.items():
            if name:
                if name not in self.column_parse:
                    handler = self.type_parse.get(name)
                    if handler is None:
                        handler = getattr(builtins, name)
                    self.column_parse[column] = handler

    def text_to_tuples(self, text: str) -> Iterable[Iterable[str]]:
        raise NotImplementedError

    def parse(self, text: str) -> list[Attrs]:
        parsed = []
        columns: list[str] | None = None
        types_row_handled = self.types_location is not ROW
        types_row_next = False
        for parts in self.text_to_tuples(text):

            if columns is not None and not types_row_handled:
                types_row_next = True

            if columns is None:
                columns = []
                type_names = {}
                for c in parts:
                    if (
                            self.types_location is HEADER
                            and (match := self.header_type_pattern.match(c))
                    ):
                        column, t = match.groups()
                        type_names[column] = t
                    else:
                        column = c
                    columns.append(column)
                self._resolve_type_names(type_names)
            elif types_row_next:
                self._resolve_type_names(type_names={c: t for c, t in zip(columns, parts)})
                types_row_handled = True
                types_row_next = False
            else:
                row = {}
                for column, value in zip(columns, parts):
                    try:
                        handler = self.column_parse.get(column, self.default_type_parse)
                        value = handler(value)
                    except ValueError:
                        pass
                    row[column] = value
                parsed.append(row)
        return parsed


class RenderedRows(list[dict[str, str]]):
    columns: list[str] | None = None
    types: dict[str, str] | None = None
    header: dict[str, str]

    def __init__(self, attrs: Iterable[Attrs], format_: 'TabularFormat') -> None:
        super().__init__()
        for attrs_ in attrs:
            if self.columns is None:
                self.columns = list(attrs_.keys())
            if self.types is None:
                self.types = {}
                for column, value in attrs_.items():
                    type_ = type(value)
                    type_name = format_.type_names.get(type_, type(value).__name__)
                    self.types[column] = type_name or ''
            row = {}
            for column, value in attrs_.items():
                handler = format_.column_render.get(column)
                if handler is None:
                    handler = format_.type_render.get(type(value), format_.default_type_render)
                text = handler(value)
                row[column] = text
            self.append(row)

        self.header = {}
        if self.columns is not None:
            for column in self.columns:
                text = column
                if self.types is not None:
                    type_name = self.types[column]
                    if format_.types_location is HEADER and type_name:
                        text = f'{text} ({type_name})'
                self.header[column] = text


class PrettyFormat(TabularFormat):

    def __init__(
            self,
            type_parse: ParseMapping | None = None,
            default_type_parse: ValueParse = default_parse,
            column_parse: ParseMapping | None = None,
            type_render: TypeRenderMapping | None = None,
            type_names: TypeNameMapping | None = None,
            default_type_render: ValueRender = default_render,
            column_render: ColumnRenderMapping | None = None,
            types_location: TypeLocation | None = None,
            minimum_column_widths: dict[str, int] | None = None,
    ) -> None:
        super().__init__(
            type_parse,
            default_type_parse,
            column_parse,
            type_render,
            type_names,
            default_type_render,
            column_render,
            types_location,
        )
        self.minimum_column_widths: dict[str, int] = minimum_column_widths or {}

    def text_to_tuples(self, text: str) -> Iterable[list[str]]:
        for line in dedent(text).splitlines():
            line = line.strip()
            if not line or line.startswith('+'):
                continue
            yield [p.strip() for p in line.split('|')[1:-1]]

    def render(self, attrs: Iterable[Attrs]) -> str:
        widths = Widths(self.minimum_column_widths)
        rows = RenderedRows(attrs, self)

        if rows.header:
            for column, text in rows.header.items():
                widths.handle(column, text)
        if rows.types is not None and self.types_location is ROW:
            for column, text in rows.types.items():
                widths.handle(column, text)
        for row in rows:
            for column, text in row.items():
                widths.handle(column, text)

        rendered = PrettyRenderedRows(widths)
        rendered.add_divider()
        if rows.header:
            rendered.add_row(rows.header)
            rendered.add_divider()
        if rows.types is not None and self.types_location is ROW:
            rendered.add_row(rows.types)
            rendered.add_divider()
        for row in rows:
            rendered.add_row(row)
        rendered.add_divider()

        return rendered.text()


class CSVFormat(TabularFormat):

    def text_to_tuples(self, text: str) -> Iterable[list[str]]:
        return [row for row in csv.reader(StringIO(text))]

    def render(self, attrs: Iterable[Attrs]) -> str:
        rows = RenderedRows(attrs, self)
        text = StringIO()
        writer = csv.writer(text)

        if rows.header:
            writer.writerow(rows.header.values())
        if rows.types is not None and self.types_location is ROW:
            writer.writerow(rows.types.values())
        for row in rows:
            writer.writerow(row.values())

        return text.getvalue()
