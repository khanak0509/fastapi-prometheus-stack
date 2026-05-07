import time
import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.metrics import (
    HTTP_REQUESTS_TOTAL,
    HTTP_ERRORS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_ACTIVE_REQUESTS,
    HTTP_REQUEST_SIZE_BYTES,
    HTTP_RESPONSE_SIZE_BYTES,
    )

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path
        
        # We normalize the path so we don't get a new metric for every single ID.
        # e.g. /users/1, /users/2 both become /users/{user_id}
        normalized_endpoint = self.normalize_path(path)
        
        # Track that we have an active request starting
        HTTP_ACTIVE_REQUESTS.labels(method=method, endpoint=normalized_endpoint).inc()
        
        start_time = time.perf_counter()
        
        # Log the request body size if available
        content_length = request.headers.get("Content-Length")
        if content_length:
            HTTP_REQUEST_SIZE_BYTES.labels(method=method, endpoint=normalized_endpoint).observe(int(content_length))
        else:
            HTTP_REQUEST_SIZE_BYTES.labels(method=method, endpoint=normalized_endpoint).observe(0)

        try:
            response: Response = await call_next(request)
            
            duration = time.perf_counter() - start_time
            status_code = response.status_code
            
            # Record the final stats for this request
            HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=normalized_endpoint, status_code=status_code).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=normalized_endpoint).observe(duration)
            
            # Log the response size
            resp_size = response.headers.get("Content-Length")
            if resp_size:
                HTTP_RESPONSE_SIZE_BYTES.labels(method=method, endpoint=normalized_endpoint).observe(int(resp_size))
            else:
                HTTP_RESPONSE_SIZE_BYTES.labels(method=method, endpoint=normalized_endpoint).observe(0)
            
            # If things went south (4xx or 5xx), log an error metric
            if status_code >= 400:
                error_type = "client_error" if status_code < 500 else "server_error"
                HTTP_ERRORS_TOTAL.labels(method=method, endpoint=normalized_endpoint, error_type=error_type).inc()
                
            return response
            
        except Exception as e:
            # If the app crashes completely, make sure we still log a 500
            duration = time.perf_counter() - start_time
            HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=normalized_endpoint, status_code=500).inc()
            HTTP_ERRORS_TOTAL.labels(method=method, endpoint=normalized_endpoint, error_type="server_error").inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=normalized_endpoint).observe(duration)
            raise e
        finally:
            # Always decrement the active count, no matter what
            HTTP_ACTIVE_REQUESTS.labels(method=method, endpoint=normalized_endpoint).dec()

    def normalize_path(self, path: str) -> str:
        # Regex magic to keep our Prometheus cardinality low.
        # Replaces specific IDs with generic placeholders.
        path = re.sub(r"/users/[^/]+", "/users/{user_id}", path)
        path = re.sub(r"/orders/[^/]+", "/orders/{order_id}", path)
        path = re.sub(r"/products/[^/]+", "/products/{id}", path)
        
        # Ensure sub-routes like /status are also handled correctly
        path = re.sub(r"/orders/\{order_id\}/status", "/orders/{order_id}/status", path)
        
        return path
