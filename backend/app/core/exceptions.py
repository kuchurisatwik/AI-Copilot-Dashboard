"""
Trader Copilot AI — Custom Exception Classes

Defines domain-specific exceptions that map to HTTP error responses.
These are caught by the global exception handler in main.py.
"""

from typing import Any


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# ── Authentication Exceptions ────────────────────────────────────

class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, code="AUTH_FAILED", status_code=401)


class InvalidCredentialsError(AppException):
    """Raised when login credentials are incorrect."""

    def __init__(self):
        super().__init__(
            message="Invalid email or password",
            code="INVALID_CREDENTIALS",
            status_code=401,
        )


class UserAlreadyExistsError(AppException):
    """Raised when registering with an email that already exists."""

    def __init__(self, email: str):
        super().__init__(
            message=f"User with email '{email}' already exists",
            code="USER_EXISTS",
            status_code=409,
        )


# ── Resource Exceptions ──────────────────────────────────────────

class NotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str, identifier: str = ""):
        detail = f"{resource} not found"
        if identifier:
            detail = f"{resource} '{identifier}' not found"
        super().__init__(message=detail, code="NOT_FOUND", status_code=404)


class ForbiddenError(AppException):
    """Raised when user tries to access a resource they don't own."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message=message, code="FORBIDDEN", status_code=403)


# ── Risk Engine Exceptions ───────────────────────────────────────

class RiskLimitExceededError(AppException):
    """Raised when a trade violates risk limits."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            code="RISK_LIMIT_EXCEEDED",
            status_code=422,
            details=details,
        )


class RuleValidationBlockedError(AppException):
    """Raised when the Rule Engine blocks a trade."""

    def __init__(self, message: str, rule_results: list | None = None):
        super().__init__(
            message=message,
            code="TRADE_BLOCKED",
            status_code=422,
            details={"rule_results": rule_results or []},
        )


# ── Trade Exceptions ─────────────────────────────────────────────

class InvalidTradeStateError(AppException):
    """Raised when attempting an invalid trade state transition."""

    def __init__(self, current_state: str, attempted_action: str):
        super().__init__(
            message=f"Cannot {attempted_action} a trade in '{current_state}' state",
            code="INVALID_TRADE_STATE",
            status_code=422,
            details={"current_state": current_state, "attempted_action": attempted_action},
        )


# ── AI Exceptions ────────────────────────────────────────────────

class InsufficientDataError(AppException):
    """Raised when there isn't enough data for AI analysis."""

    def __init__(self, message: str = "Not enough historical data available for a reliable recommendation."):
        super().__init__(
            message=message,
            code="INSUFFICIENT_DATA",
            status_code=422,
        )


# ── Validation Exceptions ───────────────────────────────────────

class ValidationError(AppException):
    """Raised for general validation failures."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )

class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(message=detail, code="BAD_REQUEST", status_code=400)

class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(message=detail, code="UNAUTHORIZED", status_code=401)

class NotFoundException(AppException):
    def __init__(self, detail: str = "Not Found"):
        super().__init__(message=detail, code="NOT_FOUND", status_code=404)
