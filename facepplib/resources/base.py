"""
Defines base FacePP resource class and it's infrastructure.
"""

from __future__ import unicode_literals

from datetime import date, datetime

from .. import managers, utilities, exceptions


registry = {}


class Registrar(type):
    """
    A resource that implements this metaclass, i.e. all resources that inherit from BaseResource,
    will be added to a resource registry to be managed by it's ResourceManager. Resource classes
    which name starts with Base are considered base classes and not added to the registry.
    """
    def __new__(mcs, name, bases, attrs):
        cls = super(Registrar, mcs).__new__(mcs, name, bases, attrs)

        if name.startswith('Base'):  # base classes shouldn't be added to the registry
            return cls

        if name not in registry:  # a name maybe already added to registry by other classes
            # {
            #   'class': cls,
            #   'attach_includes': ...,
            #   'attach_relations': ...
            # }
            registry[name] = {}

        for attr in ('_attach_includes', '_attach_relations'):
            class_attr_name = attr[7:]  # class attribute's name is `_includes`
            registry_attr_name = attr[1:]  # registry attribute's name is `attach_includes`

            if registry_attr_name in registry[name]:
                mcs.update_cls_attr(cls, class_attr_name, registry[name][registry_attr_name].keys())
                mcs.update_cls_attr(cls, '_resource_set_map', registry[name][registry_attr_name])

            if not isinstance(getattr(cls, attr), dict):  # _attach_includes
                continue

            for resource_name, value in getattr(cls, attr).items():
                if resource_name not in registry:
                    registry[resource_name] = {}

                if registry_attr_name not in registry[resource_name]:
                    registry[resource_name][registry_attr_name] = {}

                # {
                #   'attach_includes':
                #   {
                #       '<_attach_includes.value>': name
                #   }
                # }
                registry[resource_name][registry_attr_name][value] = name

                if 'class' in registry[resource_name]:
                    mcs.update_cls_attr(registry[resource_name]['class'], class_attr_name, [value])
                    mcs.update_cls_attr(registry[resource_name]['class'], '_resource_set_map', {value: name})

        return registry[name].setdefault('class', cls)

    @staticmethod
    def update_cls_attr(cls, name, value):
        """
        Updates class attribute's value by first copying the current value and then updating it with
        new value. We need that to be sure that each resource class has its own copy of the value.

        :param any cls: (required). Resource class.
        :param string name: (required). Attribute name.
        :param any value: (optional). Attribute value.
        """
        attr = getattr(cls, name, None)

        if isinstance(attr, list):
            value = list(attr) + list(value)
        elif isinstance(attr, dict):
            value = dict(attr, **value)
        else:
            return

        setattr(cls, name, value)


@utilities.fix_unicode
class BaseResource(utilities.with_metaclass(Registrar)):
    """
    Implementation of Redmine resource.
    """
    internal_id_key = 'request_id'
    facepp_version = None
    requirements = []
    container_all = None
    container_one = None
    container_filter = None
    container_create = None
    container_update = None
    query_all = None
    query_one = None
    query_filter = None
    query_create = None
    query_update = None
    query_delete = None
    http_method_create = 'post'
    http_method_update = 'post'
    http_method_delete = 'post'
    manager_class = managers.ResourceManager

    _repr = [['request_id']]
    _includes = []
    _relations = []
    _relations_name = None
    _unconvertible = ['request_id', 'time_used']
    _members = ['manager']
    _create_readonly = []
    _update_readonly = _create_readonly[:]
    _attach_includes = None
    _attach_relations = None
    _resource_map = {}  # Resources that should become a Resource object
    _resource_set_map = {}  # Resources that should become a ResourceSet object
    _single_attr_id_map = {}  # Resource attributes that should set another resource id to its value
    _multiple_attr_id_map = {}  # Resource attributes should set another resource ids to their value
    __length_hint__ = None  # fixes Python 2.6 list() call on resource object

    def __init__(self, manager, attributes):
        """
        :param managers.ResourceManager manager: (required). Manager object.
        :param dict attributes: (required). Resource attributes.
        """
        relations_includes = self._relations + self._includes

        self.manager = manager
        self._create_readonly += relations_includes
        self._update_readonly += relations_includes
        self._decoded_attrs = dict(dict.fromkeys(relations_includes), **attributes)
        self._encoded_attrs = {}
        self._changes = {}

        if self._relations_name is None:
            self._relations_name = self.__class__.__name__.lower()

    def __getitem__(self, item):
        """
        Provides a dictionary-like access to Resource attributes.
        """
        return getattr(self, item)

    def __setitem__(self, item, value):
        """
        Provides a dictionary-like setter for Resource attributes.
        """
        return setattr(self, item, value)

    def __getattr__(self, attr):
        """
        Returns the requested attribute and makes a conversion if needed.
        """
        if attr.startswith('_'):
            raise AttributeError

        # If this isn't the first time attribute access we can return it from cache
        encoded = self._encoded_attrs.get(attr)
        if encoded is not None:
            return encoded

        # Else this is the first time access and we need to encode the attribute
        decoded = self._decoded_attrs.get(attr)
        if decoded is not None:
            attr, encoded = self.encode(attr, decoded, self.manager)
        elif attr in self._relations:
            # i.e. { 'image_id': self.internal_id }
            filters = {'{0}_id'.format(self._relations_name): self.internal_id}
            encoded = self.manager.new_manager(self._resource_set_map[attr]).filter(**filters)
        elif attr in self._includes:
            if 'attributes' in self._decoded_attrs:
                encoded = self._decoded_attrs['attributes'].get(attr)
                if encoded is not None:
                    return encoded
            attr, encoded = self.encode(attr,
                                        self.refresh(itself=False, include=[attr]).raw()['attributes'][attr],
                                        self.manager)

        # In case of successful encoding we put it to a cache and return
        if encoded is not None:
            self._encoded_attrs[attr] = encoded
            return encoded

        # Else we return the defaults if this is a new item or throw an exception
        if self.is_new():
            return 0 if attr in ('id', 'version') else ''

        raise_attr_exception = self.manager.facepp.raise_attr_exception

        if isinstance(raise_attr_exception, bool) and raise_attr_exception:
            raise exceptions.ResourceAttrError
        elif isinstance(raise_attr_exception, (list, tuple)) and self.__class__.__name__ in raise_attr_exception:
            raise exceptions.ResourceAttrError

        return None

    def __setattr__(self, attr, value):
        """
        Sets the requested attribute.
        """
        if attr in self._members or attr.startswith('_'):
            return super(BaseResource, self).__setattr__(attr, value)
        elif attr in self._create_readonly and self.is_new():
            raise exceptions.ReadonlyAttrError
        elif attr in self._update_readonly and not self.is_new():
            raise exceptions.ReadonlyAttrError
        else:
            decoded_attr, decoded_value = self.decode(attr, value, self.manager)
            self._changes[decoded_attr] = decoded_value
            # i.e. _decoded_attrs['parent_id'] = parent_id
            self._decoded_attrs[attr] = decoded_value

            if attr in self._single_attr_id_map:
                # i.e. _decoded_atrs['parent'] = { 'id': parent_id }
                self._decoded_attrs[self._single_attr_id_map[attr]] = {'id': decoded_value}
            elif attr in self._multiple_attr_id_map:
                self._decoded_attrs[self._multiple_attr_id_map[attr]] = [{'id': attr_id} for attr_id in decoded_value]

        # When we set an attribute we put it's decoded value only to a _decoded_attrs
        # dict because it may never be accessed again, that is why we don't waste time
        # on the encode process but only clean the cache, and in case if it will be
        # accessed, the encoding process will be run automatically by __getattr__
        self._encoded_attrs.pop(attr, None)

    @classmethod
    def decode(cls, attr, value, manager):
        """
        Decodes a single attr, value pair from Python representation to the needed FacePP representation.

        :param string attr: (required). Attribute name.
        :param any value: (required). Attribute value.
        :param managers.ResourceManager manager: (required). Manager object.
        """
        type_ = type(value)

        if type_ is date:
            return attr, value.strftime(manager.facepp.date_format)
        elif type_ is datetime:
            return attr, value.strftime(manager.facepp.datetime_format)

        if isinstance(value, (list, tuple)):
            return 'return_attributes' if attr == 'include' else attr, ','.join(value)

        return attr, value

    @classmethod
    def encode(cls, attr, value, manager):
        """
        Encodes a single attr, value pair retrieved from FacePP to the needed Python representation.

        :param string attr: (required). Attribute name.
        :param any value: (required). Attribute value.
        :param managers.ResourceManager manager: (required). Manager object.
        """
        if attr in cls._unconvertible:
            return attr, value
        elif attr in cls._resource_map:
            return attr, manager.new_manager(cls._resource_map[attr]).to_resource(value)
        elif attr in cls._resource_set_map:
            return attr, manager.new_manager(cls._resource_set_map[attr]).to_resource_set(value)
        elif attr in cls._single_attr_id_map:
            resource_name = cls._single_attr_id_map[attr]
            resource_class = registry[resource_name]['class']
            return attr, manager.new_manager(resource_name).get(**{resource_class.internal_id_key: value})
        elif attr == 'parent':
            return attr, manager.new_manager(cls.__name__).to_resource(value)

        try:
            try:
                return attr, datetime.strptime(value, manager.facepp.datetime_format)
            except (TypeError, ValueError):
                return attr, datetime.strptime(value, manager.facepp.date_format).date()
        except (TypeError, ValueError):
            return attr, value

    @classmethod
    def bulk_decode(cls, attrs, manager):
        """
        Decodes resource data from Python representation to the needed FacePP representation.

        :param dict attrs: (required). Attributes in the form of key, value pairs.
        :param managers.ResourceManager manager: (required). Manager object.
        """
        return dict(cls.decode(attr, attrs[attr], manager) for attr in attrs)

    @classmethod
    def bulk_encode(cls, attrs, manager):
        """
        Encodes resource data retrieved from FacePP to the needed Python representation.

        :param dict attrs: (required). Attributes in the form of key, value pairs.
        :param managers.ResourceManager manager: (required). Manager object.
        """
        return dict(cls.encode(attr, attrs[attr], manager) for attr in attrs)

    @classmethod
    def construct_query_filter_path_and_container(cls, manager, **filters):
        """
        Constructs URL for filter method.

        :param managers.ResourceManager manager: (required). Manager object.
        :param dict filters: (optional). Filters used for resources retrieval.
        """
        return cls.query_filter.format(**filters), cls.container_filter.format(**filters)

    def raw(self):
        """
        Returns resource data as it was received from FacePP.
        """
        return self._decoded_attrs

    def refresh(self, itself=True, **params):
        """
        Reloads resource data from FacePP.

        :param bool itself: (optional). Whether to refresh itself or return a new resource.
        :param dict params: (optional). Parameters used for resource retrieval.
        """
        resource = self.manager.get(self.internal_id, **params)

        if itself:
            self._encoded_attrs = {}
            self._decoded_attrs = resource.raw()
        else:
            return resource

    def pre_create(self):
        """
        Tasks that should be done before creating the Resource.
        """
        pass

    def post_create(self):
        """
        Tasks that should be done after creating the Resource.
        """
        pass

    def pre_update(self):
        """
        Tasks that should be done before updating the Resource.
        """
        pass

    def post_update(self):
        """
        Tasks that should be done after updating the Resource.
        """
        pass

    def pre_delete(self):
        """
        Tasks that should be done before deleting the Resource.
        """
        pass

    def post_delete(self):
        """
        Tasks that should be done after deleting the Resource.
        """
        pass

    def save(self, **attrs):
        """
        Creates or updates a Resource.

        :param dict attrs: (optional). Attrs to be set for a resource before create/update operation.
        """
        for attr in attrs:
            setattr(self, attr, attrs[attr])

        if not self.is_new():
            self.pre_update()
            self.manager.update(**dict(self._changes, **{self.internal_id_key: self.internal_id}))
            self.post_update()
        else:
            self.pre_create()
            self._decoded_attrs = self.manager.create(**self._changes).raw()
            self.post_create()

        self._changes = {}
        return self

    def delete(self, **params):
        """
        Deletes Resource from Redmine.

        :param dict params: (optional). Parameters used for resource deletion.
        """
        self.pre_delete()
        response = self.manager.delete(self.internal_id, **params)
        self.post_delete()
        return response

    @property
    def url(self):
        """
        Returns full URL to the Resource for humans if there is one.
        """
        if self.query_one is not None:
            return self.manager.facepp.url + self.query_one.format(self.internal_id)

        return None

    @property
    def internal_id(self):
        """
        Returns identifier of the Resource for usage in internals of the library.
        """
        return getattr(self, self.internal_id_key) if self.internal_id_key else None

    def is_new(self):
        """
        Checks if Resource was just created and not yet saved to Redmine or it is an existing Resource.
        """
        return False if self.internal_id_key in self._decoded_attrs or 'request_id' in self._decoded_attrs else True

    def __dir__(self):
        """
        Allows dir() to be called on a Resource object and shows Resource attributes.
        """
        return list(self._decoded_attrs.keys())

    def __iter__(self):
        """
        Provides a way to iterate through Resource attributes and its values.
        """
        return iter(self._decoded_attrs.items())

    def __int__(self):
        """
        Integer representation of a Resource object.
        """
        return self.id

    def _representation(self, target):
        """
        Prepares values which should be used in either __str__ or __repr__ methods.

        :param string target: (required). Target of representation.
        """
        _str_, _repr_ = [], []

        for attrs in self._repr:
            for attr in reversed(attrs):
                value = getattr(self, attr, None)
                if not value:
                    continue

                _repr_.insert(0, value)  # i.e. [name, id]

                if attr != self.internal_id_key:
                    _str_.insert(0, value)  # i.e. [name]

            if len(_repr_) > 0:
                break

        if self.is_new() and len(_repr_) > 2:
            _str_ = _str_[:-1]
            _repr_ = _repr_[:-1]
        elif not _repr_:
            return []

        return _str_ or [str(_repr_[0])] if target == 'str' else _repr_

    def __str__(self):
        """
        Informal representation of a Resource object.
        """
        values = self._representation('str')
        return ' '.join(values) if values else self.__repr__()

    def __repr__(self):
        """
        Official representation of a Resource object.
        """
        values = self._representation('repr')
        view = '<facepplib.resources.{0.__class__.__name__}'.format(self)

        if not values:
            return view + '>'

        if isinstance(values[0], int):
            view += ' #{0}'.format(values.pop(0))

        if len(values) > 0:
            view += ' "{0}"'.format(' '.join(values))

        return view + '>'
