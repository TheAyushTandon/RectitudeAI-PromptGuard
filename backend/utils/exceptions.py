"""Custom exceptions."""


class RectitudeAIException(Exception):
    """Base exception for RectitudeAI."""
    pass


class AuthenticationError(RectitudeAIException):
    """Authentication failed."""
    pass


class RateLimitError(RectitudeAIException):
    """Rate limit exceeded."""
    pass


class LLMError(RectitudeAIException):
    """LLM generation error."""
    pass


class SecurityBlockError(RectitudeAIException):
    """Request blocked by security layer."""
    pass


class InjectionDetectedError(SecurityBlockError):
    """Prompt injection detected."""
    pass


class AnomalyDetectedError(SecurityBlockError):
    """Anomalous behavior detected."""
    pass


class PolicyViolationError(SecurityBlockError):
    """Policy violation detected."""
    pass
