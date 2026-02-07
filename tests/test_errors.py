"""Tests for error handling and graceful degradation."""

from kosmo.errors import (
    APIError,
    AuthenticationError,
    ErrorCategory,
    ErrorHandler,
    ErrorSeverity,
    ExecutionError,
    KosmoError,
    NetworkError,
    RateLimitError,
    TimeoutError,
    classify_error,
    get_fallback_suggestion,
    is_transient_error,
)

# =============================================================================
# Tests for ErrorSeverity enum
# =============================================================================

class TestErrorSeverity:
    """Tests for ErrorSeverity enum."""

    def test_warning_value(self):
        """Test WARNING severity value."""
        assert ErrorSeverity.WARNING.value == "warning"

    def test_recoverable_value(self):
        """Test RECOVERABLE severity value."""
        assert ErrorSeverity.RECOVERABLE.value == "recoverable"

    def test_critical_value(self):
        """Test CRITICAL severity value."""
        assert ErrorSeverity.CRITICAL.value == "critical"


# =============================================================================
# Tests for ErrorCategory enum
# =============================================================================

class TestErrorCategory:
    """Tests for ErrorCategory enum."""

    def test_api_error_value(self):
        """Test API_ERROR category value."""
        assert ErrorCategory.API_ERROR.value == "api_error"

    def test_network_error_value(self):
        """Test NETWORK_ERROR category value."""
        assert ErrorCategory.NETWORK_ERROR.value == "network_error"

    def test_rate_limit_value(self):
        """Test RATE_LIMIT category value."""
        assert ErrorCategory.RATE_LIMIT.value == "rate_limit"

    def test_timeout_value(self):
        """Test TIMEOUT category value."""
        assert ErrorCategory.TIMEOUT.value == "timeout"

    def test_authentication_value(self):
        """Test AUTHENTICATION category value."""
        assert ErrorCategory.AUTHENTICATION.value == "authentication"

    def test_validation_value(self):
        """Test VALIDATION category value."""
        assert ErrorCategory.VALIDATION.value == "validation"

    def test_execution_value(self):
        """Test EXECUTION category value."""
        assert ErrorCategory.EXECUTION.value == "execution"

    def test_not_found_value(self):
        """Test NOT_FOUND category value."""
        assert ErrorCategory.NOT_FOUND.value == "not_found"

    def test_unknown_value(self):
        """Test UNKNOWN category value."""
        assert ErrorCategory.UNKNOWN.value == "unknown"


# =============================================================================
# Tests for KosmoError base exception
# =============================================================================

class TestKosmoError:
    """Tests for KosmoError base exception."""

    def test_basic_initialization(self):
        """Test basic error initialization."""
        error = KosmoError("Test error message")
        assert error.message == "Test error message"
        assert error.category == ErrorCategory.UNKNOWN
        assert error.severity == ErrorSeverity.RECOVERABLE

    def test_full_initialization(self):
        """Test error with all parameters."""
        original = ValueError("Original error")
        error = KosmoError(
            message="Test error",
            category=ErrorCategory.API_ERROR,
            severity=ErrorSeverity.CRITICAL,
            original_error=original,
            tool_name="web_search",
            suggestion="Try again"
        )
        assert error.message == "Test error"
        assert error.category == ErrorCategory.API_ERROR
        assert error.severity == ErrorSeverity.CRITICAL
        assert error.original_error == original
        assert error.tool_name == "web_search"
        assert error.suggestion == "Try again"

    def test_str_without_suggestion(self):
        """Test string representation without suggestion."""
        error = KosmoError("Test error")
        assert str(error) == "Test error"

    def test_str_with_suggestion(self):
        """Test string representation with suggestion."""
        error = KosmoError("Test error", suggestion="Try again")
        assert str(error) == "Test error | Suggestion: Try again"

    def test_to_user_message_warning(self):
        """Test user message for warning severity."""
        error = KosmoError("Test", severity=ErrorSeverity.WARNING)
        assert error.to_user_message().startswith("Note:")

    def test_to_user_message_recoverable(self):
        """Test user message for recoverable severity."""
        error = KosmoError("Test", severity=ErrorSeverity.RECOVERABLE)
        assert "attempting recovery" in error.to_user_message()

    def test_to_user_message_critical(self):
        """Test user message for critical severity."""
        error = KosmoError("Test", severity=ErrorSeverity.CRITICAL)
        assert error.to_user_message().startswith("Error:")

    def test_to_user_message_with_suggestion(self):
        """Test user message includes suggestion."""
        error = KosmoError("Test", suggestion="Try again")
        assert "Try again" in error.to_user_message()


# =============================================================================
# Tests for specialized error classes
# =============================================================================

class TestAPIError:
    """Tests for APIError class."""

    def test_default_initialization(self):
        """Test API error with defaults."""
        error = APIError("API failed")
        assert error.category == ErrorCategory.API_ERROR
        assert error.severity == ErrorSeverity.RECOVERABLE
        assert "alternative tool" in error.suggestion.lower()

    def test_with_tool_name(self):
        """Test API error with tool name."""
        error = APIError("API failed", tool_name="web_search")
        assert error.tool_name == "web_search"

    def test_custom_suggestion(self):
        """Test API error with custom suggestion."""
        error = APIError("API failed", suggestion="Custom suggestion")
        assert error.suggestion == "Custom suggestion"


class TestNetworkError:
    """Tests for NetworkError class."""

    def test_default_initialization(self):
        """Test network error with defaults."""
        error = NetworkError("Connection failed")
        assert error.category == ErrorCategory.NETWORK_ERROR
        assert error.severity == ErrorSeverity.RECOVERABLE
        assert "internet connection" in error.suggestion.lower()

    def test_with_original_error(self):
        """Test network error with original exception."""
        original = ConnectionError("DNS failed")
        error = NetworkError("Connection failed", original_error=original)
        assert error.original_error == original


class TestRateLimitError:
    """Tests for RateLimitError class."""

    def test_default_initialization(self):
        """Test rate limit error with defaults."""
        error = RateLimitError("Too many requests")
        assert error.category == ErrorCategory.RATE_LIMIT
        assert error.severity == ErrorSeverity.RECOVERABLE
        assert error.retry_after is None

    def test_with_retry_after(self):
        """Test rate limit error with retry after."""
        error = RateLimitError("Too many requests", retry_after=60)
        assert error.retry_after == 60
        assert "60 seconds" in error.suggestion


class TestAuthenticationError:
    """Tests for AuthenticationError class."""

    def test_default_initialization(self):
        """Test auth error with defaults."""
        error = AuthenticationError("Unauthorized")
        assert error.category == ErrorCategory.AUTHENTICATION
        assert error.severity == ErrorSeverity.CRITICAL
        assert ".env" in error.suggestion

    def test_with_missing_key(self):
        """Test auth error with missing key."""
        error = AuthenticationError("Key not found", missing_key="OPENAI_API_KEY")
        assert error.missing_key == "OPENAI_API_KEY"
        assert "OPENAI_API_KEY" in error.suggestion


class TestExecutionError:
    """Tests for ExecutionError class."""

    def test_default_initialization(self):
        """Test execution error with defaults."""
        error = ExecutionError("Syntax error")
        assert error.category == ErrorCategory.EXECUTION
        assert error.tool_name == "execute_code"
        assert "syntax errors" in error.suggestion.lower()

    def test_with_code(self):
        """Test execution error with code."""
        error = ExecutionError("Syntax error", code="print('hello'")
        assert error.code == "print('hello'"


class TestTimeoutError:
    """Tests for TimeoutError class."""

    def test_default_initialization(self):
        """Test timeout error with defaults."""
        error = TimeoutError("Request timed out")
        assert error.category == ErrorCategory.TIMEOUT
        assert error.severity == ErrorSeverity.RECOVERABLE
        assert "timed out" in error.suggestion.lower()

    def test_with_timeout_seconds(self):
        """Test timeout error with timeout value."""
        error = TimeoutError("Timed out", timeout_seconds=30)
        assert error.timeout_seconds == 30


# =============================================================================
# Tests for classify_error function
# =============================================================================

class TestClassifyError:
    """Tests for classify_error function."""

    def test_rate_limit_detection(self):
        """Test detection of rate limit errors."""
        assert classify_error("Rate limit exceeded") == ErrorCategory.RATE_LIMIT
        assert classify_error("Too many requests") == ErrorCategory.RATE_LIMIT
        assert classify_error("Quota exceeded for today") == ErrorCategory.RATE_LIMIT

    def test_timeout_detection(self):
        """Test detection of timeout errors."""
        assert classify_error("Request timeout") == ErrorCategory.TIMEOUT
        assert classify_error("Connection timed out") == ErrorCategory.TIMEOUT

    def test_network_error_detection(self):
        """Test detection of network errors."""
        assert classify_error("Connection error occurred") == ErrorCategory.NETWORK_ERROR
        assert classify_error("Network error") == ErrorCategory.NETWORK_ERROR
        assert classify_error("Host unreachable") == ErrorCategory.NETWORK_ERROR

    def test_authentication_detection(self):
        """Test detection of auth errors."""
        assert classify_error("API key not found") == ErrorCategory.AUTHENTICATION
        assert classify_error("Unauthorized access") == ErrorCategory.AUTHENTICATION
        assert classify_error("Invalid API key") == ErrorCategory.AUTHENTICATION
        assert classify_error("Error 401") == ErrorCategory.AUTHENTICATION

    def test_not_found_detection(self):
        """Test detection of not found errors."""
        assert classify_error("Resource not found") == ErrorCategory.NOT_FOUND
        assert classify_error("Error 404") == ErrorCategory.NOT_FOUND
        assert classify_error("No results found") == ErrorCategory.NOT_FOUND

    def test_execution_error_detection(self):
        """Test detection of execution errors."""
        assert classify_error("Syntax error in code") == ErrorCategory.EXECUTION
        assert classify_error("Runtime error occurred") == ErrorCategory.EXECUTION
        assert classify_error("Name error: x is not defined") == ErrorCategory.EXECUTION

    def test_unknown_error(self):
        """Test unknown error classification."""
        assert classify_error("Some random error") == ErrorCategory.UNKNOWN

    def test_case_insensitive(self):
        """Test case insensitive matching."""
        assert classify_error("RATE LIMIT") == ErrorCategory.RATE_LIMIT
        assert classify_error("TIMEOUT") == ErrorCategory.TIMEOUT


# =============================================================================
# Tests for is_transient_error function
# =============================================================================

class TestIsTransientError:
    """Tests for is_transient_error function."""

    def test_rate_limit_is_transient(self):
        """Test that rate limit is transient."""
        assert is_transient_error(ErrorCategory.RATE_LIMIT) is True

    def test_timeout_is_transient(self):
        """Test that timeout is transient."""
        assert is_transient_error(ErrorCategory.TIMEOUT) is True

    def test_network_error_is_transient(self):
        """Test that network error is transient."""
        assert is_transient_error(ErrorCategory.NETWORK_ERROR) is True

    def test_authentication_not_transient(self):
        """Test that authentication error is not transient."""
        assert is_transient_error(ErrorCategory.AUTHENTICATION) is False

    def test_execution_not_transient(self):
        """Test that execution error is not transient."""
        assert is_transient_error(ErrorCategory.EXECUTION) is False

    def test_unknown_not_transient(self):
        """Test that unknown error is not transient."""
        assert is_transient_error(ErrorCategory.UNKNOWN) is False


# =============================================================================
# Tests for get_fallback_suggestion function
# =============================================================================

class TestGetFallbackSuggestion:
    """Tests for get_fallback_suggestion function."""

    def test_web_search_api_error(self):
        """Test fallback for web_search API error."""
        suggestion = get_fallback_suggestion("web_search", ErrorCategory.API_ERROR)
        assert "wikipedia" in suggestion.lower()

    def test_web_search_auth_error(self):
        """Test fallback for web_search auth error."""
        suggestion = get_fallback_suggestion("web_search", ErrorCategory.AUTHENTICATION)
        assert "TAVILY_API_KEY" in suggestion

    def test_wikipedia_not_found(self):
        """Test fallback for wikipedia not found."""
        suggestion = get_fallback_suggestion("search_wikipedia", ErrorCategory.NOT_FOUND)
        assert "web_search" in suggestion.lower()

    def test_execute_code_error(self):
        """Test fallback for code execution error."""
        suggestion = get_fallback_suggestion("execute_code", ErrorCategory.EXECUTION)
        assert "code" in suggestion.lower()

    def test_create_plot_error(self):
        """Test fallback for plot creation error."""
        suggestion = get_fallback_suggestion("create_plot", ErrorCategory.EXECUTION)
        assert "matplotlib" in suggestion.lower() or "plt" in suggestion.lower()

    def test_unknown_tool(self):
        """Test fallback for unknown tool."""
        suggestion = get_fallback_suggestion("unknown_tool", ErrorCategory.UNKNOWN)
        assert "alternative" in suggestion.lower()


# =============================================================================
# Tests for ErrorHandler class
# =============================================================================

class TestErrorHandler:
    """Tests for ErrorHandler class."""

    def test_initialization_verbose(self):
        """Test handler initialization with verbose."""
        handler = ErrorHandler(verbose=True)
        assert handler.verbose is True
        assert handler.error_log == []

    def test_initialization_quiet(self):
        """Test handler initialization without verbose."""
        handler = ErrorHandler(verbose=False)
        assert handler.verbose is False

    def test_handle_tool_error_logs(self):
        """Test that handle_tool_error logs errors."""
        handler = ErrorHandler(verbose=False)
        handler.handle_tool_error("web_search", "Rate limit exceeded")
        assert len(handler.error_log) == 1
        assert handler.error_log[0]["tool"] == "web_search"
        assert handler.error_log[0]["category"] == "rate_limit"

    def test_handle_tool_error_returns_message(self):
        """Test that handle_tool_error returns user message."""
        handler = ErrorHandler(verbose=False)
        msg = handler.handle_tool_error("web_search", "Connection error")
        assert "Connection error" in msg

    def test_should_retry_transient(self):
        """Test should_retry for transient errors."""
        handler = ErrorHandler()
        assert handler.should_retry("Rate limit exceeded") is True
        assert handler.should_retry("Timeout error") is True

    def test_should_retry_permanent(self):
        """Test should_retry for permanent errors."""
        handler = ErrorHandler()
        assert handler.should_retry("API key not found") is False
        assert handler.should_retry("Syntax error") is False

    def test_get_degradation_message_empty(self):
        """Test degradation message with no failures."""
        handler = ErrorHandler()
        msg = handler.get_degradation_message([])
        assert msg == ""

    def test_get_degradation_message_single_tool(self):
        """Test degradation message with one failed tool."""
        handler = ErrorHandler()
        msg = handler.get_degradation_message(["web_search"])
        assert "web_search" in msg
        assert "unavailable" in msg.lower()

    def test_get_degradation_message_multiple_tools(self):
        """Test degradation message with multiple failed tools."""
        handler = ErrorHandler()
        msg = handler.get_degradation_message(["web_search", "create_plot"])
        assert "web_search" in msg
        assert "create_plot" in msg
        assert "are" in msg  # plural form

    def test_get_degradation_message_web_search_fallback(self):
        """Test degradation message mentions Wikipedia fallback."""
        handler = ErrorHandler()
        msg = handler.get_degradation_message(["web_search"])
        assert "wikipedia" in msg.lower()

    def test_get_degradation_message_plot_fallback(self):
        """Test degradation message for plot failure."""
        handler = ErrorHandler()
        msg = handler.get_degradation_message(["create_plot"])
        assert "visualization" in msg.lower()

    def test_get_degradation_message_all_tools(self):
        """Test degradation message when all tools fail."""
        handler = ErrorHandler()
        all_tools = ["web_search", "search_wikipedia", "execute_code", "create_plot"]
        msg = handler.get_degradation_message(all_tools)
        assert "training data" in msg.lower()

    def test_clear_log(self):
        """Test clearing the error log."""
        handler = ErrorHandler(verbose=False)
        handler.handle_tool_error("test", "error")
        assert len(handler.error_log) == 1
        handler.clear_log()
        assert len(handler.error_log) == 0

    def test_get_error_summary_empty(self):
        """Test error summary with no errors."""
        handler = ErrorHandler()
        summary = handler.get_error_summary()
        assert summary == {}

    def test_get_error_summary_single_category(self):
        """Test error summary with one category."""
        handler = ErrorHandler(verbose=False)
        handler.handle_tool_error("test", "Rate limit exceeded")
        handler.handle_tool_error("test", "Rate limit hit again")
        summary = handler.get_error_summary()
        assert summary == {"rate_limit": 2}

    def test_get_error_summary_multiple_categories(self):
        """Test error summary with multiple categories."""
        handler = ErrorHandler(verbose=False)
        handler.handle_tool_error("test", "Rate limit exceeded")
        handler.handle_tool_error("test", "Connection timeout")
        summary = handler.get_error_summary()
        assert summary == {"rate_limit": 1, "timeout": 1}


# =============================================================================
# Tests for agent integration
# =============================================================================

class TestAgentErrorIntegration:
    """Tests for error handling integration with agent."""

    def test_agent_has_error_handler(self):
        """Test that agent initializes with error handler."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        assert hasattr(agent, '_error_handler')
        assert isinstance(agent._error_handler, ErrorHandler)

    def test_agent_has_failed_tools_set(self):
        """Test that agent initializes with failed tools set."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        assert hasattr(agent, '_failed_tools')
        assert agent._failed_tools == set()

    def test_agent_graceful_degradation_default(self):
        """Test that graceful degradation is enabled by default."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        assert agent.graceful_degradation is True

    def test_agent_graceful_degradation_disabled(self):
        """Test that graceful degradation can be disabled."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False, graceful_degradation=False)
        assert agent.graceful_degradation is False

    def test_agent_get_failed_tools(self):
        """Test getting failed tools."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        failed = agent.get_failed_tools()
        assert failed == set()

    def test_agent_get_failed_tools_returns_copy(self):
        """Test that get_failed_tools returns a copy."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        agent._failed_tools.add("test_tool")
        failed = agent.get_failed_tools()
        failed.add("another_tool")
        assert "another_tool" not in agent._failed_tools

    def test_agent_reset_failed_tools(self):
        """Test resetting failed tools."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        agent._failed_tools.add("test_tool")
        agent.reset_failed_tools()
        assert agent._failed_tools == set()

    def test_agent_get_degradation_status(self):
        """Test getting degradation status."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        agent._failed_tools.add("web_search")
        status = agent.get_degradation_status()
        assert "web_search" in status

    def test_agent_get_error_summary(self):
        """Test getting error summary from agent."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        summary = agent.get_error_summary()
        assert summary == {}

    def test_agent_is_tool_error_empty(self):
        """Test _is_tool_error with empty content."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        assert agent._is_tool_error("") is True

    def test_agent_is_tool_error_success(self):
        """Test _is_tool_error with success content."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        assert agent._is_tool_error("Result: 42") is False

    def test_agent_is_tool_error_error_message(self):
        """Test _is_tool_error with error content."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        assert agent._is_tool_error("Error: Something went wrong") is True

    def test_agent_build_retry_message_tool_failure(self):
        """Test _build_retry_message for tool failure."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        agent._failed_tools.add("web_search")
        msg = agent._build_retry_message("tool_failure")
        assert "web_search" in msg
        assert "alternative" in msg.lower()

    def test_agent_build_retry_message_empty_response(self):
        """Test _build_retry_message for empty response."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        msg = agent._build_retry_message("empty_response")
        assert "complete answer" in msg.lower()

    def test_agent_format_degraded_response_no_failures(self):
        """Test _format_degraded_response with no failures."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        response = agent._format_degraded_response("Test response")
        assert response == "Test response"

    def test_agent_format_degraded_response_with_failures(self):
        """Test _format_degraded_response with failures."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        agent._failed_tools.add("web_search")
        response = agent._format_degraded_response("Test response")
        assert "Test response" in response
        assert "web_search" in response

    def test_agent_format_error_response_auth(self):
        """Test _format_error_response for auth error."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        response = agent._format_error_response("API key not found")
        assert ".env" in response

    def test_agent_format_error_response_network(self):
        """Test _format_error_response for network error."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        response = agent._format_error_response("Connection error")
        assert "internet connection" in response.lower()

    def test_agent_format_error_response_rate_limit(self):
        """Test _format_error_response for rate limit."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(verbose=False)
        response = agent._format_error_response("Rate limit exceeded")
        assert "rate-limited" in response.lower()
