import logging
import time
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests with user_id, endpoint, timestamp, and status"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get user_id from JWT token if available
        user_id = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # In a production app, you'd decode the token here
            pass
        
        # Call the next middleware/endpoint
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log request details
        log_data = {
            "user_id": user_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": f"{process_time:.3f}s",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info(json.dumps(log_data))
        
        return response
