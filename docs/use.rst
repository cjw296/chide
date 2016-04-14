Usage
=====

Here's how to simply and quickly create sample objects using :mod:`chide`.
For the examples, these two classes will be used:

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

These can also be overridden with another sample object:

>>> samples.make(ClassTwo, b=samples.make(ClassOne, x=-1))
<ClassTwo ...>
>>> _.b.x
-1

They can also be directly overridden with an appropriate instance:

>>> samples.make(ClassTwo, b=ClassOne(11, 3))
<ClassTwo ...>
>>> _.b.x, _.b.y
(11, 3)
