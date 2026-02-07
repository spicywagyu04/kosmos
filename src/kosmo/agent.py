"""ReAct agent for cosmology research."""

import os
import time
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from .prompts import REACT_SYSTEM_PROMPT
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
        with_tool_retry: bool = True
    ):
        """Initialize the agent.

        Args:
            verbose: Whether to print intermediate steps (default: True)
            max_retries: Maximum retry attempts for incomplete results (default: 3)
            with_tool_retry: Whether to enable retry logic for tool calls (default: True)
        """
        self.verbose = verbose
        self.max_retries = max_retries
        self.with_tool_retry = with_tool_retry
        self.messages: List = []
        self._agent = None

    def _get_agent(self):
        """Get or create the ReAct agent."""
        if self._agent is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")

            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=api_key
            )

            tools = create_tools(with_retry=self.with_tool_retry)

            # Create ReAct agent using langgraph
            self._agent = create_react_agent(
                llm,
                tools,
                state_modifier=REACT_SYSTEM_PROMPT
            )

        return self._agent

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

    def query(self, question: str) -> str:
        """Run a query through the agent with retry logic for incomplete results.

        Args:
            question: The user's question about cosmology/astrophysics

        Returns:
            The agent's response
        """
        agent = self._get_agent()

        # Add user message to history
        self.messages.append({"role": "user", "content": question})

        last_response = "No response generated."

        for attempt in range(self.max_retries):
            try:
                # Invoke the agent
                config = {"recursion_limit": MAX_ITERATIONS * 2}
                result = agent.invoke(
                    {"messages": self.messages},
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
                        return response

                    # Response incomplete - decide whether to retry
                    last_response = response
                    if attempt < self.max_retries - 1:
                        if self.verbose:
                            print(f"\n⚠️  Response incomplete ({retry_reason}), retrying... "
                                  f"(attempt {attempt + 2}/{self.max_retries})")

                        # Add a follow-up prompt to encourage completion
                        self.messages.append({
                            "role": "user",
                            "content": "Please try again to complete the previous request. "
                                       "If a tool failed, try an alternative approach."
                        })
                        time.sleep(RETRY_DELAY)
                        continue

                    # Max retries reached, return best response
                    return last_response

            except Exception as e:
                if attempt < self.max_retries - 1:
                    if self.verbose:
                        print(f"\n⚠️  Error: {e}, retrying... "
                              f"(attempt {attempt + 2}/{self.max_retries})")
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                return f"Error after {self.max_retries} attempts: {str(e)}"

        return last_response

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
        for msg in messages:
            if hasattr(msg, 'type'):
                if msg.type == 'ai' and hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        print(f"\n🔧 Tool: {tool_call.get('name', 'unknown')}")
                        print(f"   Input: {tool_call.get('args', {})}")
                elif msg.type == 'tool':
                    content = msg.content
                    if len(content) > 200:
                        content = content[:200] + "..."
                    print(f"   Result: {content}")

    def clear_memory(self):
        """Clear the conversation memory."""
        self.messages = []
