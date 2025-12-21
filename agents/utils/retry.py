"""
Retry Utilities for Jarvis
Provides exponential backoff retry decorator for LLM calls and external APIs.
"""
import time
import functools
from typing import Callable, Any, Type, Tuple
import logging

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Callable = None
):
    """
    Decorator for retrying function calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for each retry (2.0 = 1s, 2s, 4s)
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback(attempt, exception) on each retry
    
    Usage:
        @retry_with_backoff(max_retries=3)
        def call_api():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        if on_retry:
                            on_retry(attempt + 1, e)
                        else:
                            logger.warning(
                                f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}. "
                                f"Waiting {delay:.1f}s..."
                            )
                        
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"All {max_retries} retries failed for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator


def retry_llm_call(func: Callable) -> Callable:
    """
    Specialized retry for LLM calls.
    Retries on timeout, connection errors, and rate limits.
    """
    import requests
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        max_retries = 3
        delays = [1, 2, 4]  # Exponential backoff
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    print(f"[LLM] Timeout, retrying in {delays[attempt]}s... ({attempt + 1}/{max_retries})")
                    time.sleep(delays[attempt])
                else:
                    raise
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    print(f"[LLM] Connection error, retrying in {delays[attempt]}s... ({attempt + 1}/{max_retries})")
                    time.sleep(delays[attempt])
                else:
                    raise
            except Exception as e:
                # Check for rate limit in response
                if "rate" in str(e).lower() or "429" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = delays[attempt] * 2  # Longer wait for rate limits
                        print(f"[LLM] Rate limited, waiting {wait_time}s... ({attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        raise
                else:
                    raise
        
        return None
    
    return wrapper


class RetryContext:
    """
    Context manager for retry operations with state tracking.
    
    Usage:
        with RetryContext(max_retries=3) as ctx:
            while ctx.should_retry():
                try:
                    result = do_something()
                    break
                except Exception as e:
                    ctx.record_failure(e)
    """
    
    def __init__(self, max_retries: int = 3, initial_delay: float = 1.0):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.attempt = 0
        self.failures = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def should_retry(self) -> bool:
        return self.attempt < self.max_retries
    
    def record_failure(self, exception: Exception):
        self.failures.append({
            "attempt": self.attempt,
            "error": str(exception),
            "type": type(exception).__name__
        })
        self.attempt += 1
        
        if self.attempt < self.max_retries:
            delay = self.initial_delay * (2 ** self.attempt)
            time.sleep(delay)
    
    def get_failures(self):
        return self.failures
