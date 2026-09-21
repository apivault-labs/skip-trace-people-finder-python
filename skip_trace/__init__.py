"""Public Python client for the hosted Skip Trace Apify Actor.

Use only for a lawful purpose and never for FCRA-regulated decisions.
"""

from .client import SkipTraceClient
from .exceptions import (
    ActorRunError,
    ActorTimeoutError,
    AuthenticationError,
    SkipTraceError,
)

__version__ = "0.2.0"
__all__ = [
    "SkipTraceClient",
    "SkipTraceError",
    "AuthenticationError",
    "ActorRunError",
    "ActorTimeoutError",
]
