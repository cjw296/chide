|CircleCI|_ |Docs|_

.. |CircleCI| image:: https://circleci.com/gh/cjw296/chide/tree/master.svg?style=shield
.. _CircleCI: https://circleci.com/gh/cjw296/tree/chide

.. |Docs| image:: https://readthedocs.org/projects/chide/badge/?version=latest
.. _Docs: http://chide.readthedocs.org/en/latest/

chide
=====

Quickly create sample objects from data.

Chide's philosophy is to give you a super simple registry of parameters
that are needed to instantiate objects needed in your tests. You'll
hopefully only need this when you have objects that are onerous to set up
as a result of having lots of required parameters needed to create
a whole tree of objects for each test.

Here's a tiny example...

Say we have two classes that each require two parameters in order to
be instantiated:

.. code-block:: python

  class ClassOne(object):

    def __init__(self, x, y):
        self.x, self.y = x, y

  class ClassTwo(object):

    def __init__(self, a, b):
        self.a, self.b = a, b

We can set up a registry of sample values as follows:

.. code-block:: python

  from chide import Collection

  samples = Collection({
      ClassOne: {'x': 1, 'y': 2},
      ClassTwo: {'a': 1, 'b': ClassOne},
  })

Now we can quickly make sample objects:

>>> samples.make(ClassOne)
<ClassOne ...>
>>> _.x, _.y
(1, 2)

We can provide our own overrides if we want:

>>> samples.make(ClassOne, y=3)
<ClassOne ...>
>>> _.x, _.y
(1, 3)

We can also create nested trees of objects:

>>> samples.make(ClassTwo)
<ClassTwo ...>
>>> _.b
<ClassOne ...>

Why chide? Well, it's hardly mocking...
