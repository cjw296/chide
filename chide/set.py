class Set(dict):
    """
    A collection of sample objects where only one object with
    a given identity may exist at one time.

    :param collection:
        The :class:`~chide.Collection` instance used to create sample objects
        when necessary.

    :param identify:
        A callable that takes `type_` and `attrs` parameters.

        `type_`, usually a class, is the type of the
        sample object being requested.

        `attrs` is a :class:`dict` of the attributes being requested for the
        sample object to have.

        The callable should return a hashable value that indicates the identity
        to use for the requested sample object. For each unique hashable value,
        only one sample object will be instantiated and returned each time
        a sample is requested where this callable returns the given identity.

        ``None`` may be returned to indicate that a new object should always
        be returned for the provided parameters.

    """

    #: You may also want to subclass :class:`Set` and implement
    #: an :meth:`identify` method, see :class:`chide.sqlalchemy.Set`
    #: for an example.
    identify = None

    def __init__(self, collection, identify=None):
        self.collection = collection
        self.identify = identify or self.identify
        if self.identify is None:
            raise TypeError('No identify callable supplied')

    def get(self, type_, **attrs):
        """
        Return an appropriate sample object of the specified ``type_``.

        The ``attrs`` mapping will be overlaid onto the sample attributes
        found in this set's :class:`~chide.Collection` before checking if
        an appropriate sample object already exists in the set.

        If one exists, it is returned. If not, one is created using
        this set's :class:`~chide.Collection`, added to the set and then
        returned.
        """
        attrs = self.collection._attrs(type_, attrs, self.get)
        key = self.identify(type_, attrs)
        if key is None:
            return type_(**attrs)
        obj = super(Set, self).get(key)
        if obj is None:
            obj = type_(**attrs)
            self[key] = obj
        return obj
