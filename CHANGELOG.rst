Changes
=======

.. currentmodule:: chide

3.1.0 (17 Jan 2024)
-------------------

- Add support for different samples of the same type using :any:`typing.Annotated`.

3.0.1 (5 Dec 2024)
------------------

- Fix location of ``py.typed`` so it is included in distributions.

3.0.0 (19 Jul 2024)
-------------------

- Python 3.11 is now the minimum supported version.

- Now strictly typed.

- Addition of :meth:`Collection.bind` and :class:`~factory.Factory` to support partial building of 
  sample objects.

- Addition of :doc:`formats <formats>`, :doc:`simplifiers <simplifiers>` and their 
  :doc:`patterns of use <patterns>`. 

- Development process refresh.

- Documentation refresh.

2.1.2 (31 Jan 2019)
-------------------

- Fix bug in :class:`Collection` occurring when sample attributes were
  not hashable.

2.1.1 (9 Jan 2019)
-------------------

-  Exclude tests from distribution.

2.1.0 (22 Nov 2018)
-------------------

-  add :meth:`~chide.Collection.attributes`.

2.0.1 (16 Jun 2016)
-------------------

- Fix nasty bug when using with :doc:`sqlalchemy <sqlalchemy:index>` where related objects could get
  added to the session even though they were never requested, as a result of
  a backref on a third model.

2.0.0 (21 Apr 2016)
-------------------

- Backwards incompatible change to split the concern for sample object
  identity out into :class:`chide.Set` and :class:`chide.sqlalchemy.Set`
  to avoid module-level :class:`~chide.Collection` instances resulting
  in cross-test pollution.

1.0.2 (15 Apr 2016)
-------------------

- Fix release faults.

1.0.0 (14 Apr 2016)
-------------------

- Initial release
