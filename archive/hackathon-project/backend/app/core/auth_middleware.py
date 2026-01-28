"""
Authentication Middleware Integration
Handles JWT tokens, rate limiting, and user context
"""
import time
import jwt
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> bool:
        now = time.time()
        user_requests = self.requests[identifier]
        
        # Remove old requests outside the window
        while user_requests and user_requests[0] < now - self.window_seconds:
            user_requests.popleft()
        
        # Check if under limit
        if len(user_requests) < self.max_requests:
            user_requests.append(now)
            return True
        
        return False
    
    def get_reset_time(self, identifier: str) -> int:
        user_requests = self.requests[identifier]
        if user_requests:
            return int(user_requests[0] + self.window_seconds)
        return int(time.time() + self.window_seconds)

class AuthenticationMiddleware:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.security = HTTPBearer(auto_error=False)
        self.rate_limiter = RateLimiter()
        self.user_sessions = {}
        
    async def authenticate_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Authenticate request and return user context"""
        try:
            # Extract token
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return None
            
            token = authorization.split(" ")[1]
            
            # Verify JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id = payload.get("user_id")
            
            if not user_id:
                return None
            
            # Check rate limiting
            client_ip = request.client.host
            identifier = f"{user_id}:{client_ip}"
            
            if not self.rate_limiter.is_allowed(identifier):
                reset_time = self.rate_limiter.get_reset_time(identifier)
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={"X-RateLimit-Reset": str(reset_time)}
                )
            
            # Update session
            self.user_sessions[user_id] = {
                "last_activity": time.time(),
                "ip_address": client_ip,
                "user_agent": request.headers.get("User-Agent", "")
            }
            
            return {
                "user_id": user_id,
                "email": payload.get("email"),
                "permissions": payload.get("permissions", []),
                "session_id": payload.get("session_id")
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    def generate_token(self, user_data: Dict[str, Any], expires_in: int = 3600) -> str:
        """Generate JWT token for user"""
        payload = {
            "user_id": user_data["user_id"],
            "email": user_data["email"],
            "permissions": user_data.get("permissions", []),
            "session_id": user_data.get("session_id"),
            "exp": time.time() + expires_in,
            "iat": time.time()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def check_permission(self, user_context: Dict[str, Any], required_permission: str) -> bool:
        """Check if user has required permission"""
        user_permissions = user_context.get("permissions", [])
        return required_permission in user_permissions or "admin" in user_permissions
    
    def get_user_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get user session metrics"""
        session = self.user_sessions.get(user_id, {})
        return {
            "user_id": user_id,
            "last_activity": session.get("last_activity"),
            "ip_address": session.get("ip_address"),
            "user_agent": session.get("user_agent"),
            "session_duration": time.time() - session.get("last_activity", time.time()) if session else 0
        }

# Global auth middleware instance
auth_middleware = AuthenticationMiddleware("your-secret-key-here")