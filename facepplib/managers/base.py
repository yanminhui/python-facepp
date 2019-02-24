"""
Defines base FacePP resource manager class and it's infrastructure.
"""

from .. import exceptions, resultsets, utilities


class ResourceManager(object):
    """
    Manages given FacePP resource class with the help of facepp object.
    """
    def __init__(self, facepp, resource_class):
        """
        :param facepp.FacePP facepp: (required). FacePP object.
        :param resources.BaseResource resource_class: (required). Resource class.
        """
        self.url = ''
        self.params = {}
        self.container = None
        self.facepp = facepp
        self.resource_class = resource_class

    def to_resource(self, resource):
        """
        Converts resource data to Resource object.

        :param dict resource: (required). Resource data.
        """
        return self.resource_class(self, resource)

    def to_resource_set(self, resources):
        """
        Converts an iterable with resources data to ResourceSet object.

        :param resources: (required). Resource data.
        :type resources: list or tuple
        """
        return resultsets.ResourceSet(self, resources)

    def new(self):
        """
        Returns new empty Resource object.
        """
        return self.to_resource({})

    def new_manager(self, resource_name, **params):
        """
        Returns new ResourceManager object.

        :param string resource_name: (required). Resource name.
        :param dict params: (optional). Parameters used for resources retrieval.
        """
        manager = getattr(self.facepp, resource_name)
        manager.params = params
        return manager

    def get(self, **params):
        """
        Returns a Resource object from FacePP.

        :param dict params: (optional). Parameters used for resource retrieval.
        """
        if self.resource_class.query_one is None:
            operation = self.all if self.resource_class.query_all else self.filter
            if operation is None:
                raise exceptions.ResourceBadMethodError

            resource = operation(**params).get(None)
            if resource is None:
                raise exceptions.ResourceNotFoundError

            return resource

        try:
            self.url = self.facepp.url + self.resource_class.query_one.format(**params)
        except KeyError as exception:
            raise exceptions.ValidationError('{0} argument is required'.format(exception))

        self.params = self.resource_class.bulk_decode(params, self)
        self.container = self.resource_class.container_one

        try:
            res = self.facepp.engine.request('post', self.url, data=self.params)
            if self.container is not None:
                res = res[self.container]
            return self.to_resource(dict(res, **params))
        except exceptions.ResourceNotFoundError as e:
            if self.resource_class.requirements:
                raise exceptions.ResourceRequirementsError(self.resource_class.requirements)
            raise e

    def all(self, **params):
        """
        Returns a ResourceSet object with all Resource objects.

        :param dict params: (optional). Parameters used for resources retrieval.
        """
        if self.resource_class.query_all is None or self.resource_class.container_all is None:
            raise exceptions.ResourceBadMethodError

        self.url = self.facepp.url + self.resource_class.query_all.format(**params)
        self.params = self.resource_class.bulk_decode(params, self)
        self.container = self.resource_class.container_all
        return resultsets.ResourceSet(self)

    def filter(self, **filters):
        """
        Returns a ResourceSet object with Resource objects filtered by a dict of filters.

        :param dict filters: (optional). Filters used for resources retrieval.
        """
        if self.resource_class.query_filter is None:
            raise exceptions.ResourceBadMethodError

        if not filters:
            raise exceptions.ResourceNoFiltersProvidedError

        try:
            path, self.container = self.resource_class.construct_query_filter_path_and_container(self, **filters)
            self.url = self.facepp.url + path
        except KeyError:
            raise exceptions.ResourceFilterError

        self.params = self.resource_class.bulk_decode(filters, self)
        return resultsets.ResourceSet(self)

    def _construct_create_url(self, path):
        """
        Constructs URL for create method.

        :param string path: absolute URL path.
        """
        return self.facepp.url + path

    def _prepare_create_request(self, request):
        """
        Makes the necessary preparations for create request data.

        :param dict request: Request data.
        """
        return self.resource_class.bulk_decode(request, self)

    def create(self, **fields):
        """
        Creates a new resource in FacePP and returns created Resource object on success.

        :param dict fields: (optional). Fields used for resource creation.
        """
        if self.resource_class.query_create is None:
            raise exceptions.ResourceBadMethodError

        if not fields:
            raise exceptions.ResourceNoFieldsProvidedError

        formatter = utilities.MemorizeFormatter()

        try:
            url = self._construct_create_url(formatter.format(self.resource_class.query_create, **fields))
        except KeyError as e:
            raise exceptions.ValidationError('{0} field is required'.format(e))

        self.params = fields
        self.container = self.resource_class.container_create
        request = self._prepare_create_request(formatter.unused_kwargs)
        response = self.facepp.engine.request(self.resource_class.http_method_create, url, data=request)
        resource = self._process_create_response(request, response)
        # self.url = self.facepp.url + self.resource_class.query_one.format(resource.internal_id, **fields)
        return resource

    def _process_create_response(self, request, response):
        """
        Processes create response and constructs resource object.

        :param dict request: Original request data.
        :param any response: Response received from FacePP for this request data.
        """
        res = response[self.container] if self.container else response
        return self.to_resource(dict(res, **self.params))

    def _construct_update_url(self, path):
        """
        Constructs URL for update method.

        :param string path: absolute URL path.
        """
        return self.facepp.url + path

    def _prepare_update_request(self, request):
        """
        Makes the necessary preparations for update request data.

        :param dict request: Request data.
        """
        return self.resource_class.bulk_decode(request, self)

    def update(self, **fields):
        """
        Updates a Resource object by resource id.

        :param dict fields: (optional). Fields that will be updated for the resource.
        """
        if self.resource_class.query_update is None:
            raise exceptions.ResourceBadMethodError

        if not fields:
            raise exceptions.ResourceNoFieldsProvidedError

        formatter = utilities.MemorizeFormatter()

        try:
            query_update = formatter.format(self.resource_class.query_update, **fields)
        except KeyError as e:
            param = e.args[0]

            if param in self.params:
                fields[param] = self.params[param]
                query_update = formatter.format(self.resource_class.query_update, **fields)
            else:
                raise exceptions.ValidationError('{0} argument is required'.format(e))

        url = self._construct_update_url(query_update)
        self.container = self.resource_class.container_update
        request = self._prepare_update_request(formatter.unused_kwargs)
        response = self.facepp.engine.request(self.resource_class.http_method_update, url, data=request)
        return self._process_update_response(request, response)

    def _process_update_response(self, request, response):
        """
        Processes update response.

        :param dict request: Original request data.
        :param any response: Response received from Redmine for this request data.
        """
        res = response[self.container] if self.container else response
        return self.to_resource(dict(res, **self.params))

    def _construct_delete_url(self, path):
        """
        Constructs URL for delete method.

        :param string path: absolute URL path.
        """
        return self.facepp.url + path

    def _prepare_delete_request(self, request):
        """
        Makes the necessary preparations for delete request data.

        :param dict request: Request data.
        """
        return self.resource_class.bulk_decode(request, self)

    def delete(self, **params):
        """
        Deletes a Resource object by resource id.

        :param dict params: (optional). Parameters used for resource deletion.
        """
        if self.resource_class.query_delete is None:
            raise exceptions.ResourceBadMethodError

        try:
            url = self._construct_delete_url(self.resource_class.query_delete.format(**params))
        except KeyError as e:
            raise exceptions.ValidationError('{0} argument is required'.format(e))

        request = self._prepare_delete_request(params)
        response = self.facepp.engine.request(self.resource_class.http_method_delete, url, data=request)
        return self._process_delete_response(request, response)

    def _process_delete_response(self, request, response):
        """
        Processes delete response.

        :param dict request: Original request data.
        :param any response: Response received from FacePP for this request data.
        """
        res = response[self.container] if self.container else response
        return self.to_resource(dict(res, **self.params))

    def __repr__(self):
        """
        Official representation of a ResourceManager object.
        """
        return '<facepplib.managers.{0} object for {1} resource>'.format(
            self.__class__.__name__, self.resource_class.__name__)
