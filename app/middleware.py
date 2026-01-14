import logging
import time
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils import decode_token

from app.utils import decode_token
from app.logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests with user_id, endpoint, timestamp, and status"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get user_id from JWT token if available
        user_id = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                payload = decode_token(token)
                if payload:
                    user_id = payload.get("sub")
            except Exception:
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
