import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    """
    Logs every incoming request for debugging — URL, method, body, headers, etc.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request info before view executes
        try:
            body = request.body.decode("utf-8") if request.body else ""
        except Exception:
            body = "<unreadable>"

        logger.info(
            f"\n--- Incoming Request ---\n"
            f"Method: {request.method}\n"
            f"Path: {request.path}\n"
            f"Query Params: {dict(request.GET)}\n"
            f"Headers: {dict(request.headers)}\n"
            f"Body: {body}\n"
            f"------------------------\n"
        )

        response = self.get_response(request)

        # Log response info
        try:
            resp_preview = (
                response.content.decode("utf-8")[:500]
                if hasattr(response, "content")
                else "<streaming>"
            )
        except Exception:
            resp_preview = "<unreadable>"

        logger.info(
            f"\n--- Response ---\n"
            f"Status: {response.status_code}\n"
            f"Body: {resp_preview}\n"
            f"----------------\n"
        )

        return response
