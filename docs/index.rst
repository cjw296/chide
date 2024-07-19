.. include:: ../README.rst

Documentation
~~~~~~~~~~~~~

If you're looking to create simple sample objects, read the :doc:`collections` documentation.

If your sample objects have relationships between them, have a look at :doc:`sets`.
There is a :ref:`specialised set implementation <sqlalchemy-set>` for use with SQLAlchemy.

If you need to deal with multiple sample objects that have many different attribute values,
read about :doc:`formats`.

If you need to make assertions about many objects and want to use :doc:`formats <formats>`
to do so, you will probably want to use :doc:`simplifiers`.
There are specialised simplifiers for SQLAlchemy :ref:`rows <sqlalchemy-row-simplifier>` and
:ref:`ORM-mapped objects <sqlalchemy-mapped-simplifier>`.

If you're interested in seeing patterns of using the above in "real world" ways,
see :doc:`patterns`.

.. toctree::
   :maxdepth: 2

   collections.rst
   sets.rst
   formats.rst
   simplifiers.rst
   sqlalchemy.rst
   patterns.rst
   api.rst
   development.rst
   changes.rst
   license.rst


Why chide?
~~~~~~~~~~

Well, it's hardly mocking...

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

