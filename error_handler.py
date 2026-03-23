"""
Error Handling: Comprehensive error handling and recovery mechanisms.
Provides retry logic, fallback strategies, and error tracking.
"""

import time
import functools
from typing import Callable, TypeVar, Optional, Any, List
from utils.logger import app_logger, log_error

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry logic."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            backoff_factor: Multiplier for exponential backoff
            exceptions: Tuple of exceptions to catch and retry on
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.exceptions = exceptions


def retry(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable] = None
) -> Callable:
    """
    Decorator for retry logic with exponential backoff.
    
    Args:
        config: Retry configuration
        on_retry: Callback function called before each retry
        
    Returns:
        Decorated function
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    app_logger.debug(f"Attempting {func.__name__} (attempt {attempt}/{config.max_attempts})")
                    return func(*args, **kwargs)
                
                except config.exceptions as e:
                    last_exception = e
                    
                    if attempt < config.max_attempts:
                        app_logger.warning(
                            f"{func.__name__} failed on attempt {attempt}: {str(e)}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        
                        # Call retry callback if provided
                        if on_retry:
                            on_retry(attempt, e, delay)
                        
                        time.sleep(delay)
                        delay = min(delay * config.backoff_factor, config.max_delay)
                    else:
                        app_logger.error(
                            f"{func.__name__} failed after {config.max_attempts} attempts: {str(e)}"
                        )
            
            # All retries exhausted
            raise last_exception
        
        return wrapper
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern implementation for fault tolerance."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 60.0
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            success_threshold: Number of successes before closing circuit
            timeout: Timeout before attempting to close circuit (seconds)
        """
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == "open":
            # Check if timeout has passed
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
                app_logger.info("Circuit breaker transitioning to half-open state")
            else:
                raise Exception(f"Circuit breaker is open (opened at {self.last_failure_time})")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        
        if self.state == "half_open":
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = "closed"
                self.success_count = 0
                app_logger.info("Circuit breaker closed")
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            app_logger.error("Circuit breaker opened due to excessive failures")
        
        if self.state == "half_open":
            self.state = "open"
            app_logger.warning("Circuit breaker reopened (half-open test failed)")
    
    def reset(self):
        """Reset circuit breaker to closed state."""
        self.state = "closed"
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        app_logger.info("Circuit breaker reset")


class SafeExecutor:
    """Safely execute functions with error handling and fallbacks."""
    
    @staticmethod
    def execute_with_fallback(
        primary_func: Callable,
        fallback_func: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with fallback on failure.
        
        Args:
            primary_func: Primary function to execute
            fallback_func: Fallback function if primary fails
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Result from primary or fallback function
        """
        try:
            app_logger.debug(f"Executing primary function: {primary_func.__name__}")
            return primary_func(*args, **kwargs)
        except Exception as e:
            app_logger.warning(
                f"Primary function {primary_func.__name__} failed: {str(e)}"
            )
            
            if fallback_func:
                try:
                    app_logger.debug(f"Executing fallback function: {fallback_func.__name__}")
                    return fallback_func(*args, **kwargs)
                except Exception as fallback_error:
                    log_error(
                        f"Fallback function {fallback_func.__name__} also failed",
                        fallback_error
                    )
                    raise
            else:
                raise
    
    @staticmethod
    def execute_safely(
        func: Callable,
        default_return: Optional[Any] = None,
        log_error_msg: Optional[str] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function safely with error catching and default return.
        
        Args:
            func: Function to execute
            default_return: Value to return on error
            log_error_msg: Custom error message
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or default value
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = log_error_msg or f"Error in {func.__name__}: {str(e)}"
            log_error(error_msg, e)
            return default_return


def safe_call(func: Callable, *args, default: Any = None, **kwargs) -> Any:
    """
    Convenience function for safe function execution.
    
    Args:
        func: Function to call
        *args: Function arguments
        default: Default value on error
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default value
    """
    return SafeExecutor.execute_safely(func, default, None, *args, **kwargs)


# API-specific retry configuration
API_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=30.0,
    backoff_factor=2.0,
    exceptions=(
        ConnectionError,
        TimeoutError,
        IOError,
        OSError,
    )
)

# Circuit breaker for API calls
api_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    success_threshold=2,
    timeout=60.0
)
