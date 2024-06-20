import builtins
import csv
import re
from ast import literal_eval
from enum import Enum, auto
from io import StringIO
from itertools import zip_longest
from textwrap import dedent
from typing import Protocol, Iterable, Type, Callable, Any, TypeVar, TypeAlias, Mapping

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

    def _parse(self, text: str, lexer: Callable[[str], Iterable[Iterable[str]]]) -> list[Attrs]:
        parsed = []
        columns: list[str] | None = None
        types_row_handled = self.types_location is not ROW
        types_row_next = False
        for parts in lexer(text):

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


class Widths(dict[str, int]):

    def handle(self, item: Mapping[str, str | int]) -> None:
        for column, text_or_width in item.items():
            width = text_or_width if isinstance(text_or_width, int) else len(text_or_width)
            self[column] = max(width, self.get(column, 0))


class RenderedRows(list[dict[str, str]]):
    columns: list[str] | None = None
    types: dict[str, str] | None = None
    header: dict[str, str]

    def __init__(
            self, attrs: Iterable[Attrs], format_: 'TabularFormat', columns: list[str] | None = None
    ) -> None:
        super().__init__()
        for attrs_ in attrs:
            if self.columns is None:
                attr_columns = list(attrs_.keys())
                if columns is None:
                    self.columns = attr_columns
                else:
                    self.columns = columns + [c for c in attr_columns if c not in columns]
            if self.types is None:
                self.types = {}
                for column, value in attrs_.items():
                    type_ = type(value)
                    type_name = format_.type_names.get(type_, type(value).__name__)
                    self.types[column] = type_name or ''
            row = {}
            for column in self.columns:
                value = attrs_.get(column)
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
                if self.types is not None and (type_name := self.types.get(column)) is not None:
                    if format_.types_location is HEADER and type_name:
                        text = f'{text} ({type_name})'
                self.header[column] = text

    def update(self, widths: Widths, types_location: TypeLocation | None) -> None:
        if self.header:
            widths.handle(self.header)
        if self.types is not None and types_location is ROW:
            widths.handle(self.types)
        for row in self:
            widths.handle(row)


class PrettyLexer:

    def __init__(self, padding: int):
        self.widths: list[int] = []
        self.padding = padding

    def __call__(self, text: str) -> Iterable[list[str]]:
        padding_text = ' ' * self.padding
        padding_size = self.padding * 2
        for line in dedent(text).splitlines():
            line = line.strip()
            if not line or line.startswith('+'):
                continue
            parts = line.split('|')[1:-1]
            widths = []
            for part in parts:
                width = len(part)
                if (
                        width >= padding_size and
                        part[:self.padding] == padding_text and
                        part[-self.padding:] == padding_text
                ):
                    width -= padding_size
                widths.append(width)
            if self.widths:
                self.widths = [max(w, w_) for w, w_ in zip_longest(self.widths, widths)]
            else:
                self.widths = widths
            yield [p.strip() for p in parts]


class PrettyParsed(list[Attrs]):
    def __init__(self, attrs: list[Attrs], widths: list[int]) -> None:
        super().__init__(attrs)
        self.widths: dict[str, int] = {}
        if attrs:
            for columns, width in zip(attrs[0].keys(), widths):
                self.widths[columns] = width


class PrettyRenderedRows(list[str]):

    def __init__(self, widths: Widths, padding: int) -> None:
        super().__init__()
        self.divider = ''.join('+'+'-'*(widths[column]+padding*2) for column in widths)+'+\n'
        pad = padding*' '
        self.templates = {c: f'|{pad}{{:{w}}}{pad}' for c, w in widths.items()}
        self.widths = widths

    def add_divider(self) -> None:
        self.append(self.divider)

    def add_row(self, row: dict[str, str]) -> None:
        parts = (self.templates[column].format(value) for column, value in row.items())
        self.append(''.join(parts) + '|\n')

    def text(self) -> str:
        return ''.join(self)


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
            padding: int = 1,
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
        self.padding = padding

    def parse(self, text: str) -> PrettyParsed:
        lexer = PrettyLexer(self.padding)
        rows = self._parse(text, lexer)
        return PrettyParsed(rows, lexer.widths)

    def render(self, attrs: Iterable[Attrs], ref: list[Attrs] | PrettyParsed | None = None) -> str:
        columns = None
        widths = Widths(self.minimum_column_widths)

        if ref is not None:
            ref_widths = getattr(ref, 'widths', None)
            if ref_widths is None:
                ref_rows = RenderedRows(ref, self)
                ref_rows.update(widths, self.types_location)
                columns = ref_rows.columns
            else:
                widths.handle(ref_widths)
                columns = list(ref_widths)

        rows = RenderedRows(attrs, self, columns)
        rows.update(widths, self.types_location)

        rendered = PrettyRenderedRows(widths, self.padding)
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

    def parse(self, text: str) -> list[Attrs]:
        return self._parse(text, lambda text: [row for row in csv.reader(StringIO(text))])

    def render(self, attrs: Iterable[Attrs], ref: list[Attrs] | None = None) -> str:
        columns = None
        if ref:
            columns = list(ref[0])

        rows = RenderedRows(attrs, self, columns)
        text = StringIO()
        writer = csv.writer(text)

        if rows.header:
            writer.writerow(rows.header.values())
        if rows.types is not None and self.types_location is ROW:
            writer.writerow(rows.types.values())
        for row in rows:
            writer.writerow(row.values())

        return text.getvalue()
