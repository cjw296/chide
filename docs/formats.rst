Formats
=======

These are an encapsulation of parsing and rendering of attributes from multiple objects
into text, such that tests are easier to read and sample objects, with many attributes
that all vary, can take up less vertical space.

A format must implement the :class:`~chide.formats.Format` protocol.
The included formats are described below.

Pretty Format
-------------

This format is based on a tabular layout of attributes that is easy to read:

.. code-block:: python

  text = """
    +-----+------+
    | x   | y    |
    +-----+------+
    | 1   | foo  |
    | 2   | bar  |
    +-----+------+
  """

The above example can be parsed as follows:

>>> from chide.formats import PrettyFormat
>>> pretty = PrettyFormat()
>>> pretty.parse(text)
[{'x': 1, 'y': 'foo'}, {'x': 2, 'y': 'bar'}]

The result can be rendered back into text:

>>> print(pretty.render([{'x': 1, 'y': 'foo'}, {'x': 2, 'y': 'bar'}]))
+---+-----+
| x | y   |
+---+-----+
| 1 | foo |
| 2 | bar |
+---+-----+
<BLANKLINE>

If the default value parsing isn't sufficient, you can specify your own:

>>> pretty = PrettyFormat(column_parse={'x': float, 'y': lambda y: y.encode()})
>>> pretty.parse(text)
[{'x': 1.0, 'y': b'foo'}, {'x': 2.0, 'y': b'bar'}]

Similar is possible for rendering:

>>> pretty = PrettyFormat(
...     column_render={'x': lambda x: str(int(x)), 'y': lambda y: y.decode()}
... )
>>> print(pretty.render([{'x': 1.0, 'y': b'foo'}, {'x': 2.0, 'y': b'bar'}]))
+---+-----+
| x | y   |
+---+-----+
| 1 | foo |
| 2 | bar |
+---+-----+
<BLANKLINE>

For more control over parsing and rendering of specific types, see :ref:`pretty-type-info`.

If you need to ensure columns are present and are in a particular order, you can pass in
a reference for :meth:`~chide.formats.PrettyFormat.render` to use:

>>> data = [{'y': 'foo', 'x': 1}, {'y': 'bar', 'x': 2}]
>>> print(PrettyFormat().render(data, ref=[{'x': True, 'y': True, 'z': True}]))
+------+------+------+
| x    | y    | z    |
+------+------+------+
| 1    | foo  | None |
| 2    | bar  | None |
+------+------+------+
<BLANKLINE>

Controlling column widths
~~~~~~~~~~~~~~~~~~~~~~~~~
The padding around values can be controlled with the ``padding`` parameter:

>>> data = [{'y': 'foo', 'x': 1}, {'y': 'bar', 'x': 2}]
>>> print(PrettyFormat(padding=0).render(data))
+---+-+
|y  |x|
+---+-+
|foo|1|
|bar|2|
+---+-+
<BLANKLINE>
>>> print(PrettyFormat(padding=3).render(data))
+---------+-------+
|   y     |   x   |
+---------+-------+
|   foo   |   1   |
|   bar   |   2   |
+---------+-------+
<BLANKLINE>

If you are expecting to add more rows later than may have wider values, you
can minimise differences when doing so by specifying minimum column widths:

>>> data = [{'y': 'foo', 'x': 1}, {'y': 'bar', 'x': 2}]
>>> print(PrettyFormat(minimum_column_widths={'y': 10}).render(data))
+------------+---+
| y          | x |
+------------+---+
| foo        | 1 |
| bar        | 2 |
+------------+---+
<BLANKLINE>

If you are making assertions about an expected table versus what was actually found,
it can make differences easier to spot if you pass in a reference that is made by parsing
the rendering of your expected data; this will ensure all columns are present, in the same
order and have the same width, where possible:

>>> from chide.formats import PrettyFormat
>>> from testfixtures import compare
>>> expected = [{'y': 'f', 'x': 1, 'z': True}, {'y': 'bar', 'x': 2, 'z': False}]
>>> actual = [{'y': 'f', 'x': 1, 'z': True}, {'y': 'b', 'x': 2}]
>>> pretty = PrettyFormat()
>>> expected_text = pretty.render(expected)
>>> expected_ref = pretty.parse(expected_text)
>>> compare(expected=expected_text, actual=pretty.render(actual, ref=expected_ref))
Traceback (most recent call last):
...
AssertionError: 
--- expected
+++ actual
@@ -2,6 +2,6 @@
 | y   | x | z     |
 +-----+---+-------+
 | f   | 1 | True  |
-| bar | 2 | False |
+| b   | 2 | None  |
 +-----+---+-------+
<BLANKLINE>

.. _pretty-type-info:

Including type information
~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, types of cells are inferred from their values. So, given:

.. code-block:: python

  text = """
    +-----+-------+
    | x   | y     |
    +-----+-------+
    | 1   | ' a ' |
    | 2   | 2.0   |
    +-----+-------+
  """

We get the following list of attributes:

>>> results = PrettyFormat().parse(text)
>>> results
[{'x': 1, 'y': ' a '}, {'x': 2, 'y': 2.0}]

When rendering, a similar approach is taken:

>>> print(PrettyFormat().render(results))
+---+-------+
| x | y     |
+---+-------+
| 1 | ' a ' |
| 2 | 2.0   |
+---+-------+
<BLANKLINE>

We saw above how type parsing and rendering could be specified for columns by their name,
but this information can also be explicitly included in parenthesis after the column headings:

.. code-block:: python

  text = """
    +-----------+---------+
    | x (float) | y (str) |
    +-----------+---------+
    | 1         | ' a '   |
    | 2         | 2.0     |
    +-----------+---------+
  """

This can be parsed as follows:

>>> from chide.formats import PrettyFormat, HEADER
>>> pretty = PrettyFormat(types_location=HEADER)
>>> pretty.parse(text)
[{'x': 1.0, 'y': "' a '"}, {'x': 2.0, 'y': '2.0'}]

The same format can also be used to render lists of attributes, including the types,
in the same way:

>>> print(pretty.render([{'x': 1.0, 'y': "' a '"}, {'x': 2.0, 'y': '2.0'}]))
+-----------+---------+
| x (float) | y (str) |
+-----------+---------+
| 1.0       | ' a '   |
| 2.0       | 2.0     |
+-----------+---------+
<BLANKLINE>

If it makes more sense, type information can instead be included in its own row:

.. code-block:: python

  text = """
    +-----+-------+
    | x   | y     |
    +-----+-------+
    |float| str   |
    +-----+-------+
    | 1   | ' a ' |
    | 2   | 2.0   |
    +-----+-------+
  """

This can be parsed as follows:

>>> from chide.formats import PrettyFormat, ROW
>>> pretty = PrettyFormat(types_location=ROW)
>>> pretty.parse(text)
[{'x': 1.0, 'y': "' a '"}, {'x': 2.0, 'y': '2.0'}]

Again, the same format can also be used to render lists of attributes:

>>> print(pretty.render([{'x': 1.0, 'y': "' a '"}, {'x': 2.0, 'y': '2.0'}]))
+-------+-------+
| x     | y     |
+-------+-------+
| float | str   |
+-------+-------+
| 1.0   | ' a ' |
| 2.0   | 2.0   |
+-------+-------+
<BLANKLINE>

Where types are not simple built-in types, for example:

.. code-block:: python

  text = """
    +-----------+
    | start     |
    +-----------+
    | DD MMM YY |
    +-----------+
    | 27 May 04 |
    | 02 Jun 04 |
    +-----------+
  """

The type name specified in the row or column heading can be mapped to a parsing function as follows:

>>> from datetime import datetime
>>> pretty = PrettyFormat(
...     types_location=ROW, 
...     type_parse={'DD MMM YY': lambda text: datetime.strptime(text, '%d %b %y').date()}
... )
>>> pretty.parse(text)
[{'start': datetime.date(2004, 5, 27)}, {'start': datetime.date(2004, 6, 2)}]

The inverse is true for rendering, where the object type can be passed through to a rendering
function. The name shown in the row or columns heading and also be mapped from the object type
as follows:


>>> from datetime import date
>>> data = [{'start': date(2004, 5, 27)}, {'start': date(2004, 6, 2)}]
>>> pretty = PrettyFormat(
...     types_location=ROW, 
...     type_render={date: lambda d: d.strftime('%d %b %y')},
...     type_names={date: 'DD MMM YY'}
... )
>>> print(pretty.render(data))
+-----------+
| start     |
+-----------+
| DD MMM YY |
+-----------+
| 27 May 04 |
| 02 Jun 04 |
+-----------+
<BLANKLINE>

CSV Format
----------

This format is based on the well known comma separated value format:

.. code-block:: python

  from textwrap import dedent
  text = dedent("""\
    x,y
    1,foo
    2,bar
  """)

The above example can be parsed as follows:

>>> from chide.formats import CSVFormat
>>> pretty = CSVFormat()
>>> pretty.parse(text)
[{'x': 1, 'y': 'foo'}, {'x': 2, 'y': 'bar'}]

The result can be rendered back into text:

.. invisible-code-block: python

    _print = print
    def print(text):
        # \r is pretty annoying to deal with in docstring, but part of the default CSV format
        return _print(text.replace('\r', ''))

>>> print(pretty.render([{'x': 1, 'y': 'foo'}, {'x': 2, 'y': 'bar'}]))
x,y
1,foo
2,bar
<BLANKLINE>

If the default value parsing isn't sufficient, you can specify your own:

>>> pretty = CSVFormat(column_parse={'x': float, 'y': lambda y: y.encode()})
>>> pretty.parse(text)
[{'x': 1.0, 'y': b'foo'}, {'x': 2.0, 'y': b'bar'}]

Similar is possible for rendering:

>>> pretty = CSVFormat(
...     column_render={'x': lambda x: str(int(x)), 'y': lambda y: y.decode()}
... )
>>> print(pretty.render([{'x': 1.0, 'y': b'foo'}, {'x': 2.0, 'y': b'bar'}]))
x,y
1,foo
2,bar
<BLANKLINE>

For more control over parsing and rendering of specific types, see :ref:`csv-type-info`.

If you need to ensure columns are present and are in a particular order, you can pass in
a reference for :meth:`~chide.formats.CSVFormat.render` to use:

>>> data = [{'y': 'foo', 'x': 1}, {'y': 'bar', 'x': 2}]
>>> print(CSVFormat().render(data, ref=[{'x': True, 'y': True, 'z': True}]))
x,y,z
1,foo,None
2,bar,None
<BLANKLINE>

.. _csv-type-info:

Including type information
~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, types of cells are inferred from their values. So, given:

.. code-block:: python

  from textwrap import dedent
  text = dedent("""\
    x,y
    1,' a '
    2,2.0
  """)

We get the following list of attributes:

>>> results = CSVFormat().parse(text)
>>> results
[{'x': 1, 'y': ' a '}, {'x': 2, 'y': 2.0}]

When rendering, a similar approach is taken:

>>> print(CSVFormat().render(results))
x,y
1,' a '
2,2.0
<BLANKLINE>

We saw above how type parsing and rendering could be specified for columns by their name,
but this information can also be explicitly included in parenthesis after the column headings:

.. code-block:: python

  from textwrap import dedent
  text = dedent("""\
    x (float),y (str)
    1,' a '
    2,2.0
  """)

This can be parsed as follows:

>>> from chide.formats import CSVFormat, HEADER
>>> csv = CSVFormat(types_location=HEADER)
>>> csv.parse(text)
[{'x': 1.0, 'y': "' a '"}, {'x': 2.0, 'y': '2.0'}]

The same format can also be used to render lists of attributes, including the types,
in the same way:

>>> print(csv.render([{'x': 1.0, 'y': "' a '"}, {'x': 2.0, 'y': '2.0'}]))
x (float),y (str)
1.0,' a '
2.0,2.0
<BLANKLINE>

If it makes more sense, type information can instead be included in its own row:

.. code-block:: python

  from textwrap import dedent
  text = dedent("""\
    x,y
    float,str
    1,' a '
    2,2.0
  """)

This can be parsed as follows:

>>> from chide.formats import CSVFormat, ROW
>>> csv = CSVFormat(types_location=ROW)
>>> csv.parse(text)
[{'x': 1.0, 'y': "' a '"}, {'x': 2.0, 'y': '2.0'}]

Again, the same format can also be used to render lists of attributes:

>>> print(csv.render([{'x': 1.0, 'y': "' a '"}, {'x': 2.0, 'y': '2.0'}]))
x,y
float,str
1.0,' a '
2.0,2.0
<BLANKLINE>

Where types are not simple built-in types, for example:

.. code-block:: python

  from textwrap import dedent
  text = dedent("""\
    start
    DD MMM YY
    27 May 04
    02 Jun 04
  """)

The type name specified in the row or column heading can be mapped to a parsing function as follows:

>>> from datetime import datetime
>>> csv = CSVFormat(
...     types_location=ROW, 
...     type_parse={'DD MMM YY': lambda text: datetime.strptime(text, '%d %b %y').date()}
... )
>>> csv.parse(text)
[{'start': datetime.date(2004, 5, 27)}, {'start': datetime.date(2004, 6, 2)}]

The inverse is true for rendering, where the object type can be passed through to a rendering
function. The name shown in the row or columns heading and also be mapped from the object type
as follows:


>>> from datetime import date
>>> data = [{'start': date(2004, 5, 27)}, {'start': date(2004, 6, 2)}]
>>> csv = CSVFormat(
...     types_location=ROW, 
...     type_render={date: lambda d: d.strftime('%d %b %y')},
...     type_names={date: 'DD MMM YY'}
... )
>>> print(csv.render(data))
start
DD MMM YY
27 May 04
02 Jun 04
<BLANKLINE>
