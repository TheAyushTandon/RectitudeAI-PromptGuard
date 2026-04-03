"""Rate limiting using Redis."""

from fastapi import HTTPException, status, Request
from redis import Redis
from redis.exceptions import RedisError
from backend.gateway.config import settings
from backend.utils.logging import get_logger
import time

logger = get_logger(__name__)


class RateLimiter:
    """Rate limiting using Redis sliding window."""
    
    def __init__(self):
        try:
            self.redis_client = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
        except RedisError as e:
            logger.warning(f"Redis connection failed: {e}. Rate limiting disabled.")
            self.redis_client = None
        
        self.max_requests = settings.rate_limit_requests
        self.window_seconds = settings.rate_limit_window_seconds
    
    async def check_rate_limit(self, key: str) -> None:
        """
        Check if rate limit is exceeded.
        
        Args:
            key: Rate limit key (usually user/IP based)
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        
        # If Redis is not available, skip rate limiting
        if self.redis_client is None:
            return
        
        try:
            current_time = int(time.time())
            window_start = current_time - self.window_seconds
            
            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count requests in current window
            request_count = self.redis_client.zcard(key)
            
            if request_count >= self.max_requests:
                logger.warning(f"Rate limit exceeded for key: {key}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds} seconds."
                )
            
            # Add current request
            self.redis_client.zadd(key, {str(current_time): current_time})
            self.redis_client.expire(key, self.window_seconds)
            
        except RedisError as e:
            logger.error(f"Redis error during rate limiting: {e}")
            # Fail open - don't block requests if Redis fails
            pass


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_dependency(request: Request):
    """
    FastAPI dependency for rate limiting.
    
    Args:
        request: FastAPI request object
    """
    
    # Use IP address as rate limit key
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}"
    
    await rate_limiter.check_rate_limit(key)
