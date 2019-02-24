"""
Provides public API.
"""

import contextlib
import locale
import inspect

from distutils.version import LooseVersion

from . import exceptions, engines, utilities, resources
from .version import __version__


class FacePP(object):
    """
    Entry point for all requests.
    """
    def __init__(self, api_key, api_secret, **kwargs):
        """
        :param string api_key: (required). Your registered API Key to call API.
        :param string api_secret: (required). Your registered API Secret to call API.
        :param string url: (optional). FacePP location.
        :param string version: (optional). FacePP version.
        :param dict requests: (optional). Connection options.
        :param string date_format: (optional). Formatting directives for date format.
        :param string datetime_format: (optional). Formatting directives for datetime format.
        :param raise_attr_exception: (optional). Control over resource attribute access exception raising.
        :type raise_attr_exception: bool or tuple
        :param cls engine: (optional). Engine that will be used to make requests to FacePP.
        :param bool return_raw_response (optional). Whether engine should return raw or json encoded responses.
        """
        self.url = kwargs.get('url', None)
        if self.url is None:
            url = 'https://api-{0}.faceplusplus.com'
            if locale.getdefaultlocale()[0].lower() == 'zh_cn':
                self.url = url.format('cn')
            else:
                self.url = url.format('us')

        self.ver = kwargs.get('version', None)
        self.date_format = kwargs.get('date_format', '%Y-%m-%d')
        self.datetime_format = kwargs.get('datetime_format', '%Y-%m-%dT%H:%M:%SZ')
        self.raise_attr_exception = kwargs.get('raise_attr_exception', True)

        engine = kwargs.get('engine', engines.DefaultEngine)

        if not inspect.isclass(engine) or not issubclass(engine, engines.BaseEngine):
            raise exceptions.EngineClassError

        self.engine = engine(api_key=api_key, api_secret=api_secret, **kwargs)

    def __getattr__(self, resource_name):
        """
        Returns a ResourceManager object for the requested resource.

        :param string resource_name: (required). Resource name.
        """
        if resource_name.startswith('_'):
            raise AttributeError

        resource_name = ''.join(word[0].upper() + word[1:] for word in str(resource_name).split('_'))

        try:
            resource_class = resources.registry[resource_name]['class']
        except KeyError:
            raise exceptions.ResourceError

        if self.ver is not None and LooseVersion(str(self.ver)) < LooseVersion(resource_class.facepp_version):
            raise exceptions.ResourceVersionMismatchError

        return resource_class.manager_class(self, resource_class)

    @classmethod
    def version(cls):
        """
        FacePP package's current version.
        """
        return __version__

    @contextlib.contextmanager
    def session(self, **options):
        """
        Initiates a temporary session with a copy of the current engine but with new options.

        :param dict options: (optional). Engine's options for a session.
        """
        engine = self.engine
        self.engine = engine.__class__(
            requests=utilities.merge_dicts(engine.requests, options.pop('requests', {})), **options)
        yield self
        self.engine = engine

