# middleware.py in your Django project to get some detailed request info - should be deactivated in prod
import logging
log = logging.getLogger(__name__)

class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log incoming request data
        if request.path == '/sum/api/token/':
            log.debug(f"Incoming request method: {request.method}")
            log.debug(f"Incoming request headers: {request.headers}")
            log.debug(f"Incoming request body: {request.body.decode('utf-8')}")

        response = self.get_response(request)

        # Log outgoing response data
        if request.path == '/sum/api/token/':
            log.debug(f"Outgoing response: {response.status_code}")
            log.debug(f"Outgoing response content: {response.content}")

        return response
