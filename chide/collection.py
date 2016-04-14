from weakref import WeakValueDictionary


class Collection(dict):
    """
    A collection of attributes to use to make sample objects.

    :param mapping:
        A dictionary mapping object types to a dictionary
        of attributes to make a sample object of that type.

    :param identify:
        An optional callable that will determine the identity
        of a sample object. The callable must take the :class:`type`
        of the sample object that the dictionary of attributes
        that will be used to create it and should return a hashable
        object representing the identity of that object.
        Only one object with a given identity will be instantiated, after
        that any calls to :meth:`~Collection.make` will return that
        instance rather than creating a new one.
    """

    identify = None

    def __init__(self, mapping, identify=None):
        super(Collection, self).__init__(mapping)
        self.instances = WeakValueDictionary()
        if identify is not None:
            self.identify = identify

    def make(self, type_, **attrs):
        """
        Make a sample object of the specified ``type_`` using the default
        attributes for that type in this :class:`Collection`.

        The ``attrs`` mapping will be overlayed onto the sample attributes
        before being used with ``type_`` to instantiate and return a new
        sample object.
        """
        computed_attrs = dict(self[type_])
        for key, value in computed_attrs.items():
            if value in self:
                computed_attrs[key] = self.make(value)
        computed_attrs.update(attrs)
        if self.identify is not None:
            key = self.identify(type_, computed_attrs)
            if key:
                obj = self.instances.get(key)
                if obj is None:
                    obj = type_(**computed_attrs)
                    self.instances[key] = obj
                return obj
        return type_(**computed_attrs)
