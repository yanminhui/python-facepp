"""
Defines facial recognition FacePP resources and resource mappings.
"""

from __future__ import unicode_literals

from .. import exceptions
from . import BaseResource


class Image(BaseResource):
    internal_id_key = 'image_id'
    container_one = None
    query_one = '/facepp/v3/detect'

    _repr = [['image_id', 'image_url', 'image_file']]
    _resource_set_map = {
        'faces': 'Face'
    }


class Base4TryGenerateImage(BaseResource):

    def _get_image(self, idx=None):

        def attr_name(attr, idx_):
            return ''.join([attr + '_' if attr[-1].isdigit() else attr, str(idx_)] if idx_ else attr)

        image = {}

        image_url = self._getattr(attr_name('image_url', idx))
        if image_url:
            image['image_url'] = image_url
        image_file = self._getattr(attr_name('image_file', idx))
        if image_file:
            image['image_file'] = image_file
        image_base64 = self._getattr(attr_name('image_base64', idx))
        if image_base64:
            image['image_base64'] = image_base64
        image_id = self._getattr(attr_name('image_id', idx))
        if image_id:
            image['image_id'] = image_id

        if len(image):
            faces = self._getattr(attr_name('faces', idx))
            if faces:
                image['faces'] = faces
                return image
            else:
                return self.manager.facepp.image.get(**image).raw()

        raise_attr_exception = self.manager.facepp.raise_attr_exception

        if isinstance(raise_attr_exception, bool) and raise_attr_exception:
            raise exceptions.ResourceAttrError
        elif isinstance(raise_attr_exception, (list, tuple)) and self.__class__.__name__ in raise_attr_exception:
            raise exceptions.ResourceAttrError

        return None

    def _getattr(self, attr, default=None):
        try:
            return super(Base4TryGenerateImage, self).__getattr__(attr)
        except exceptions.ResourceAttrError:
            return default
        return default


class Face(Base4TryGenerateImage):
    internal_id_key = 'face_token'
    container_all = 'faces'
    container_filter = 'faces'
    query_all = '/facepp/v3/detect'
    query_one = '/facepp/v3/face/getdetail'
    query_filter = '/facepp/v3/face/analyze'
    query_update = '/facepp/v3/face/setuserid'

    _repr = [['face_token', 'user_id']]
    _includes = ['gender', 'age', 'smiling', 'smile', 'headpose', 'facequality', 'blur', 'eyestatus',
                 'emotion', 'ethnicity', 'beauty', 'mouthstatus', 'eyegaze', 'skinstatus']
    _resource_map = {
        'faceset_token': 'FaceSet',
        'out_id': 'FaceSet'
    }
    _resource_set_map = {
        'facesets': 'FaceSet'
    }
    # _single_attr_id_map = {
    #     'image_id': 'Image'
    # }
    _multiple_attr_id_map = {
        'faceset_tokens': 'facesets',
        'outer_ids': 'facesets'
    }

    def __getattr__(self, attr):
        """
        Returns the requested attribute and makes a conversion if needed.
        """
        if attr == self.internal_id_key:
            value = super(Face, self).__getattr__(attr)
            if value:
                return value
            img = self.manager.new_manager('Image').to_resource(self._get_image())
            if len(img.faces):
                return img.faces[0].internal_id

        return super(Face, self).__getattr__(attr)

    @classmethod
    def construct_query_filter_path_and_container(cls, manager, **filters):
        """
        Constructs URL for filter method.

        :param managers.ResourceManager manager: (required). Manager object.
        :param dict filters: (optional). Filters used for resources retrieval.
        """
        if 'return_landmark' in filters:
            landmark = filters['return_landmark']
            if not str(landmark).isdigit():
                return '/facepp/v1/face/thousandlandmark', 'face'

        return cls.query_filter.format(**filters), cls.container_filter.format(**filters)

    def refresh(self, itself=True, **params):
        """
        Reloads resource data from FacePP.

        :param bool itself: (optional). Whether to refresh itself or return a new resource.
        :param dict params: (optional). Parameters used for resource retrieval.
        """
        resources = self.manager.filter(**dict(params, **{self.internal_id_key+'s': self.internal_id}))
        for resource in resources:
            if resource.internal_id != self.internal_id:
                continue
            if itself:
                self._encoded_attrs = {}
                self._decoded_attrs = resource.raw()
            else:
                return resource
            break

    def pre_update(self):
        """
        Tasks that should be done before updating the Resource.
        """
        if 'outer_ids' in self._changes or 'faceset_tokens' in self._changes:
            # Delete from all FaceSet
            tokens = [item.faceset_token for item in self.manager.facepp.face.get(
                **{self.internal_id_key: self.internal_id}).facesets]
            for token in tokens:
                url = self.manager.facepp.url + '/facepp/v3/faceset/removeface'
                data = {'faceset_token': token, self.internal_id_key: self.internal_id}
                self.manager.facepp.engine.request('post', url, data=data)

            # Add to FaceSet
            url = self.manager.facepp.url + '/facepp/v3/faceset/addface'

            for outer_id in self._changes['outer_ids'].split(',') if 'outer_ids' in self._changes else []:
                if not outer_id.strip():
                    continue
                data = {'outer_id': outer_id, 'face_tokens': self.face_token}
                self.manager.facepp.engine.request('post', url, data=data)

            for token in self._changes['faceset_tokens'].split(',') if 'faceset_tokens' in self._changes else []:
                if not token.strip():
                    continue
                data = {'faceset_token': token, 'face_tokens': self.face_token}
                self.manager.facepp.engine.request('post', url, data=data)

    def save(self, **attrs):
        """
        Creates or updates a Resource.

        :param dict attrs: (optional). Attrs to be set for a resource before create/update operation.
        """
        for attr in attrs:
            setattr(self, attr, attrs[attr])

        if not self.is_new():
            self.pre_update()
            if 'user_id' in self._changes:
                self.manager.update(**dict(self._changes, **{self.internal_id_key: self.internal_id}))
            self.post_update()
        else:
            self.pre_create()
            self._decoded_attrs = self.manager.create(**self._changes).raw()
            self.post_create()

        self._changes = {}
        return self


class FaceSet(BaseResource):
    internal_id_key = 'faceset_token'
    container_all = 'facesets'
    query_all = '/facepp/v3/faceset/getfacesets'
    query_one = '/facepp/v3/faceset/getdetail'
    query_create = '/facepp/v3/faceset/create'
    query_update = '/facepp/v3/faceset/update'
    query_delete = '/facepp/v3/faceset/delete'

    _repr = [['faceset_token', 'outer_id', 'display_name']]


class Compare(Base4TryGenerateImage):
    query_one = '/facepp/v3/compare'

    _unconvertible = ['request_id', 'time_used', 'confidence']
    _resource_map = {
        'image1': 'Image',
        'image2': 'Image'
    }
    _resource_set_map = {
        'faces1': 'Face',
        'faces2': 'Face'
    }
    # _single_attr_id_map = {
    #     'image_id1': 'Image',
    #     'image_id2': 'Image'
    # }

    def __getattr__(self, attr):
        """
        Returns the requested attribute and makes a conversion if needed.
        """
        if attr == 'image1':
            return self.manager.new_manager(self._resource_map[attr]).to_resource(self._get_image(1))
        elif attr == 'image2':
            return self.manager.new_manager(self._resource_map[attr]).to_resource(self._get_image(2))
        return super(Compare, self).__getattr__(attr)


class Search(Base4TryGenerateImage):
    query_one = '/facepp/v3/search'

    _unconvertible = ['request_id', 'time_used', 'confidence', 'user_id']
    _resource_map = {
        'image': 'Image'
    }
    _resource_set_map = {
        'results': 'Face'
    }
    # _single_attr_id_map = {
    #     'image_id': 'Image'
    # }

    def __getattr__(self, attr):
        """
        Returns the requested attribute and makes a conversion if needed.
        """
        if attr == 'image':
            return self.manager.new_manager(self._resource_map[attr]).to_resource(self._get_image())
        return super(Search, self).__getattr__(attr)
