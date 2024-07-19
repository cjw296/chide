Chide
=====

|CircleCI|_ |Docs|_

.. |CircleCI| image:: https://circleci.com/gh/cjw296/chide/tree/master.svg?style=shield
.. _CircleCI: https://circleci.com/gh/cjw296/tree/chide

.. |Docs| image:: https://readthedocs.org/projects/chide/badge/?version=latest
.. _Docs: http://chide.readthedocs.org/en/latest/

Quickly create and compare sample objects.

Chide's philosophy is to give you a simple registry of parameters
needed to instantiate objects for your tests.
There's also support for simplifying objects down to mappings of their attributes
for easier comparison and rendering, along with parsing and rendering of formats
for inserting or asserting about multiple objects that are naturally tabular.

Quickstart
~~~~~~~~~~

Say we have two classes that each require two parameters in order to
be instantiated:

.. code-block:: python

  from dataclasses import dataclass

  @dataclass
  class ClassOne:
    x: int
    y: int

  @dataclass
  class ClassTwo:
    a: int
    b: ClassOne

We can set up a registry of sample values as follows:

.. code-block:: python

  from chide import Collection

  samples = Collection({
      ClassOne: {'x': 1, 'y': 2},
      ClassTwo: {'a': 1, 'b': ClassOne},
  })

Now we can quickly make sample objects:

>>> samples.make(ClassOne)
ClassOne(x=1, y=2)

We can provide our own overrides if we want:

>>> samples.make(ClassOne, y=3)
ClassOne(x=1, y=3)

We can also create nested trees of objects:

>>> samples.make(ClassTwo)
ClassTwo(a=1, b=ClassOne(x=1, y=2))
