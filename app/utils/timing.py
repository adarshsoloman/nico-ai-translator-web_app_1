"""
Timing Utilities
Helper functions for measuring execution time
"""

import time
from contextlib import contextmanager


@contextmanager
def timer(name: str = "Operation"):
    """
    Context manager for timing operations
    
    Usage:
        with timer("Translation"):
            # do something
    """
    start = time.time()
    yield
    elapsed = (time.time() - start) * 1000  # Convert to milliseconds
    print(f"{name} took {elapsed:.2f}ms")


def format_time(seconds: float) -> str:
    """
    Format seconds into human-readable string
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.2f}s"
