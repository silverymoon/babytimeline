from django import http
from django.conf import settings

import logging
import logging.handlers
import sys
import traceback

def _get_traceback(self, exc_info=None):
    """Helper function to return the traceback as a string"""
    return '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))

class LoggingExceptionMiddleware:

    def __init__(self):
        self.logger = logging.getLogger("errors")
        self.logger.setLevel(logging.WARN)
        handler = logging.handlers.TimedRotatingFileHandler(settings.ERROR_LOG_FILE, 'midnight', 1, 15)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(pathname)s.%(funcName)s:%(lineno)d %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def process_exception(self, request, exception):
        self.logger.error("EXCEPTION: request: %r", request, exc_info=True)
        return None

class LoggingRequestMiddleware:

    def __init__(self):
        self.logger = logging.getLogger("actions")
        self.logger.setLevel(logging.INFO)
        handler = logging.handlers.TimedRotatingFileHandler(settings.ACTIONS_LOG_FILE, 'midnight', 1, 15)
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def process_request(self, request):
        request_keys = request.GET.keys()
        request_keys += request.POST.keys()
        clean_request_items = [(key, request.REQUEST[key]) for key in request_keys if not "password" in key]
        clean_request = dict(clean_request_items)
        self.logger.info("%s %s %s (%s)" %(request.method, request.path, clean_request, request.user))
        return None


