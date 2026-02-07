"""ReAct agent for cosmology research."""

import os
from typing import List

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


def create_tools() -> List[Tool]:
    """Create the tool list for the agent."""
    return [
        Tool(
            name="web_search",
            func=web_search,
            description="Search the web for scientific papers, NASA data, and current research. Input should be a search query string."
        ),
        Tool(
            name="execute_code",
            func=execute_code,
            description="Execute Python code for physics calculations. NumPy and SymPy are available, along with physics constants (G, c, M_sun, M_earth, R_earth, AU). Input should be valid Python code."
        ),
        Tool(
            name="search_wikipedia",
            func=search_wikipedia,
            description="Retrieve scientific facts and definitions from Wikipedia. Input should be a topic or term to look up."
        ),
        Tool(
            name="create_plot",
            func=create_plot,
            description="Generate visualizations using Matplotlib. Input should be Python code that creates a matplotlib figure using plt."
        ),
    ]


class KosmoAgent:
    """Cosmology Research Agent using ReAct pattern."""

    def __init__(self, verbose: bool = True):
        """Initialize the agent.

        Args:
            verbose: Whether to print intermediate steps (default: True)
        """
        self.verbose = verbose
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

            tools = create_tools()

            # Create ReAct agent using langgraph
            self._agent = create_react_agent(
                llm,
                tools,
                state_modifier=REACT_SYSTEM_PROMPT
            )

        return self._agent

    def query(self, question: str) -> str:
        """Run a query through the agent.

        Args:
            question: The user's question about cosmology/astrophysics

        Returns:
            The agent's response
        """
        agent = self._get_agent()

        # Add user message to history
        self.messages.append({"role": "user", "content": question})

        # Invoke the agent
        config = {"recursion_limit": MAX_ITERATIONS * 2}
        result = agent.invoke(
            {"messages": self.messages},
            config=config
        )

        # Extract the final response
        output_messages = result.get("messages", [])
        if output_messages:
            # Get the last AI message
            for msg in reversed(output_messages):
                if hasattr(msg, 'content') and msg.content:
                    # Store the updated message history
                    self.messages = output_messages
                    if self.verbose:
                        self._print_steps(output_messages)
                    return msg.content

        return "No response generated."

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
