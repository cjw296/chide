Collections
===========

.. py:currentmodule:: chide

Collections are the starting point for creating sample objects when using :mod:`chide`.
They contain sample attributes for each of the types that have been added to them
and can be used to create sample objects of those types that will have the sample
attributes.

For the examples below, these two classes will be used:

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

Creating sample objects
-----------------------

We can set up a collection of sample values as follows:

.. code-block:: python

  from chide import Collection

  samples = Collection({
      ClassOne: {'x': 1, 'y': 2},
      ClassTwo: {'a': 1, 'b': ClassOne},
  })

Now we can quickly make sample objects:

>>> samples.make(ClassOne)
ClassOne(x=1, y=2)

We can also add sample objects directly to the registry:

.. code-block:: python

    more_samples = Collection()
    more_samples.add(ClassOne(x=3, y=4))

The attributes extracted will then be used to create sample objects of that type:

>>> obj1 = more_samples.make(ClassOne)
>>> obj2 = more_samples.make(ClassOne)
>>> obj1
ClassOne(x=3, y=4)
>>> obj2
ClassOne(x=3, y=4)
>>> obj1 is obj2
False

We can provide our own overrides if we want:

>>> samples.make(ClassOne, y=3)
ClassOne(x=1, y=3)

We can also create nested trees of objects:

>>> samples.make(ClassTwo)
ClassTwo(a=1, b=ClassOne(x=1, y=2))

These can also be overridden with another sample object:

>>> samples.make(ClassTwo, b=samples.make(ClassOne, x=-1))
ClassTwo(a=1, b=ClassOne(x=-1, y=2))

They can also be directly overridden with an appropriate instance:

>>> samples.make(ClassTwo, b=ClassOne(11, 3))
ClassTwo(a=1, b=ClassOne(x=11, y=3))

Creating attributes for objects
--------------------------------

Given this collection:

.. code-block:: python

  from chide import Collection

  samples = Collection({
      ClassOne: {'x': 1, 'y': 2},
      ClassTwo: {'a': 1, 'b': ClassOne},
  })

We can also create attributes to make a sample object:

>>> attrs = samples.attributes(ClassOne)
>>> attrs['x']
1
>>> attrs['y']
2

>>> attrs = samples.attributes(ClassTwo)
>>> attrs['a']
1
>>> attrs['b']
ClassOne(x=1, y=2)

Partially creating objects
--------------------------

Given this collection:

.. code-block:: python

  from chide import Collection

  samples = Collection()
  samples.add(ClassOne(x=1, y=2))

If we need to create several objects that have a different value from the sample,
we can bind this into a factory:

>>> factory = samples.bind(ClassOne, x=4)

This can then be used to create sample objects with less duplicated code:

>>> factory.make()
ClassOne(x=4, y=2)
>>> factory.make(y=3)
ClassOne(x=4, y=3)

Factories can also be used to provide attributes:

>>> factory.attributes()
{'x': 4, 'y': 2}

Further attributes can be bound into a factory to create a new, more specialised, factory:

>>> another_factory = factory.bind(y=5)
>>> another_factory.make()
ClassOne(x=4, y=5)

Generic classes and types
-------------------------

When working with generic classes such as this:

.. code-block:: python

    from typing import TypeVar, Generic

    T = TypeVar('T')

    class Sample(Generic[T]):
        def __init__(self, value: T) -> None:
            self.value = value

        def __repr__(self) -> str:
            return f'<Sample: {self.value!r}>'

        @classmethod
        def create(cls, value: T) -> 'Sample[T]':
            return cls(value)

You can add them to collections via their attributes:

>>> collection = Collection({Sample[int]: {'value': 1}})
>>> collection.make(Sample[int])
<Sample: 1>

You can also add sample objects:

>>> collection.add(Sample[str]('hello'))
>>> collection.make(Sample[str])
<Sample: 'hello'>

There is, however, an intricacy with parameterized types;
instantiating them using the parameterized type alias will result in the instance having an
``__orig_class__`` attribute:

>>> Sample[int](1).__orig_class__
Sample[int]

But, if you instantiate them via the class alone, such as in the class method above, they will
not:

>>> Sample.create(1).__orig_class__
Traceback (most recent call last):
...
AttributeError: 'Sample' object has no attribute '__orig_class__'...

If you need all or most of your sample objects to be without this attribute, then
you can override the constructor to use when adding a sample:

>>> collection = Collection()
>>> collection.add(Sample[str]('hello'), constructor=Sample)
>>> collection.make(Sample[str])
<Sample: 'hello'>
>>> _.__orig_class__
Traceback (most recent call last):
...
AttributeError: 'Sample' object has no attribute '__orig_class__'...

If you're passing an attribute mapping to the :class:`Collection` constructor or need some samples
with the ``__orig_class__`` and some without, then you can use this pattern with
:meth:`~Collection.bind` and :meth:`~chide.factory.Factory.make`:

>>> collection = Collection({Sample[int]: {'value': 1}})
>>> collection.make(Sample[int])
<Sample: 1>
>>> _.__orig_class__
Sample[int]
>>> collection.bind(Sample[int]).make(Sample)
<Sample: 1>
>>> _.__orig_class__
Traceback (most recent call last):
...
AttributeError: 'Sample' object has no attribute '__orig_class__'...
