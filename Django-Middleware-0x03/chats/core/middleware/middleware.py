from __future__ import annotations
from rest_framework import status

import os
import logging
import time as time_module
from datetime import date, datetime
from collections import deque
from threading import Lock

from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse

# -- Helpers


def _get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # X-Forwarded-For can be a comma-separated list. The left-most is the original client.
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "127.0.0.1")


# -- Middlewares


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

            self.logger.info(
                f"{datetime.now()} - User: {user_str} - Path: {request.path}"
            )

            response = self.get_response()
            return response


# Restrict Access By Time Middleware
class RestrictAccessByTimeMiddleware:
    """
    Deny requests to chat-related paths when server local time is outside allowed hours.


    Configurable via settings:
    CHAT_ALLOWED_START_HOUR (int, 0-23) default: 6
    CHAT_ALLOWED_END_HOUR (int, 0-23) default: 21


    Behavior:
    - Applies only to paths that start with '/chats' (so it doesn't block whole site).
    - If outside allowed window, returns 403 with JSON detail.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.start_hour = getattr(settings, "CHAT_ALLOWED_START_HOUR", 6)
        self.end_hour = getattr(settings, "CHAT_ALLOWED_END_HOUR", 21)

    def _is_allowed_time(self):
        now_hour = datetime.now().hour
        return self.start_hour <= now_hour < self.end_hour

    def __call__(self, request):
        if request.path.startswith("/chats"):
            if not self._is_allowed_time():
                return JsonResponse(
                    {
                        "detail": f"Chat is available only between {self.start_hour:02d}:00 and {self.end_hour:02d}:00 server time."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        return self.get_response(request)


# Offensive Language Middleware
class OffensiveLanguageFilterMiddleware:
    """
    Implements a simple rate limiter: counts POST requests (assumed to be "send message") by IP and block
    if they exceed MAX_MESSAGES_PER_WINDOW within MESSAGE_WINDOW_SECONDS.

    Configurable via settings:
    MAX_MESSAGES_PER_WINDOW (int) default: 5
    MESSAGE_WINDOW_SECONDS (int) default: 60
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.max_messages = getattr(settings, "MAX_MESSAGES_PER_WINDOW", 5)
        self.window = getattr(settings, "MESSAGE_WINDOW_SECONDS", 60)
        self.ip_records = dict[str, deque] = (
            {}
        )  # pyright: ignore[reportGeneralTypeIssues]
        self.lock = Lock()

    def __call__(self, request):
        if request.method == "POST" and request.path.startswith("/chats"):
            ip = _get_client_ip(request)
            now = time_module.time()

            with self.lock:
                if ip not in self.ip_records:
                    self.ip_records[ip] = deque()

                # Remove outdated timestamps
                while (
                    self.ip_records[ip] and self.ip_records[ip][0] < now - self.window
                ):
                    self.ip_records[ip].popleft()

                # Check if limit exceeded
                if len(self.ip_records[ip]) >= self.max_messages:
                    return JsonResponse(
                        {"detail": "Message limit exceeded. Try again later."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )

                # Record new message timestamp
                self.ip_records[ip].append(now)

        return self.get_response(request)


# -- Role Permissions Middleware


class RolePermissionsMiddleware:
    """
    Ensures only users with admin/moderator roles can access certain protected chat actions.
    Configurable via settings:
        ROLE_PROTECTED_PATHS -> list of path prefixes to protect (default: ['/chats/admin', "chats/moderator])
        ALLOWED_ADMIN_ROLES -> list of roles considered admin (default: ['admin', 'moderator'])
    if user.is_superuser or user.is_staff -> allowed
    else if user.role in ALLOWED_ADMIN_ROLES -> allowed
    else -> 403 Forbidden
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_roles = getattr(settings, "ALLOWED_ADMIN_ROLES", ["admin", "moderator"])
        self.protected_paths = getattr(
            settings, "ROLE_PROTECTED_PATHS", ["/chats/admin", "/chats/moderator"]
        )

    def _is_protected(self, path):
        return any(path.startswith(prefix) for prefix in self.protected_paths)

    def _user_has_role(self, user):
        if not user or not getattr(user, "is_authenticated", False):
            return False
        
        if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
            return True
        
        user_role = getattr(user, "role", None)
        if user_role:   
            return user_role.lower() in self.admin_roles
        return False

    def __call__(self, request):
        if self._is_protected(request.path):
            user = getattr(request, "user", None)
            if not self._user_has_role(user):
                return HttpResponseForbidden(
                    "You do not have permission to access this resource."
                )

        return self.get_response(request)