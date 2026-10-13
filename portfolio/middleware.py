"""Per-request memo for SiteSettings, so one page render loads it once.

Outside a request (shell, tests calling code directly) nothing is cached.
"""
from contextvars import ContextVar

_request_memo = ContextVar('portfolio_request_memo', default=None)


def get_request_memo():
    return _request_memo.get()


class RequestMemoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = _request_memo.set({})
        try:
            return self.get_response(request)
        finally:
            _request_memo.reset(token)
