Simplifiers
===========

When making assertions about the structure of data or parsing and rendering with 
different :doc:`formats <formats>`, it can be easier if each datum involved is a simple 
:class:`dict` mapping names to their values, and the data is presented as a :class:`list`
of these mappings.

The :class:`~chide.simplifiers.Simplifier` protocol provides a way to take objects of any 
type and turn them into just such mappings or lists of mappings.

An :class:`~chide.simplifiers.ObjectSimplifier` is included that can be used to simplify most
Python objects:

  >>> from chide.simplifiers import ObjectSimplifier
  >>> simplifier = ObjectSimplifier()

This includes dataclasses:

.. code-block:: python

  from dataclasses import dataclass

  @dataclass
  class Point:
      x: int
      y: int

>>> simplifier.one(Point(1, 2))
{'x': 1, 'y': 2}

Objects that store their attributes in slots can also be simplified:

.. code-block:: python

  from dataclasses import dataclass

  class Small:
      __slots__ = 'a', 'b'

>>> small = Small()
>>> simplifier.one(small)
{}
>>> small.a = 'a thing'
>>> small.b = 'b thing'
>>> simplifier.one(small)
{'a': 'a thing', 'b': 'b thing'}

If you have an iterable of objects, these can all be simplified in one go:

.. code-block:: python

  def objects():
      yield Point(42, 13)
      small = Small()
      small.a = 0.001
      yield small

>>> simplifier.many(objects())
[{'x': 42, 'y': 13}, {'a': 0.001}]

Simplifiers for SQLAlchemy :ref:`rows <sqlalchemy-row-simplifier>` and
:ref:`ORM-mapped objects <sqlalchemy-mapped-simplifier>` are also included.
