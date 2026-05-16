import logging
import time


logger = logging.getLogger('performance.api')


class ApiTimingMiddleware:
    """
    Lightweight request timing for HTML/API endpoints.
    Logs only slower requests to keep noise manageable in production.
    """

    SLOW_MS = 300

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        duration_ms = (time.perf_counter() - start) * 1000

        if duration_ms >= self.SLOW_MS:
            logger.warning(
                "slow_request method=%s path=%s status=%s duration_ms=%.2f",
                request.method,
                request.path,
                getattr(response, 'status_code', 'unknown'),
                duration_ms,
            )

        if request.path.startswith('/api/') or request.path.startswith('/market/'):
            response['Server-Timing'] = f'app;dur={duration_ms:.2f}'

        return response
