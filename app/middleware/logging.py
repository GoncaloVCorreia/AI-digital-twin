"""
Custom middleware for request logging and monitoring.
"""

import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests with timing and user information."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        if forwarded_for := request.headers.get("X-Forwarded-For"):
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Log request start
        start_time = time.time()
        logger.info(
            f"Request started - ID: {request_id} | "
            f"Method: {request.method} | "
            f"URL: {request.url} | "
            f"Client: {client_ip}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log successful response
            process_time = time.time() - start_time
            logger.info(
                f"Request completed - ID: {request_id} | "
                f"Status: {response.status_code} | "
                f"Duration: {process_time:.4f}s"
            )
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Request failed - ID: {request_id} | "
                f"Error: {str(e)} | "
                f"Duration: {process_time:.4f}s"
            )
            raise

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response