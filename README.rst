|Travis|_ |Coveralls|_ |Docs|_

.. |Travis| image:: https://api.travis-ci.org/cjw296/chide.png?branch=master
.. _Travis: https://travis-ci.org/cjw296/chide

.. |Coveralls| image:: https://coveralls.io/repos/cjw296/chide/badge.png?branch=master
.. _Coveralls: https://coveralls.io/r/cjw296/chide?branch=master

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
