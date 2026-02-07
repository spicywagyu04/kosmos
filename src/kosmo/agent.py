"""ReAct agent for cosmology research."""

import copy
import os
import time
import uuid
from typing import Dict, List, Optional, Set, Tuple

from dotenv import load_dotenv
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from .errors import ErrorHandler, classify_error, is_transient_error
from .prompts import REACT_SYSTEM_PROMPT, enhance_prompt_for_topic
from .tools import create_plot, execute_code, search_wikipedia, web_search

# Load environment variables
load_dotenv()

# Maximum iterations for the ReAct loop
MAX_ITERATIONS = 10

# Maximum retries for failed tool calls
MAX_RETRIES = 3

# Delay between retries (seconds)
RETRY_DELAY = 1.0

# Keywords indicating incomplete or failed results
INCOMPLETE_INDICATORS = [
    "error:",
    "failed to",
    "could not",
    "unable to",
    "no results found",
    "api key not found",
    "rate limit",
    "timeout",
    "connection error",
]


def _is_result_incomplete(result: str) -> bool:
    """Check if a tool result indicates failure or incomplete data.

    Args:
        result: The string result from a tool execution

    Returns:
        True if the result appears to be incomplete or failed
    """
    if not result:
        return True
    result_lower = result.lower()
    return any(indicator in result_lower for indicator in INCOMPLETE_INDICATORS)


def _wrap_tool_with_retry(tool_func, max_retries: int = MAX_RETRIES):
    """Wrap a tool function with retry logic.

    Args:
        tool_func: The original tool function
        max_retries: Maximum number of retry attempts

    Returns:
        A wrapped function that retries on failure
    """
    def wrapped_func(*args, **kwargs) -> str:
        last_error = None
        for attempt in range(max_retries):
            try:
                result = tool_func(*args, **kwargs)
                # Check if result indicates a transient failure
                if _is_result_incomplete(result) and attempt < max_retries - 1:
                    # Only retry for transient errors, not for "no results" type responses
                    if any(
                        err in result.lower()
                        for err in ["rate limit", "timeout", "connection error", "api error"]
                    ):
                        time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
                        continue
                return result
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                return f"Error after {max_retries} attempts: {str(last_error)}"
        return result if 'result' in locals() else f"Failed after {max_retries} attempts"
    return wrapped_func


def create_tools(with_retry: bool = True) -> List[Tool]:
    """Create the tool list for the agent.

    Args:
        with_retry: Whether to wrap tools with retry logic (default: True)

    Returns:
        List of Tool objects for the agent
    """
    # Optionally wrap tool functions with retry logic
    ws_func = _wrap_tool_with_retry(web_search) if with_retry else web_search
    ec_func = _wrap_tool_with_retry(execute_code) if with_retry else execute_code
    sw_func = _wrap_tool_with_retry(search_wikipedia) if with_retry else search_wikipedia
    cp_func = _wrap_tool_with_retry(create_plot) if with_retry else create_plot

    return [
        Tool(
            name="web_search",
            func=ws_func,
            description="Search the web for scientific papers, NASA data, and current research. Input should be a search query string."
        ),
        Tool(
            name="execute_code",
            func=ec_func,
            description="Execute Python code for physics calculations. NumPy and SymPy are available, along with physics constants (G, c, M_sun, M_earth, R_earth, AU). Input should be valid Python code."
        ),
        Tool(
            name="search_wikipedia",
            func=sw_func,
            description="Retrieve scientific facts and definitions from Wikipedia. Input should be a topic or term to look up."
        ),
        Tool(
            name="create_plot",
            func=cp_func,
            description="Generate visualizations using Matplotlib. Input should be Python code that creates a matplotlib figure using plt."
        ),
    ]


class KosmoAgent:
    """Cosmology Research Agent using ReAct pattern."""

    def __init__(
        self,
        verbose: bool = True,
        max_retries: int = MAX_RETRIES,
        with_tool_retry: bool = True,
        use_topic_prompts: bool = True,
        enable_memory: bool = True,
        graceful_degradation: bool = True
    ):
        """Initialize the agent.

        Args:
            verbose: Whether to print intermediate steps (default: True)
            max_retries: Maximum retry attempts for incomplete results (default: 3)
            with_tool_retry: Whether to enable retry logic for tool calls (default: True)
            use_topic_prompts: Whether to use topic-specific prompt templates (default: True)
            enable_memory: Whether to enable session memory for multi-turn conversations (default: True)
            graceful_degradation: Whether to enable graceful degradation on tool failures (default: True)
        """
        self.verbose = verbose
        self.max_retries = max_retries
        self.with_tool_retry = with_tool_retry
        self.use_topic_prompts = use_topic_prompts
        self.enable_memory = enable_memory
        self.graceful_degradation = graceful_degradation
        self.messages: List = []
        # Cache agents by prompt to avoid recreating for same topic
        self._agents: dict = {}
        self._llm = None
        self._tools = None
        # Session memory using LangGraph checkpointer
        self._checkpointer: Optional[InMemorySaver] = None
        self._current_thread_id: str = str(uuid.uuid4())
        # Store session metadata (thread_id -> session info)
        self._sessions: Dict[str, dict] = {}
        # Error handling
        self._error_handler = ErrorHandler(verbose=verbose)
        self._failed_tools: Set[str] = set()

    def _get_llm(self):
        """Get or create the LLM instance."""
        if self._llm is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")

            self._llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=api_key
            )
        return self._llm

    def _get_tools(self):
        """Get or create the tools list."""
        if self._tools is None:
            self._tools = create_tools(with_retry=self.with_tool_retry)
        return self._tools

    def _get_checkpointer(self) -> Optional[InMemorySaver]:
        """Get or create the checkpointer for session memory.

        Returns:
            InMemorySaver instance if memory is enabled, None otherwise
        """
        if not self.enable_memory:
            return None
        if self._checkpointer is None:
            self._checkpointer = InMemorySaver()
        return self._checkpointer

    def _get_agent(self, system_prompt: str):
        """Get or create the ReAct agent for a given system prompt.

        Args:
            system_prompt: The system prompt to use for the agent

        Returns:
            The ReAct agent instance
        """
        # Use prompt as cache key
        if system_prompt not in self._agents:
            llm = self._get_llm()
            tools = self._get_tools()
            checkpointer = self._get_checkpointer()

            # Create ReAct agent using langgraph with optional checkpointer
            self._agents[system_prompt] = create_react_agent(
                llm,
                tools,
                state_modifier=system_prompt,
                checkpointer=checkpointer
            )

        return self._agents[system_prompt]

    def _check_response_complete(self, response: str) -> Tuple[bool, Optional[str]]:
        """Check if the agent's response is complete or needs retry.

        Args:
            response: The agent's response string

        Returns:
            Tuple of (is_complete, retry_reason)
        """
        if not response or response == "No response generated.":
            return False, "empty_response"

        response_lower = response.lower()

        # Check for explicit failure indicators
        failure_phrases = [
            "i was unable to",
            "i couldn't complete",
            "the tool failed",
            "error occurred",
            "i apologize, but i cannot",
        ]
        for phrase in failure_phrases:
            if phrase in response_lower:
                return False, "tool_failure"

        return True, None

    def query(self, question: str, thread_id: Optional[str] = None) -> str:
        """Run a query through the agent with retry logic for incomplete results.

        Args:
            question: The user's question about cosmology/astrophysics
            thread_id: Optional thread ID for session continuity. If not provided,
                      uses the current thread ID. Pass a new ID to start a new session.

        Returns:
            The agent's response
        """
        # Determine the appropriate system prompt based on the query topic
        if self.use_topic_prompts:
            system_prompt = enhance_prompt_for_topic(REACT_SYSTEM_PROMPT, question)
        else:
            system_prompt = REACT_SYSTEM_PROMPT

        # Add degradation context if tools have failed
        if self.graceful_degradation and self._failed_tools:
            degradation_msg = self.get_degradation_status()
            if degradation_msg:
                system_prompt += f"\n\nNote: {degradation_msg}"

        agent = self._get_agent(system_prompt)

        # Use provided thread_id or current thread
        effective_thread_id = thread_id or self._current_thread_id

        # Track session
        if effective_thread_id not in self._sessions:
            self._sessions[effective_thread_id] = {
                "created_at": time.time(),
                "query_count": 0
            }
        self._sessions[effective_thread_id]["query_count"] += 1
        self._sessions[effective_thread_id]["last_query_at"] = time.time()

        # Add user message to history (for legacy compatibility)
        self.messages.append({"role": "user", "content": question})

        last_response = "No response generated."
        current_message = question

        for attempt in range(self.max_retries):
            try:
                # Build config with recursion limit and thread_id for memory
                config = {"recursion_limit": MAX_ITERATIONS * 2}
                if self.enable_memory:
                    config["configurable"] = {"thread_id": effective_thread_id}

                result = agent.invoke(
                    {"messages": [{"role": "user", "content": current_message}]},
                    config=config
                )

                # Extract the final response
                output_messages = result.get("messages", [])
                response = self._extract_response(output_messages)

                if response:
                    # Store the updated message history
                    self.messages = output_messages
                    if self.verbose:
                        self._print_steps(output_messages)

                    # Check if response is complete
                    is_complete, retry_reason = self._check_response_complete(response)

                    if is_complete:
                        # Add degradation notice if needed
                        if self.graceful_degradation and self._failed_tools:
                            degradation_notice = self.get_degradation_status()
                            if degradation_notice and degradation_notice not in response:
                                response = f"{response}\n\n---\n{degradation_notice}"
                        return response

                    # Response incomplete - decide whether to retry
                    last_response = response
                    if attempt < self.max_retries - 1:
                        if self.verbose:
                            print(f"\n⚠️  Response incomplete ({retry_reason}), retrying... "
                                  f"(attempt {attempt + 2}/{self.max_retries})")

                        # Set the next message to be a retry prompt with fallback suggestions
                        retry_message = self._build_retry_message(retry_reason)
                        current_message = retry_message
                        self.messages.append({"role": "user", "content": retry_message})
                        time.sleep(RETRY_DELAY)
                        continue

                    # Max retries reached, return best response with degradation notice
                    return self._format_degraded_response(last_response)

            except Exception as e:
                error_str = str(e)
                category = classify_error(error_str)
                should_retry = is_transient_error(category) and attempt < self.max_retries - 1

                if should_retry:
                    if self.verbose:
                        print(f"\n⚠️  Error ({category.value}): {e}, retrying... "
                              f"(attempt {attempt + 2}/{self.max_retries})")
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue

                # Non-recoverable error
                return self._format_error_response(error_str)

        return self._format_degraded_response(last_response)

    def _build_retry_message(self, retry_reason: Optional[str]) -> str:
        """Build a retry message based on the failure reason.

        Args:
            retry_reason: The reason for retrying

        Returns:
            A message prompting the agent to retry
        """
        base_msg = "Please try again to complete the previous request."

        if retry_reason == "tool_failure":
            if self._failed_tools:
                failed_list = ", ".join(self._failed_tools)
                return (
                    f"{base_msg} The following tools have failed: {failed_list}. "
                    "Please try an alternative approach using different tools or "
                    "provide the best answer you can with available information."
                )
            return f"{base_msg} If a tool failed, try an alternative approach."

        if retry_reason == "empty_response":
            return f"{base_msg} Please provide a complete answer."

        return f"{base_msg} Try an alternative approach if needed."

    def _format_degraded_response(self, response: str) -> str:
        """Format a response with degradation notices.

        Args:
            response: The agent response

        Returns:
            Response with degradation notices if applicable
        """
        if self.graceful_degradation and self._failed_tools:
            degradation_notice = self.get_degradation_status()
            if degradation_notice and degradation_notice not in response:
                return f"{response}\n\n---\n{degradation_notice}"
        return response

    def _format_error_response(self, error: str) -> str:
        """Format an error response with helpful information.

        Args:
            error: The error string

        Returns:
            User-friendly error response
        """
        category = classify_error(error)
        msg = f"I encountered an error while processing your request: {error}\n"

        if category.value == "authentication":
            msg += "\nPlease check that your API keys are correctly configured in the .env file."
        elif category.value == "network_error":
            msg += "\nPlease check your internet connection and try again."
        elif category.value == "rate_limit":
            msg += "\nThe service is rate-limited. Please wait a moment and try again."
        else:
            msg += "\nPlease try rephrasing your question or try again later."

        return msg

    def _extract_response(self, messages: List) -> Optional[str]:
        """Extract the final AI response from message list.

        Args:
            messages: List of messages from agent execution

        Returns:
            The last AI message content, or None if not found
        """
        if not messages:
            return None

        # Get the last AI message
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content:
                # Skip tool messages, we want the final AI response
                if hasattr(msg, 'type') and msg.type == 'tool':
                    continue
                return msg.content

        return None

    def _print_steps(self, messages: List):
        """Print intermediate reasoning steps if verbose."""
        current_tool_name = None
        for msg in messages:
            if hasattr(msg, 'type'):
                if msg.type == 'ai' and hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        current_tool_name = tool_call.get('name', 'unknown')
                        print(f"\n🔧 Tool: {current_tool_name}")
                        print(f"   Input: {tool_call.get('args', {})}")
                elif msg.type == 'tool':
                    content = msg.content
                    # Check for errors and track failed tools
                    if self._is_tool_error(content):
                        if current_tool_name:
                            self._handle_tool_failure(current_tool_name, content)
                    if len(content) > 200:
                        content = content[:200] + "..."
                    print(f"   Result: {content}")

    def _is_tool_error(self, content: str) -> bool:
        """Check if tool output indicates an error.

        Args:
            content: The tool output content

        Returns:
            True if the content indicates an error
        """
        if not content:
            return True
        return content.lower().startswith("error")

    def _handle_tool_failure(self, tool_name: str, error_message: str):
        """Handle a tool failure with graceful degradation.

        Args:
            tool_name: Name of the failed tool
            error_message: The error message from the tool
        """
        if self.graceful_degradation:
            self._failed_tools.add(tool_name)
            self._error_handler.handle_tool_error(tool_name, error_message)

    def get_failed_tools(self) -> Set[str]:
        """Get the set of tools that have failed in this session.

        Returns:
            Set of tool names that have failed
        """
        return self._failed_tools.copy()

    def reset_failed_tools(self):
        """Reset the set of failed tools."""
        self._failed_tools.clear()
        self._error_handler.clear_log()

    def get_degradation_status(self) -> str:
        """Get a message about current degraded functionality.

        Returns:
            Message describing which tools are unavailable
        """
        return self._error_handler.get_degradation_message(list(self._failed_tools))

    def get_error_summary(self) -> dict:
        """Get a summary of errors that occurred.

        Returns:
            Dictionary with error counts by category
        """
        return self._error_handler.get_error_summary()

    def clear_memory(self):
        """Clear the conversation memory for the current session.

        This clears the local message history but does not affect the
        checkpointer's stored state. Use new_session() to start fresh.
        """
        self.messages = []

    def new_session(self) -> str:
        """Start a new conversation session.

        Creates a new thread ID for session memory, allowing a fresh
        conversation without prior context.

        Returns:
            The new thread ID for the session
        """
        self._current_thread_id = str(uuid.uuid4())
        self.messages = []
        return self._current_thread_id

    def get_current_thread_id(self) -> str:
        """Get the current thread ID for session tracking.

        Returns:
            The current thread ID
        """
        return self._current_thread_id

    def set_thread_id(self, thread_id: str) -> None:
        """Set the current thread ID to continue a previous session.

        Args:
            thread_id: The thread ID to resume
        """
        self._current_thread_id = thread_id

    def get_session_info(self, thread_id: Optional[str] = None) -> Optional[dict]:
        """Get information about a session.

        Args:
            thread_id: The thread ID to look up. Uses current thread if not provided.

        Returns:
            Session info dict or None if session not found
        """
        tid = thread_id or self._current_thread_id
        return self._sessions.get(tid)

    def list_sessions(self) -> Dict[str, dict]:
        """List all tracked sessions.

        Returns:
            Dictionary mapping thread IDs to session info (deep copy)
        """
        return copy.deepcopy(self._sessions)
