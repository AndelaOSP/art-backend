# Standard Library
import threading

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


class RequestMiddleware(MiddlewareMixin):
    """Class for getting the current request"""

    _requestdata = {}

    def process_request(self, request):
        """Store the current request."""
        self._requestdata[threading.current_thread()] = request

    def process_response(self, request, response):
        """remove the current request to avoid leaking memory"""
        self._requestdata.pop(threading.current_thread(), None)
        return response

    @classmethod
    def get_request(cls, default=None):
        """returns the current request or none if there is no request"""
        return cls._requestdata.get(threading.current_thread(), default)
