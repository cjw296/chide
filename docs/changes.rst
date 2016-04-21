Changes
=======

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
