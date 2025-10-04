import os
import logging
from django.conf import settings
from datetime import datetime

# Logger Middleware
class RequestLoggingMiddleware:
    """
    Logs each incoming request to a file with timestamp, user, and path.


    Configurable via settings:
    REQUEST_LOG_PATH -> path to log file (defaults to <BASE_DIR>/requests.log)
    """

    def __init__(self, get_response):
        self.get_response = get_response

        base_dir = getattr(settings, "BASE_DIR", os.getcwd())
        log_path = getattr(
            settings, "REQUEST_LOG_PATH", os.path.join(base_dir, "requests.log")
        )

        self.logger = logging.getLogger("django.request_logging")

        if not self.logger.handlers:
            handler = logging.FileHandler(log_path)
            formatter = logging.Formatter("%(message)s")

            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            # avoid double logging into root handlers
            self.logger.propagate = False

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            user_str = getattr(user, "username", str(user))
        else:
            user_str = "Anonymous"

        self.logger.info(f"{datetime.now()} - User: {user_str} - Path: {request.path}")

        response = self.get_response(request)
        return response
