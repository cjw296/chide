Changes
=======

2.1.1 (9 Jan 2019)
-------------------

-  Exclude tests from distribution.

2.1.0 (22 Nov 2018)
-------------------

-  add :meth:`~chide.Collection.attributes`.

2.0.1 (16 Jun 2016)
-------------------

- Fix nasty bug when using with :mod:`sqlalchemy` where related objects could get
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
