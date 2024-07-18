Sets
====

In some circumstances, you may need a set of related objects
where the objects have a notion of an identifier, and only one
object of each type with a given identifier can exist. Here's an
example:

.. code-block:: python

  class Person(object):
      def __init__(self, name, address):
          self.name = name
          self.address = address

  class Address(object):
      seen = set()
      def __init__(self, value):
          if value in self.seen:
              raise Exception(value)
          self.seen.add(value)
          self.value = value

So, given that there can be multiple people but each address can only
be instantiated once we want all people used in tests, by default, to be at
the same address. We can do this using a :class:`~chide.Set` and an ``identify``
function as follows:

.. code-block:: python

  from chide import Collection, Set

  data = Collection({
      Person: {'name': 'Fred', 'address': Address},
      Address: {'value': 'some place in the clouds'},
  })

  def identify(type_, attrs):
      if type_ is Address:
          return attrs['value']

  samples = Set(data, identify)

Now, we can create multiple sample people without having to specify their
address:

>>> person1 = samples.get(Person, name='Chris')
>>> person2 = samples.get(Person, name='Kirsty')

They both just end up at the same address:

>>> person1.address.value
'some place in the clouds'
>>> person2.address.value
'some place in the clouds'
>>> person1.address is person2.address
True

We can still create people with different addresses:

>>> person3 = samples.get(Person, name='Fred', address=Address('elsewhere'))
>>> person3.address.value
'elsewhere'

The :class:`~chide.Set` can also be used to make sure that only one of each
address is used:

>>> person4 = samples.get(Person, name='Bob', address=samples.get(Address, value='here'))
>>> person5 = samples.get(Person, name='Joe', address=samples.get(Address, value='here'))

This way, we don't have to manually ensure that only one address for "here"
exists.

You'll notice that we can still get multiple people with the same name from the
:class:`~chide.Set`:

>>> person6 = samples.get(Person, name='Chris')
>>> person1 is person6
False

This because the :func:`identify` function above returns ``None`` for all types
other than :class:`Address`. Returning ``None`` from :func:`identify` is the
way to indicate that a new object should be returned, regardless of the
attributes it has.
