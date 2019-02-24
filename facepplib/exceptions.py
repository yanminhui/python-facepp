"""
Python-FacePP tries it's best to provide human readable errors in all situations.
This is a list of all exceptions that Python-FacePP can throw.
"""

from __future__ import unicode_literals

from . import utilities


@utilities.fix_unicode
class BaseFacePPError(Exception):
    """
    Base exception class for FacePP exceptions.
    """


class HTTPProtocolError(BaseFacePPError):
    """
    Wrong HTTP protocol usage.
    """
    def __init__(self):
        super(HTTPProtocolError, self).__init__('FacePP url should start with HTTPS and not with HTTP')


class JSONDecodeError(BaseFacePPError):
    """
    Unable to decode received JSON.
    """
    def __init__(self, response):
        self.response = response
        super(JSONDecodeError, self).__init__(
            'Unable to decode received JSON, you can inspect exception\'s '
            '"response" attribute to find out what the response was')


class ResourceSetIndexError(BaseFacePPError):
    """
    Index doesn't exist in the ResourceSet.
    """
    def __init__(self):
        super(ResourceSetIndexError, self).__init__('Resource not available by requested index')


class ResourceNotFoundError(BaseFacePPError):
    """
    Requested resource doesn't exist.
    """
    def __init__(self):
        super(ResourceNotFoundError, self).__init__("Requested resource doesn't exist")


class ResourceRequirementsError(BaseFacePPError):
    """
    Resource requires specified FacePP plugin(s) to function.
    """
    def __init__(self, requirements):
        super(ResourceRequirementsError, self).__init__(
            'The following requirements must be installed for resource to function: {0}'.format(
                ', '.join(' >= '.join(req) if isinstance(req, (list, tuple)) else req for req in requirements)))


class ValidationError(BaseFacePPError):
    """
    FacePP validation errors occured on create/update resource.
    """
    def __init__(self, error):
        super(ValidationError, self).__init__(error)


class ResourceBadMethodError(BaseFacePPError):
    """
    Resource doesn't support the requested method.
    """
    def __init__(self):
        super(ResourceBadMethodError, self).__init__("Resource doesn't support the requested method")


class ResourceNoFiltersProvidedError(BaseFacePPError):
    """
    No filter(s) provided.
    """
    def __init__(self):
        super(ResourceNoFiltersProvidedError, self).__init__('Resource needs some filters to be filtered on')


class ResourceFilterError(BaseFacePPError):
    """
    Resource doesn't support requested filter(s).
    """
    def __init__(self):
        super(ResourceFilterError, self).__init__("Resource doesn't support requested filter(s)")


class ResourceNoFieldsProvidedError(BaseFacePPError):
    """
    No field(s) provided.
    """
    def __init__(self):
        super(ResourceNoFieldsProvidedError, self).__init__(
            'Resource needs some fields to be set to be created/updated')


class ResourceAttrError(BaseFacePPError, AttributeError):
    """
    Resource doesn't have the requested attribute.
    """
    def __init__(self):
        super(ResourceAttrError, self).__init__("Resource doesn't have the requested attribute")


class CustomFieldValueError(BaseFacePPError):
    """
    Custom fields should be passed as a list of dictionaries.
    """
    def __init__(self):
        super(CustomFieldValueError, self).__init__(
            "Custom fields should be passed as a list of dictionaries in the form of [{'id': 1, 'value': 'foo'}]")


class ReadonlyAttrError(BaseFacePPError):
    """
    Resource can't set attribute that is read only.
    """
    def __init__(self):
        super(ReadonlyAttrError, self).__init__("Can't set read only attribute")


class EngineClassError(BaseFacePPError):
    """
    Engine isn't a class or isn't a BaseEngine subclass.
    """
    def __init__(self):
        super(EngineClassError, self).__init__("Engine isn't a class or isn't a BaseEngine subclass")


class ResourceError(BaseFacePPError):
    """
    Unsupported FacePP resource exception.
    """
    def __init__(self):
        super(ResourceError, self).__init__('Unsupported FacePP resource')


class AuthenticationError(BaseFacePPError):
    """
    Invalid authentication details.
    """
    def __init__(self, reason=None):
        if reason:
            self.reason = reason
            super(AuthenticationError,
                  self).__init__('api_key does not have permission to call this API. (' + self.reason + ')')
        else:
            super(AuthenticationError,
                  self).__init__('api_key and api_secret does not match. '
                                 'Please make sure you use correct api_key, api_secret and API URL')


class ConcurrencyLimitExceeded(BaseFacePPError):
    """
    Concurrency limit exceeded.
    """
    def __init__(self):
        super(ConcurrencyLimitExceeded, self).__init__('Concurrency limit exceeded.')


class MissingArguments(BaseFacePPError):
    """
    Some required arguments missed.
    """
    def __init__(self, key):
        self.key = key
        super(MissingArguments, self).__init__('Some required arguments missed. (' + self.key + ')')


class BadArguments(BaseFacePPError):
    """
    Error while parsing some arguments.
    """
    def __init__(self, key):
        self.key = key
        super(BadArguments, self).__init__('Error while parsing some arguments. '
                                           'This error may be cause by illegal type or length of argument. (' +
                                           self.key + ')')


class CoexistenceArguments(BaseFacePPError):
    """
    Passed several arguments which are not allowed to coexist.
    """
    def __init__(self):
        super(CoexistenceArguments, self).__init__('Passed several arguments which are not allowed to coexist. '
                                                   'This error message will be returned unless otherwise stated')


class RequestEntityTooLarge(BaseFacePPError):
    """
    The request entity has exceeded the limit (2MB).
    """
    def __init__(self):
        super(RequestEntityTooLarge, self).__init__('The request entity has exceeded the limit (2MB). '
                                                    'This error message will be returned in plain text, '
                                                    'instead of JSON')


class ApiNotFound(BaseFacePPError):
    """
    Requested API can not be found.
    """
    def __init__(self):
        super(ApiNotFound, self).__init__('Requested API can not be found')


class InternalError(BaseFacePPError):
    """
    Internal error.
    """
    def __init__(self):
        super(InternalError, self).__init__('Internal error. Please retry the request. '
                                            'If this error keeps occurring, please contact our support team')


class ImageErrorUnsupportedFormat(BaseFacePPError):
    """
    The image which <param> indicates can not be resolved.
    """
    def __init__(self, param):
        self.param = param
        super(ImageErrorUnsupportedFormat,
              self).__init__('The image which <param> indicates can not be resolved. '
                             'The file format may not be supported or the file is damaged. (' +
                             self.param + ')')


class InvalidImageSize(BaseFacePPError):
    """
    The image which <param> indicates can not be resolved.
    """
    def __init__(self, param):
        self.param = param
        super(InvalidImageSize,
              self).__init__('The size of uploaded image does not meet the requirement as above. '
                             '<param> is the argument which indicates its size of image is too big or too small. (' +
                             self.param + ')')


class InvalidImageUrl(BaseFacePPError):
    """
    Failed downloading image from URL.
    """
    def __init__(self):
        super(InvalidImageUrl, self).__init__('Failed downloading image from URL. The image URL is wrong or invalid.')


class ImageFileTooLarge(BaseFacePPError):
    """
    The image file passed by <param> is too large.
    """
    def __init__(self, param):
        self.param = param
        super(ImageFileTooLarge,
              self).__init__('The image file passed by <param> is too large. '
                             'This API requires image file size to be no larger than 2 MB. (' +
                             self.param + ')')


class InsufficientPermission(BaseFacePPError):
    """
    The image file passed by <param> is too large.
    """
    def __init__(self, param):
        self.param = param
        super(InsufficientPermission,
              self).__init__('With a Free API Key, you cannot use <param>. '
                             'Please do not use this parameter, or use with a Standard API Key. (' +
                             self.param + ')')


class ImageDownloadTimeout(BaseFacePPError):
    """
    Image download timeout
    """
    def __init__(self):
        super(ImageDownloadTimeout, self).__init__('Image download timeout.')


class InvalidFaceToken(BaseFacePPError):
    """
    Face_token can not be found
    """
    def __init__(self, face_token):
        self.face_token = face_token
        super(InvalidFaceToken, self).__init__('Face_token can not be found. (' + self.face_token + ')')


class InvalidOuterId(BaseFacePPError):
    """
    Outer_id can not be found.
    """
    def __init__(self):
        super(InvalidOuterId, self).__init__('Outer_id can not be found.')


class InvalidFacesetToken(BaseFacePPError):
    """
    Faceset_token can not be found.
    """
    def __init__(self):
        super(InvalidFacesetToken, self).__init__('Faceset_token can not be found.')


class EmptyFaceset(BaseFacePPError):
    """
    No face_token found in the Faceset.
    """
    def __init__(self):
        super(EmptyFaceset, self).__init__('No face_token found in the Faceset.')


class FacesetNotEmpty(BaseFacePPError):
    """
    FaceSet is not empty, cannot be deleted (when check_empty=1).
    """
    def __init__(self):
        super(FacesetNotEmpty, self).__init__('FaceSet is not empty, cannot be deleted (when check_empty=1)')


class NewOuterIdExist(BaseFacePPError):
    """
    The new_outer_id passed already exists.
    """
    def __init__(self):
        super(NewOuterIdExist, self).__init__('The new_outer_id passed already exists')


class InvalidFaceTokensSize(BaseFacePPError):
    """
    Invalid size of face_tokens string passed.
    """
    def __init__(self):
        super(InvalidFaceTokensSize, self).__init__('Invalid size of face_tokens string passed')


class FacesetExist(BaseFacePPError):
    """
    FaceSet already exists.
    """
    def __init__(self):
        super(FacesetExist,
              self).__init__('FaceSet already exists (when outer_id is passed which already exists in the storage, '
                             'and the value of force_merge is 0)')


class FaceQuotaExceeded(BaseFacePPError):
    """
    The limitation of FaceSet number reached, cannot create FaceSet.
    """
    def __init__(self):
        super(FaceQuotaExceeded, self).__init__('The limitation of FaceSet number reached, cannot create FaceSet')


class InvalidTaskId(BaseFacePPError):
    """
    Task id cannot be found or task id is not allowed querying for this apikey.
    """
    def __init__(self):
        super(InvalidTaskId,
              self).__init__('Task id cannot be found or task id is not allowed querying for this apikey')


class VoidRequest(BaseFacePPError):
    """
    Face analyze operation cannot be performed, when return_landmark=0, and return_attributes=none.
    """
    def __init__(self):
        super(VoidRequest, self).__init__('Face analyze operation cannot be performed, '
                                          'when return_landmark=0, and return_attributes=none')


#
# {
#   status_code: ({
#                       exception_name: exception_with_zero_argument
#                 },
#                 {
#                       exception_name: exception_with_one_argument
#                 }),
#   ...
# }
#
exception_table = {
    400: ({
              'COEXISTENCE_ARGUMENTS': CoexistenceArguments,
              'INVALID_IMAGE_URL': InvalidImageUrl,
              'IMAGE_FILE_TOO_LARGE': ImageFileTooLarge,
              'INVALID_OUTER_ID': InvalidOuterId,
              'INVALID_FACESET_TOKEN': InvalidFacesetToken,
              'EMPTY_FACESET': InvalidFaceToken,
              'FACESET_NOT_EMPTY': FacesetNotEmpty,
              'NEW_OUTER_ID_EXIST': NewOuterIdExist,
              'INVALID_FACE_TOKENS_SIZE': InvalidFaceTokensSize,
              'FACESET_EXIST': FacesetExist,
              'FACESET_QUOTA_EXCEEDED': FaceQuotaExceeded,
              'INVALID_TASK_ID': InvalidTaskId,
              'VOID_REQUEST': VoidRequest
          },
          {
              'MISSING_ARGUMENTS': MissingArguments,
              'BAD_ARGUMENTS': BadArguments,
              'IMAGE_ERROR_UNSUPPORTED_FORMAT': ImageErrorUnsupportedFormat,
              'INVALID_IMAGE_SIZE': InvalidImageSize,
              'INVALID_FACE_TOKEN': InvalidFaceToken
           }),
    401: ({
              'AUTHENTICATION_ERROR': AuthenticationError
          },
          {
          }),
    403: ({
              'CONCURRENCY_LIMIT_EXCEEDED': ConcurrencyLimitExceeded
          },
          {
              'AUTHENTICATION_ERROR': AuthenticationError,
              'INSUFFICIENT_PERMISSION': InsufficientPermission
          }),
    404: ({
              'API_NOT_FOUND': ApiNotFound
          },
          {
          }),
    412: ({
              'IMAGE_DOWNLOAD_TIMEOUT': ImageDownloadTimeout
          },
          {
          }),
    413: ({
              'REQUEST_ENTITY_TOO_LARGE': RequestEntityTooLarge
          },
          {
          }),
    500: ({
              'INTERNAL_ERROR': InternalError
          },
          {
          })
}


#
# others
#

class NoFileError(BaseFacePPError):
    """
    File doesn't exist or is empty exception.
    """
    def __init__(self):
        super(NoFileError, self).__init__("Can't upload a file that doesn't exist or is empty")


class ConflictError(BaseFacePPError):
    """
    Resource version on the server is newer than on the client.
    """
    def __init__(self):
        super(ConflictError, self).__init__('Resource version on the server is newer than on the client')


class ImpersonateError(BaseFacePPError):
    """
    Invalid impersonate login provided.
    """
    def __init__(self):
        super(ImpersonateError, self).__init__("Impersonate login provided doesn't exist or isn't active")


class ServerError(BaseFacePPError):
    """
    FacePP internal error.
    """
    def __init__(self):
        super(ServerError, self).__init__('FacePP returned internal error')


class RequestEntityTooLargeError(BaseFacePPError):
    """
    Size of the request exceeds the capacity limit on the server.
    """
    def __init__(self):
        super(RequestEntityTooLargeError, self).__init__(
            "The requested resource doesn't allow POST requests or the size of the request exceeds the capacity limit")


class UnknownError(BaseFacePPError):
    """
    FacePP returned unknown error.
    """
    def __init__(self, status_code):
        self.status_code = status_code
        super(UnknownError, self).__init__(
            'FacePP returned unknown error with the status code {0}'.format(status_code))


class ResourceSetFilterLookupError(BaseFacePPError):
    """
    Resource set filter method received an invalid lookup in one of the filters.
    """
    def __init__(self, lookup, f):
        super(ResourceSetFilterLookupError, self).__init__(
            'Received an invalid lookup "{0}" in "{1}" filter'.format(lookup, f))


class VersionMismatchError(BaseFacePPError):
    """
    Feature isn't supported on specified Redmine version.
    """
    def __init__(self, feature):
        super(VersionMismatchError, self).__init__("{0} isn't supported on specified FacePP version".format(feature))


class ResourceVersionMismatchError(VersionMismatchError):
    """
    Resource isn't supported on specified Redmine version.
    """
    def __init__(self):
        super(ResourceVersionMismatchError, self).__init__('Resource')


class ResultSetTotalCountError(BaseFacePPError):
    """
    ResultSet hasn't been yet evaluated and cannot yield a total_count.
    """
    def __init__(self):
        super(ResultSetTotalCountError, self).__init__('Total count is unknown before evaluation')


class FileUrlError(BaseFacePPError):
    """
    URL provided to download a file can't be parsed.
    """
    def __init__(self):
        super(FileUrlError, self).__init__("URL provided to download a file can't be parsed")


class ForbiddenError(BaseFacePPError):
    """
    Requested resource is forbidden.
    """
    def __init__(self):
        super(ForbiddenError, self).__init__('Requested resource is forbidden')


class ExportNotSupported(BaseFacePPError):
    """
    Export functionality not supported by resource.
    """
    def __init__(self):
        super(ExportNotSupported, self).__init__('Export functionality not supported by resource')


class ExportFormatNotSupportedError(BaseFacePPError):
    """
    The given format isn't supported by resource.
    """
    def __init__(self):
        super(ExportFormatNotSupportedError, self).__init__(
            "The given format isn't supported by resource")



