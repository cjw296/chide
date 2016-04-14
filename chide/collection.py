from weakref import WeakValueDictionary


class Collection(dict):

    identify = None

    def __init__(self, mapping, identify=None):
        super(Collection, self).__init__(mapping)
        self.instances = WeakValueDictionary()
        if identify is not None:
            self.identify = identify

    def make(self, type_, **attrs):
        computed_attrs = dict(self[type_])
        for key, value in computed_attrs.items():
            if value in self:
                computed_attrs[key] = self.make(value)
        computed_attrs.update(attrs)
        if self.identify is not None:
            key = self.identify(type_, computed_attrs)
            obj = self.instances.get(key)
            if obj is None:
                obj = type_(**computed_attrs)
                self.instances[key] = obj
            return obj

        else:
            return type_(**computed_attrs)
