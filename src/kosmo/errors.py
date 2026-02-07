"""Error handling and graceful degradation for the Kosmo agent."""

from enum import Enum
from typing import Optional


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    WARNING = "warning"  # Non-critical, agent can continue
    RECOVERABLE = "recoverable"  # Error can be recovered with fallback
    CRITICAL = "critical"  # Agent cannot proceed


class ErrorCategory(Enum):
    """Categories of errors for better handling."""
    API_ERROR = "api_error"  # External API failures
    NETWORK_ERROR = "network_error"  # Connection issues
    RATE_LIMIT = "rate_limit"  # Rate limiting from APIs
    TIMEOUT = "timeout"  # Request timeouts
    AUTHENTICATION = "authentication"  # API key issues
    VALIDATION = "validation"  # Invalid input
    EXECUTION = "execution"  # Code execution errors
    NOT_FOUND = "not_found"  # Resource not found
    UNKNOWN = "unknown"  # Unclassified errors


class KosmoError(Exception):
    """Base exception for Kosmo agent errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.RECOVERABLE,
        original_error: Optional[Exception] = None,
        tool_name: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        """Initialize a Kosmo error.

        Args:
            message: Human-readable error message
            category: Category of the error
            severity: How critical the error is
            original_error: The underlying exception if any
            tool_name: Name of the tool that raised the error
            suggestion: Suggestion for recovery or alternative action
        """
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.original_error = original_error
        self.tool_name = tool_name
        self.suggestion = suggestion

    def __str__(self) -> str:
        parts = [self.message]
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
        return " | ".join(parts)

    def to_user_message(self) -> str:
        """Get a user-friendly error message."""
        if self.severity == ErrorSeverity.WARNING:
            prefix = "Note"
        elif self.severity == ErrorSeverity.RECOVERABLE:
            prefix = "Error (attempting recovery)"
        else:
            prefix = "Error"

        msg = f"{prefix}: {self.message}"
        if self.suggestion:
            msg += f"\n  → {self.suggestion}"
        return msg


class APIError(KosmoError):
    """Error from external API calls."""

    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        original_error: Optional[Exception] = None,
        suggestion: Optional[str] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.API_ERROR,
            severity=ErrorSeverity.RECOVERABLE,
            original_error=original_error,
            tool_name=tool_name,
            suggestion=suggestion or "Try using an alternative tool or rephrasing the query."
        )


class NetworkError(KosmoError):
    """Network connectivity errors."""

    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK_ERROR,
            severity=ErrorSeverity.RECOVERABLE,
            original_error=original_error,
            tool_name=tool_name,
            suggestion="Check your internet connection and try again."
        )


class RateLimitError(KosmoError):
    """Rate limiting error from APIs."""

    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        original_error: Optional[Exception] = None,
        retry_after: Optional[int] = None
    ):
        suggestion = "Wait a moment and try again."
        if retry_after:
            suggestion = f"Rate limited. Try again after {retry_after} seconds."

        super().__init__(
            message=message,
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.RECOVERABLE,
            original_error=original_error,
            tool_name=tool_name,
            suggestion=suggestion
        )
        self.retry_after = retry_after


class AuthenticationError(KosmoError):
    """API authentication/authorization errors."""

    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        missing_key: Optional[str] = None
    ):
        suggestion = "Check that your API keys are correctly configured in .env file."
        if missing_key:
            suggestion = f"Missing API key: {missing_key}. Add it to your .env file."

        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.CRITICAL,
            tool_name=tool_name,
            suggestion=suggestion
        )
        self.missing_key = missing_key


class ExecutionError(KosmoError):
    """Code execution errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.EXECUTION,
            severity=ErrorSeverity.RECOVERABLE,
            original_error=original_error,
            tool_name="execute_code",
            suggestion="Check the code for syntax errors or unsupported operations."
        )
        self.code = code


class TimeoutError(KosmoError):
    """Request timeout errors."""

    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        timeout_seconds: Optional[int] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.RECOVERABLE,
            tool_name=tool_name,
            suggestion="The request timed out. Try a simpler query or try again later."
        )
        self.timeout_seconds = timeout_seconds


# Error classification patterns
ERROR_PATTERNS = {
    ErrorCategory.RATE_LIMIT: [
        "rate limit",
        "too many requests",
        "quota exceeded",
        "429",
    ],
    ErrorCategory.TIMEOUT: [
        "timeout",
        "timed out",
        "connection timeout",
    ],
    ErrorCategory.NETWORK_ERROR: [
        "connection error",
        "network error",
        "unreachable",
        "connection refused",
        "dns resolution",
    ],
    ErrorCategory.AUTHENTICATION: [
        "api key not found",
        "unauthorized",
        "authentication failed",
        "invalid api key",
        "403",
        "401",
    ],
    ErrorCategory.NOT_FOUND: [
        "not found",
        "404",
        "no results",
        "does not exist",
    ],
    ErrorCategory.EXECUTION: [
        "syntax error",
        "execution error",
        "runtime error",
        "name error",
        "type error",
    ],
}


def classify_error(error_message: str) -> ErrorCategory:
    """Classify an error message into a category.

    Args:
        error_message: The error message string

    Returns:
        The error category
    """
    error_lower = error_message.lower()
    for category, patterns in ERROR_PATTERNS.items():
        if any(pattern in error_lower for pattern in patterns):
            return category
    return ErrorCategory.UNKNOWN


def is_transient_error(category: ErrorCategory) -> bool:
    """Check if an error category is transient (worth retrying).

    Args:
        category: The error category

    Returns:
        True if the error is transient
    """
    transient_categories = {
        ErrorCategory.RATE_LIMIT,
        ErrorCategory.TIMEOUT,
        ErrorCategory.NETWORK_ERROR,
    }
    return category in transient_categories


def get_fallback_suggestion(tool_name: str, category: ErrorCategory) -> str:
    """Get a fallback suggestion for a failed tool.

    Args:
        tool_name: Name of the tool that failed
        category: Category of the error

    Returns:
        Suggestion string for fallback action
    """
    fallbacks = {
        "web_search": {
            ErrorCategory.API_ERROR: "Try using search_wikipedia for basic facts instead.",
            ErrorCategory.RATE_LIMIT: "Wait and retry, or use search_wikipedia as a fallback.",
            ErrorCategory.AUTHENTICATION: "Check TAVILY_API_KEY in .env file.",
            ErrorCategory.NETWORK_ERROR: "Check internet connection. Use cached knowledge if available.",
        },
        "search_wikipedia": {
            ErrorCategory.NOT_FOUND: "Try a different search term or use web_search for broader results.",
            ErrorCategory.NETWORK_ERROR: "Check internet connection and retry.",
            ErrorCategory.TIMEOUT: "Wikipedia may be slow. Try again with a simpler query.",
        },
        "execute_code": {
            ErrorCategory.EXECUTION: "Review the code for errors. Try breaking into smaller steps.",
            ErrorCategory.TIMEOUT: "The code may be too complex. Simplify the computation.",
        },
        "create_plot": {
            ErrorCategory.EXECUTION: "Check matplotlib code syntax. Ensure plt.plot() or similar is called.",
        },
    }

    tool_fallbacks = fallbacks.get(tool_name, {})
    return tool_fallbacks.get(
        category,
        "Try an alternative approach or rephrase your query."
    )


class ErrorHandler:
    """Centralized error handler for the Kosmo agent."""

    def __init__(self, verbose: bool = True):
        """Initialize the error handler.

        Args:
            verbose: Whether to print detailed error information
        """
        self.verbose = verbose
        self.error_log: list = []

    def handle_tool_error(
        self,
        tool_name: str,
        error_message: str,
        original_error: Optional[Exception] = None
    ) -> str:
        """Handle an error from a tool and return a user-friendly message.

        Args:
            tool_name: Name of the tool that failed
            error_message: The error message
            original_error: The original exception if any

        Returns:
            User-friendly error message with suggestions
        """
        category = classify_error(error_message)
        is_transient = is_transient_error(category)
        suggestion = get_fallback_suggestion(tool_name, category)

        # Create error object for logging
        kosmo_error = KosmoError(
            message=error_message,
            category=category,
            severity=ErrorSeverity.RECOVERABLE if is_transient else ErrorSeverity.WARNING,
            original_error=original_error,
            tool_name=tool_name,
            suggestion=suggestion
        )

        # Log the error
        self.error_log.append({
            "tool": tool_name,
            "category": category.value,
            "message": error_message,
            "is_transient": is_transient,
        })

        if self.verbose:
            status = "⚠️ " if is_transient else "❌ "
            print(f"\n{status}Tool '{tool_name}' error ({category.value}): {error_message}")
            print(f"   Suggestion: {suggestion}")

        return kosmo_error.to_user_message()

    def should_retry(self, error_message: str) -> bool:
        """Determine if an error should trigger a retry.

        Args:
            error_message: The error message

        Returns:
            True if the operation should be retried
        """
        category = classify_error(error_message)
        return is_transient_error(category)

    def get_degradation_message(self, failed_tools: list) -> str:
        """Get a message about degraded functionality.

        Args:
            failed_tools: List of tool names that have failed

        Returns:
            Message describing current capabilities
        """
        if not failed_tools:
            return ""

        available_tools = {"web_search", "search_wikipedia", "execute_code", "create_plot"}
        working_tools = available_tools - set(failed_tools)

        if not working_tools:
            return "All tools are currently unavailable. I can only provide information from my training data."

        msg_parts = [f"Note: {', '.join(failed_tools)} {'is' if len(failed_tools) == 1 else 'are'} currently unavailable."]

        if "web_search" in failed_tools and "search_wikipedia" in working_tools:
            msg_parts.append("Using Wikipedia for fact lookup instead of web search.")
        if "create_plot" in failed_tools:
            msg_parts.append("Unable to generate visualizations. Providing numerical results only.")

        return " ".join(msg_parts)

    def clear_log(self):
        """Clear the error log."""
        self.error_log = []

    def get_error_summary(self) -> dict:
        """Get a summary of logged errors.

        Returns:
            Dictionary with error counts by category
        """
        summary = {}
        for error in self.error_log:
            category = error["category"]
            summary[category] = summary.get(category, 0) + 1
        return summary
