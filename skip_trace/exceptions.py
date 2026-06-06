"""Exception classes for the Skip Trace SDK."""


class SkipTraceError(Exception):
    """Base exception for all SDK errors."""


class AuthenticationError(SkipTraceError):
    """Raised when the Apify API token is missing or invalid."""


class ActorRunError(SkipTraceError):
    """Raised when the actor run fails on Apify infrastructure."""


class ActorTimeoutError(SkipTraceError):
    """Raised when the actor run does not finish within the allowed timeout."""
