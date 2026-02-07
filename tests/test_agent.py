"""Tests for the ReAct agent."""

from unittest.mock import MagicMock, patch

import pytest

from kosmo.agent import KosmoAgent, create_tools


class TestCreateTools:
    """Tests for the create_tools function."""

    def test_create_tools_returns_four_tools(self):
        """Test that create_tools returns exactly 4 tools."""
        tools = create_tools()
        assert len(tools) == 4

    def test_create_tools_has_web_search(self):
        """Test that web_search tool is included."""
        tools = create_tools()
        tool_names = [t.name for t in tools]
        assert "web_search" in tool_names

    def test_create_tools_has_execute_code(self):
        """Test that execute_code tool is included."""
        tools = create_tools()
        tool_names = [t.name for t in tools]
        assert "execute_code" in tool_names

    def test_create_tools_has_search_wikipedia(self):
        """Test that search_wikipedia tool is included."""
        tools = create_tools()
        tool_names = [t.name for t in tools]
        assert "search_wikipedia" in tool_names

    def test_create_tools_has_create_plot(self):
        """Test that create_plot tool is included."""
        tools = create_tools()
        tool_names = [t.name for t in tools]
        assert "create_plot" in tool_names


class TestKosmoAgentInit:
    """Tests for KosmoAgent initialization."""

    def test_init_default_verbose(self):
        """Test that agent defaults to verbose=True."""
        agent = KosmoAgent()
        assert agent.verbose is True

    def test_init_verbose_false(self):
        """Test that agent can be initialized with verbose=False."""
        agent = KosmoAgent(verbose=False)
        assert agent.verbose is False

    def test_init_empty_messages(self):
        """Test that agent starts with empty message history."""
        agent = KosmoAgent()
        assert agent.messages == []

    def test_init_no_agent_created(self):
        """Test that internal agent is not created until needed."""
        agent = KosmoAgent()
        assert agent._agent is None


class TestKosmoAgentMemory:
    """Tests for agent memory management."""

    def test_clear_memory(self):
        """Test that clear_memory empties the message history."""
        agent = KosmoAgent()
        agent.messages = [{"role": "user", "content": "test"}]
        agent.clear_memory()
        assert agent.messages == []


class TestKosmoAgentQuery:
    """Tests for agent query functionality."""

    def test_query_requires_api_key(self):
        """Test that query raises error when API key is missing."""
        agent = KosmoAgent()
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                agent.query("Test query")

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_query_adds_user_message(self, mock_llm_class, mock_create_agent):
        """Test that query adds user message to history."""
        # Setup mock agent
        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_message.type = "ai"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        agent.query("What is escape velocity?")

        # Check that user message was added before invoke
        assert mock_agent.invoke.called
        call_args = mock_agent.invoke.call_args[0][0]
        assert call_args["messages"][0]["role"] == "user"
        assert call_args["messages"][0]["content"] == "What is escape velocity?"

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_query_returns_response(self, mock_llm_class, mock_create_agent):
        """Test that query returns the agent response."""
        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Escape velocity is 11.2 km/s"
        mock_message.type = "ai"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("What is escape velocity?")

        assert result == "Escape velocity is 11.2 km/s"

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_query_handles_empty_response(self, mock_llm_class, mock_create_agent):
        """Test that query handles empty response gracefully."""
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {"messages": []}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("Test query")

        assert result == "No response generated."

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_react_loop_with_tool_calls(self, mock_llm_class, mock_create_agent):
        """Test that ReAct loop processes tool calls correctly."""
        mock_agent = MagicMock()

        # Simulate a ReAct loop with tool call
        tool_call_msg = MagicMock()
        tool_call_msg.type = "ai"
        tool_call_msg.content = ""
        tool_call_msg.tool_calls = [
            {"name": "execute_code", "args": {"code": "print(11.2)"}}
        ]

        tool_result_msg = MagicMock()
        tool_result_msg.type = "tool"
        tool_result_msg.content = "Output:\n11.2"

        final_msg = MagicMock()
        final_msg.type = "ai"
        final_msg.content = "The escape velocity from Earth is 11.2 km/s"
        final_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [tool_call_msg, tool_result_msg, final_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("Calculate escape velocity from Earth")

        assert "11.2" in result
        assert mock_agent.invoke.called


class TestEscapeVelocityCalculation:
    """Tests specifically for escape velocity calculation - PRD requirement."""

    def test_code_executor_escape_velocity(self):
        """Test that code executor can calculate escape velocity correctly."""
        from kosmo.tools import execute_code

        # The escape velocity formula: v = sqrt(2*G*M/R)
        # np is already available in the sandbox, no import needed
        code = """
# Using pre-defined constants G, M_earth, R_earth (np is pre-imported)
v_escape = np.sqrt(2 * G * M_earth / R_earth)
print(f"Escape velocity: {v_escape / 1000:.2f} km/s")
"""
        result = execute_code(code)
        assert "11.18" in result or "11.19" in result  # ~11.186 km/s

    def test_code_executor_has_physics_constants(self):
        """Test that code executor has required physics constants."""
        from kosmo.tools import execute_code

        code = """
print(f"G = {G}")
print(f"M_earth = {M_earth}")
print(f"R_earth = {R_earth}")
"""
        result = execute_code(code)
        assert "6.6743" in result  # Gravitational constant
        assert "5.972e+24" in result  # Earth mass
        assert "6371000" in result or "6.371e" in result  # Earth radius


class TestReActLoopVerification:
    """Tests to verify ReAct Thought-Action-Observation loop."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_react_loop_structure(self, mock_llm_class, mock_create_agent):
        """Verify the ReAct loop has proper Thought-Action-Observation structure."""
        mock_agent = MagicMock()

        # Create messages that simulate a full ReAct cycle:
        # 1. AI thinks and decides to use a tool (Thought + Action)
        thought_action_msg = MagicMock()
        thought_action_msg.type = "ai"
        thought_action_msg.content = "I need to calculate escape velocity using physics."
        thought_action_msg.tool_calls = [
            {
                "name": "execute_code",
                "args": {"code": "v = np.sqrt(2*G*M_earth/R_earth); print(v/1000)"}
            }
        ]

        # 2. Tool returns result (Observation)
        observation_msg = MagicMock()
        observation_msg.type = "tool"
        observation_msg.content = "Output:\n11.186"

        # 3. AI synthesizes final answer
        synthesis_msg = MagicMock()
        synthesis_msg.type = "ai"
        synthesis_msg.content = "The escape velocity from Earth is approximately 11.2 km/s."
        synthesis_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [thought_action_msg, observation_msg, synthesis_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("Calculate escape velocity from Earth")

        # Verify the response contains the expected result
        assert "11.2" in result or "11.186" in result
        assert "escape velocity" in result.lower()

    def test_agent_max_iterations_configured(self):
        """Test that max iterations is properly configured."""
        from kosmo.agent import MAX_ITERATIONS
        assert MAX_ITERATIONS == 10  # As specified in PRD
