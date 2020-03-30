from __future__ import absolute_import

from .contract import LazyProperty, LazyContract, LazyContractValidationError


class StringProperty(LazyProperty):

    _type = str

    def deserialize(self, obj):
        return obj if isinstance(obj, self._type) else str(obj)


class BooleanProperty(LazyProperty):

    _type = bool

    def deserialize(self, obj):
        if isinstance(obj, str):
            return obj.lower() == "true"
        else:
            return self._type(obj)


class IntegerProperty(LazyProperty):

    _type = int

    def deserialize(self, obj):
        return obj if isinstance(obj, self._type) else int(obj)


class EnumerationProperty(LazyProperty):

    _type = str

    def __init__(self, options, *args, **kwargs):
        super(EnumerationProperty, self).__init__(*args, **kwargs)
        self._options = set(options)

    def deserialize(self, obj):
        if obj is not None and obj not in self._options:
            raise ValueError(
                "enumeration option {} not in acception options: {}".format(
                    obj, self._options
                )
            )
        return obj


class FloatProperty(LazyProperty):

    _type = float


class ObjectProperty(LazyProperty):

    _type = LazyContract

    def __init__(self, kind, *args, **kwargs):
        assert issubclass(kind, LazyContract)
        super(ObjectProperty, self).__init__(*args, **kwargs)
        self._kind = kind

    def serialize(self, obj):
        return obj.to_dict()

    def deserialize(self, obj):
        return obj if isinstance(obj, self._kind) else self._kind(obj)


class ContainerProperty(LazyProperty):
    def __init__(self, lazyproperty=None, *args, **kwargs):
        assert lazyproperty is None or isinstance(lazyproperty, LazyProperty)
        super(ContainerProperty, self).__init__(*args, **kwargs)
        self._property = lazyproperty


class ListProperty(ContainerProperty):

    _type = list

    def serialize(self, obj):
        if self._property is None:
            return obj
        else:
            return [self._property.serialize(e) for e in obj]

    def deserialize(self, obj):
        if self._property is None:
            return obj
        else:
            l = []
            i = 0
            try:
                for i, e in enumerate(obj):
                    l.append(self._property.deserialize(e))
                return l
            except Exception as e:
                if isinstance(e, LazyContractValidationError):
                    idx = "[" + str(i) + "]"
                    if e.path:
                        e.path = idx + "." + e.path
                    else:
                        e.path = idx
                raise


class DictProperty(ContainerProperty):

    _type = dict

    def serialize(self, obj):
        if self._property is None:
            return obj
        else:
            return {k: self._property.serialize(e) for k, e in obj.items()}

    def deserialize(self, obj):
        if self._property is None:
            return obj
        else:
            d = {}
            l = []
            k = ""
            try:
                for k, e in obj.items():
                    d[k] = self._property.deserialize(e)
                return d
            except Exception as e:
                if isinstance(e, LazyContractValidationError):
                    idx = "[" + k + "]"
                    if e.path:
                        e.path = idx + "." + e.path
                    else:
                        e.path = idx
                raise


class SetProperty(ContainerProperty):

    _type = set

    def serialize(self, obj):
        if self._property is None:
            return [e for e in obj]
        else:
            return [self._property.serialize(e) for e in obj]

    def deserialize(self, obj):
        if self._property is None:
            return {e for e in obj}
        else:
            return {self._property.deserialize(e) for e in obj}
