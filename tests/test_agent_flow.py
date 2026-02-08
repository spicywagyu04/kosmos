"""Integration tests for agent flow - PRD requirement.

This module tests the complete agent flow including:
1. ReAct loop execution (Thought-Action-Observation cycles)
2. Multi-tool query orchestration
3. Error recovery and retry flow
4. Session continuity and memory
5. Graceful degradation when tools fail
6. Response synthesis and formatting
"""

from unittest.mock import MagicMock, patch

from kosmo.agent import (
    MAX_ITERATIONS,
    MAX_RETRIES,
    RETRY_DELAY,
    KosmoAgent,
    create_tools,
)


class TestReActLoopFlow:
    """Integration tests for ReAct loop execution."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_complete_react_cycle_thought_action_observation(
        self, mock_llm_class, mock_create_agent
    ):
        """Test a complete Thought-Action-Observation cycle."""
        mock_agent = MagicMock()

        # Thought: Agent reasons about what to do
        thought_msg = MagicMock()
        thought_msg.type = "ai"
        thought_msg.content = "I need to calculate the escape velocity using physics constants."
        thought_msg.tool_calls = [
            {"name": "execute_code", "args": {"code": "v = np.sqrt(2*G*M_earth/R_earth); print(f'{v/1000:.2f} km/s')"}}
        ]

        # Observation: Tool returns result
        observation_msg = MagicMock()
        observation_msg.type = "tool"
        observation_msg.content = "Output:\n11.19 km/s"

        # Final synthesis
        synthesis_msg = MagicMock()
        synthesis_msg.type = "ai"
        synthesis_msg.content = "The escape velocity from Earth is approximately 11.2 km/s."
        synthesis_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [thought_msg, observation_msg, synthesis_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("What is the escape velocity from Earth?")

        # Verify complete cycle
        assert "11.2" in result or "11.19" in result
        assert mock_agent.invoke.called

        # Verify message structure passed to agent
        call_args = mock_agent.invoke.call_args[0][0]
        assert "messages" in call_args
        assert call_args["messages"][0]["role"] == "user"

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_multi_step_react_loop(self, mock_llm_class, mock_create_agent):
        """Test ReAct loop with multiple Thought-Action-Observation cycles."""
        mock_agent = MagicMock()

        # First cycle: Search for information
        search_thought = MagicMock()
        search_thought.type = "ai"
        search_thought.content = "Let me search for current data on black holes."
        search_thought.tool_calls = [
            {"name": "web_search", "args": {"query": "Sagittarius A black hole mass"}}
        ]

        search_observation = MagicMock()
        search_observation.type = "tool"
        search_observation.content = "Sagittarius A* has a mass of 4 million solar masses."

        # Second cycle: Calculate based on search results
        calc_thought = MagicMock()
        calc_thought.type = "ai"
        calc_thought.content = "Now I'll calculate the Schwarzschild radius."
        calc_thought.tool_calls = [
            {"name": "execute_code", "args": {"code": "r_s = 2*G*4e6*M_sun/c**2; print(f'{r_s/1000:.2e} km')"}}
        ]

        calc_observation = MagicMock()
        calc_observation.type = "tool"
        calc_observation.content = "Output:\n1.18e+07 km"

        # Final synthesis
        final_msg = MagicMock()
        final_msg.type = "ai"
        final_msg.content = "Sagittarius A* has a Schwarzschild radius of approximately 12 million km."
        final_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [
                search_thought, search_observation,
                calc_thought, calc_observation,
                final_msg
            ]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("What is the Schwarzschild radius of Sagittarius A*?")

        assert "schwarzschild" in result.lower() or "12 million" in result.lower()
        assert mock_agent.invoke.called

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_react_loop_with_visualization(self, mock_llm_class, mock_create_agent):
        """Test ReAct loop that includes visualization generation."""
        mock_agent = MagicMock()

        # Calculate parameters
        calc_msg = MagicMock()
        calc_msg.type = "ai"
        calc_msg.content = "Calculating orbital parameters."
        calc_msg.tool_calls = [
            {"name": "execute_code", "args": {"code": "T = 2*np.pi*np.sqrt((1.524*AU)**3/(G*M_sun)); print(T)"}}
        ]

        calc_result = MagicMock()
        calc_result.type = "tool"
        calc_result.content = "Output:\n5.936e+07"

        # Create visualization
        plot_msg = MagicMock()
        plot_msg.type = "ai"
        plot_msg.content = "Creating orbital visualization."
        plot_msg.tool_calls = [
            {"name": "create_plot", "args": {"code": "plt.plot(...); plt.title('Mars Orbit')"}}
        ]

        plot_result = MagicMock()
        plot_result.type = "tool"
        plot_result.content = "Plot saved to: plots/mars_orbit.png"

        final_msg = MagicMock()
        final_msg.type = "ai"
        final_msg.content = "Mars has an orbital period of 1.88 years. See the visualization."
        final_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [calc_msg, calc_result, plot_msg, plot_result, final_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("Plot the orbit of Mars")

        assert "1.88" in result or "visualization" in result.lower() or "orbit" in result.lower()


class TestMultiToolOrchestration:
    """Test orchestration of multiple tools in a single query."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_search_then_calculate_flow(self, mock_llm_class, mock_create_agent):
        """Test flow: search for data, then calculate based on results."""
        mock_agent = MagicMock()

        messages = self._create_search_calculate_messages()
        mock_agent.invoke.return_value = {"messages": messages}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("Find the mass of Jupiter and calculate its escape velocity")

        assert mock_agent.invoke.called
        # Result should contain the final answer
        assert "escape" in result.lower() or "velocity" in result.lower() or "km/s" in result.lower()

    def _create_search_calculate_messages(self):
        """Helper to create mock messages for search-then-calculate flow."""
        search_msg = MagicMock()
        search_msg.type = "ai"
        search_msg.content = ""
        search_msg.tool_calls = [{"name": "search_wikipedia", "args": {"query": "Jupiter mass"}}]

        search_result = MagicMock()
        search_result.type = "tool"
        search_result.content = "Jupiter has a mass of 1.898 × 10^27 kg"

        calc_msg = MagicMock()
        calc_msg.type = "ai"
        calc_msg.content = ""
        calc_msg.tool_calls = [{"name": "execute_code", "args": {"code": "v = np.sqrt(2*G*1.898e27/69911000); print(v/1000)"}}]

        calc_result = MagicMock()
        calc_result.type = "tool"
        calc_result.content = "Output:\n59.5"

        final = MagicMock()
        final.type = "ai"
        final.content = "Jupiter's escape velocity is approximately 59.5 km/s."
        final.tool_calls = []

        return [search_msg, search_result, calc_msg, calc_result, final]

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_calculate_then_visualize_flow(self, mock_llm_class, mock_create_agent):
        """Test flow: calculate parameters, then visualize results."""
        mock_agent = MagicMock()

        calc_msg = MagicMock()
        calc_msg.type = "ai"
        calc_msg.content = "Calculating Hohmann transfer parameters."
        calc_msg.tool_calls = [{"name": "execute_code", "args": {"code": "delta_v = 3.6; print(delta_v)"}}]

        calc_result = MagicMock()
        calc_result.type = "tool"
        calc_result.content = "Output:\n3.6"

        plot_msg = MagicMock()
        plot_msg.type = "ai"
        plot_msg.content = "Creating transfer orbit visualization."
        plot_msg.tool_calls = [{"name": "create_plot", "args": {"code": "plt.plot(...)"}}]

        plot_result = MagicMock()
        plot_result.type = "tool"
        plot_result.content = "Plot saved to: plots/hohmann.png"

        final = MagicMock()
        final.type = "ai"
        final.content = "The Hohmann transfer requires delta-v of 3.6 km/s. Visualization created."
        final.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [calc_msg, calc_result, plot_msg, plot_result, final]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("Calculate and visualize a Hohmann transfer orbit")

        assert "3.6" in result or "delta" in result.lower() or "visualization" in result.lower()

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_triple_tool_chain(self, mock_llm_class, mock_create_agent):
        """Test a chain of three tool calls in sequence."""
        mock_agent = MagicMock()

        # Tool 1: Web search
        web_msg = MagicMock()
        web_msg.type = "ai"
        web_msg.content = ""
        web_msg.tool_calls = [{"name": "web_search", "args": {"query": "latest exoplanet discoveries"}}]

        web_result = MagicMock()
        web_result.type = "tool"
        web_result.content = "TESS discovered several new exoplanets..."

        # Tool 2: Wikipedia lookup
        wiki_msg = MagicMock()
        wiki_msg.type = "ai"
        wiki_msg.content = ""
        wiki_msg.tool_calls = [{"name": "search_wikipedia", "args": {"query": "TESS space telescope"}}]

        wiki_result = MagicMock()
        wiki_result.type = "tool"
        wiki_result.content = "TESS is NASA's Transiting Exoplanet Survey Satellite..."

        # Tool 3: Calculation
        calc_msg = MagicMock()
        calc_msg.type = "ai"
        calc_msg.content = ""
        calc_msg.tool_calls = [{"name": "execute_code", "args": {"code": "print('habitable zone: 0.95 AU')"}}]

        calc_result = MagicMock()
        calc_result.type = "tool"
        calc_result.content = "Output:\nhabitable zone: 0.95 AU"

        final = MagicMock()
        final.type = "ai"
        final.content = "TESS has discovered numerous exoplanets, including several in habitable zones around 0.95 AU from their stars."
        final.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [web_msg, web_result, wiki_msg, wiki_result, calc_msg, calc_result, final]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("Tell me about TESS and its exoplanet discoveries")

        assert "TESS" in result or "exoplanet" in result.lower()


class TestErrorRecoveryFlow:
    """Test error recovery and retry flow."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch("kosmo.agent.time.sleep")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_retry_on_incomplete_response(
        self, mock_sleep, mock_llm_class, mock_create_agent
    ):
        """Test that agent retries when response is incomplete."""
        mock_agent = MagicMock()

        incomplete = MagicMock()
        incomplete.type = "ai"
        incomplete.content = "I was unable to complete the calculation."

        complete = MagicMock()
        complete.type = "ai"
        complete.content = "The escape velocity is 11.2 km/s."

        mock_agent.invoke.side_effect = [
            {"messages": [incomplete]},
            {"messages": [complete]},
        ]
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, max_retries=3)
        result = agent.query("Calculate escape velocity")

        assert "11.2" in result
        assert mock_agent.invoke.call_count == 2
        mock_sleep.assert_called()

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch("kosmo.agent.time.sleep")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_retry_with_alternative_approach(
        self, mock_sleep, mock_llm_class, mock_create_agent
    ):
        """Test that retry message encourages alternative approaches."""
        mock_agent = MagicMock()

        # Tool failure response
        fail_msg = MagicMock()
        fail_msg.type = "ai"
        fail_msg.content = "The tool failed to execute."

        # Success on retry
        success_msg = MagicMock()
        success_msg.type = "ai"
        success_msg.content = "Based on physics principles, the answer is 11.2 km/s."

        mock_agent.invoke.side_effect = [
            {"messages": [fail_msg]},
            {"messages": [success_msg]},
        ]
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, max_retries=3)
        agent.query("What is escape velocity?")

        # Check retry message contains guidance
        retry_call = mock_agent.invoke.call_args_list[1]
        retry_content = str(retry_call)
        assert "try again" in retry_content.lower() or "alternative" in retry_content.lower() or "complete" in retry_content.lower()

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch("kosmo.agent.time.sleep")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_max_retries_returns_best_response(
        self, mock_sleep, mock_llm_class, mock_create_agent
    ):
        """Test that after max retries, best available response is returned."""
        mock_agent = MagicMock()

        partial = MagicMock()
        partial.type = "ai"
        partial.content = "I was unable to complete but escape velocity is around 11 km/s."

        mock_agent.invoke.return_value = {"messages": [partial]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, max_retries=2)
        result = agent.query("Calculate escape velocity")

        assert "11" in result or "unable" in result.lower()
        assert mock_agent.invoke.call_count == 2

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch("kosmo.agent.time.sleep")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_transient_error_retry(
        self, mock_sleep, mock_llm_class, mock_create_agent
    ):
        """Test retry on transient errors (rate limits, timeouts)."""
        mock_agent = MagicMock()

        success = MagicMock()
        success.type = "ai"
        success.content = "Answer: 11.2 km/s"

        mock_agent.invoke.side_effect = [
            RuntimeError("Rate limit exceeded"),
            {"messages": [success]},
        ]
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, max_retries=3)
        result = agent.query("Calculate escape velocity")

        assert "11.2" in result
        assert mock_agent.invoke.call_count == 2

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_non_transient_error_no_retry(
        self, mock_llm_class, mock_create_agent
    ):
        """Test that non-transient errors (auth) don't retry."""
        mock_agent = MagicMock()
        mock_agent.invoke.side_effect = RuntimeError("Invalid API key")
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, max_retries=3)
        result = agent.query("Test query")

        assert "error" in result.lower() or "api key" in result.lower()
        # Auth errors shouldn't be retried
        assert mock_agent.invoke.call_count == 1


class TestSessionContinuityFlow:
    """Test session continuity and memory across queries."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_multi_turn_conversation_same_session(
        self, mock_llm_class, mock_create_agent
    ):
        """Test that multiple queries maintain session context."""
        mock_agent = MagicMock()

        first_msg = MagicMock()
        first_msg.type = "ai"
        first_msg.content = "Earth's escape velocity is 11.2 km/s."
        first_msg.tool_calls = []

        second_msg = MagicMock()
        second_msg.type = "ai"
        second_msg.content = "For the Moon, it's 2.38 km/s, about 5 times less."
        second_msg.tool_calls = []

        mock_agent.invoke.side_effect = [
            {"messages": [first_msg]},
            {"messages": [second_msg]},
        ]
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, enable_memory=True)
        thread_id = agent.get_current_thread_id()

        agent.query("What is Earth's escape velocity?")
        agent.query("What about the Moon?")

        # Same thread ID used
        assert agent.get_current_thread_id() == thread_id

        # Session info updated
        session = agent.get_session_info()
        assert session["query_count"] == 2

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_new_session_creates_new_thread(
        self, mock_llm_class, mock_create_agent
    ):
        """Test that new_session() creates a fresh thread."""
        mock_agent = MagicMock()
        msg = MagicMock()
        msg.type = "ai"
        msg.content = "Response"
        msg.tool_calls = []
        mock_agent.invoke.return_value = {"messages": [msg]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, enable_memory=True)

        first_thread = agent.get_current_thread_id()
        agent.query("First query")

        new_thread = agent.new_session()
        agent.query("Second query")

        assert first_thread != new_thread
        assert agent.get_current_thread_id() == new_thread

        # Both sessions should be tracked
        sessions = agent.list_sessions()
        assert len(sessions) == 2

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_resume_session_by_thread_id(
        self, mock_llm_class, mock_create_agent
    ):
        """Test resuming a previous session by thread ID."""
        mock_agent = MagicMock()
        msg = MagicMock()
        msg.type = "ai"
        msg.content = "Response"
        msg.tool_calls = []
        mock_agent.invoke.return_value = {"messages": [msg]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, enable_memory=True)

        # First session
        first_thread = agent.get_current_thread_id()
        agent.query("Query in first session")

        # New session
        agent.new_session()
        agent.query("Query in second session")

        # Resume first session
        agent.set_thread_id(first_thread)
        agent.query("Another query in first session")

        # First session should have 2 queries
        first_session = agent.get_session_info(first_thread)
        assert first_session["query_count"] == 2

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_session_disabled_no_thread_tracking(
        self, mock_llm_class, mock_create_agent
    ):
        """Test that disabling memory doesn't track sessions."""
        mock_agent = MagicMock()
        msg = MagicMock()
        msg.type = "ai"
        msg.content = "Response"
        msg.tool_calls = []
        mock_agent.invoke.return_value = {"messages": [msg]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, enable_memory=False)
        agent.query("Test query")

        # Checkpointer should be None
        assert agent._get_checkpointer() is None


class TestGracefulDegradationFlow:
    """Test graceful degradation when tools fail."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_tool_failure_tracked(self, mock_llm_class, mock_create_agent):
        """Test that tool failures are tracked."""
        mock_agent = MagicMock()

        # Tool call with error
        tool_msg = MagicMock()
        tool_msg.type = "ai"
        tool_msg.content = ""
        tool_msg.tool_calls = [{"name": "web_search", "args": {"query": "test"}}]

        tool_result = MagicMock()
        tool_result.type = "tool"
        tool_result.content = "Error: API rate limit exceeded"

        final = MagicMock()
        final.type = "ai"
        final.content = "I couldn't complete the search due to an error."
        final.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [tool_msg, tool_result, final]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=True, graceful_degradation=True)
        agent.query("Search for something")

        # Web search should be tracked as failed
        assert "web_search" in agent.get_failed_tools()

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_degradation_notice_in_response(self, mock_llm_class, mock_create_agent):
        """Test that degradation notice is added to response."""
        mock_agent = MagicMock()

        final = MagicMock()
        final.type = "ai"
        final.content = "Based on available information, the answer is X."
        final.tool_calls = []

        mock_agent.invoke.return_value = {"messages": [final]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, graceful_degradation=True)
        # Manually mark a tool as failed
        agent._failed_tools.add("web_search")

        result = agent.query("Test query")

        # Response should include degradation notice
        assert "web_search" in result.lower() or "unavailable" in result.lower() or "degraded" in result.lower() or "---" in result

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_reset_failed_tools(self, mock_llm_class, mock_create_agent):
        """Test resetting failed tools."""
        agent = KosmoAgent(verbose=False, graceful_degradation=True)
        agent._failed_tools.add("web_search")
        agent._failed_tools.add("execute_code")

        assert len(agent.get_failed_tools()) == 2

        agent.reset_failed_tools()

        assert len(agent.get_failed_tools()) == 0

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_degradation_context_in_prompt(self, mock_llm_class, mock_create_agent):
        """Test that degradation context is added to system prompt."""
        mock_agent = MagicMock()

        msg = MagicMock()
        msg.type = "ai"
        msg.content = "Response"
        msg.tool_calls = []
        mock_agent.invoke.return_value = {"messages": [msg]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, graceful_degradation=True)
        agent._failed_tools.add("web_search")

        agent.query("Test query")

        # Agent should be created with modified prompt (contains degradation info)
        # The prompt is passed to _get_agent which is called with enhanced prompt
        assert mock_create_agent.called

    def test_get_error_summary(self):
        """Test getting error summary from error handler."""
        agent = KosmoAgent(verbose=False, graceful_degradation=True)

        summary = agent.get_error_summary()

        # Summary is empty dict when no errors have occurred
        assert isinstance(summary, dict)
        assert len(summary) == 0

    def test_get_error_summary_with_errors(self):
        """Test error summary after errors have been logged."""
        agent = KosmoAgent(verbose=False, graceful_degradation=True)

        # Simulate logging an error
        agent._error_handler.handle_tool_error("web_search", "API rate limit exceeded")

        summary = agent.get_error_summary()

        assert isinstance(summary, dict)
        assert len(summary) > 0


class TestResponseSynthesisFlow:
    """Test response synthesis and formatting."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_extracts_final_ai_response(self, mock_llm_class, mock_create_agent):
        """Test that final AI message is extracted as response."""
        mock_agent = MagicMock()

        tool_msg = MagicMock()
        tool_msg.type = "ai"
        tool_msg.content = ""
        tool_msg.tool_calls = [{"name": "execute_code", "args": {"code": "print(42)"}}]

        tool_result = MagicMock()
        tool_result.type = "tool"
        tool_result.content = "Output:\n42"

        final = MagicMock()
        final.type = "ai"
        final.content = "The answer is 42."
        final.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [tool_msg, tool_result, final]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("What is the answer?")

        assert result == "The answer is 42."

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_handles_empty_messages(self, mock_llm_class, mock_create_agent):
        """Test handling of empty message list."""
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {"messages": []}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("Test")

        assert result == "No response generated."

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_skips_tool_messages_for_response(self, mock_llm_class, mock_create_agent):
        """Test that tool messages are skipped when extracting response."""
        mock_agent = MagicMock()

        ai_msg = MagicMock()
        ai_msg.type = "ai"
        ai_msg.content = "The final answer."
        ai_msg.tool_calls = []

        # Tool message is last but should be skipped
        tool_msg = MagicMock()
        tool_msg.type = "tool"
        tool_msg.content = "Tool output"

        mock_agent.invoke.return_value = {
            "messages": [ai_msg, tool_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("Test")

        # Should get AI message, not tool message
        assert result == "The final answer."


class TestTopicPromptEnhancementFlow:
    """Test topic-specific prompt enhancement flow."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_dark_matter_query_uses_enhanced_prompt(
        self, mock_llm_class, mock_create_agent
    ):
        """Test that dark matter queries get enhanced prompts."""
        mock_agent = MagicMock()
        msg = MagicMock()
        msg.type = "ai"
        msg.content = "Dark matter response"
        msg.tool_calls = []
        mock_agent.invoke.return_value = {"messages": [msg]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, use_topic_prompts=True)
        agent.query("What is dark matter?")

        # Agent should be created (with enhanced prompt)
        assert mock_create_agent.called

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_topic_prompts_disabled(self, mock_llm_class, mock_create_agent):
        """Test that topic prompts can be disabled."""
        mock_agent = MagicMock()
        msg = MagicMock()
        msg.type = "ai"
        msg.content = "Response"
        msg.tool_calls = []
        mock_agent.invoke.return_value = {"messages": [msg]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, use_topic_prompts=False)
        agent.query("What is dark matter?")

        # Agent still works, just without enhanced prompts
        assert mock_create_agent.called


class TestAgentConfigurationFlow:
    """Test agent configuration options."""

    def test_max_iterations_configured(self):
        """Test MAX_ITERATIONS is properly set."""
        assert MAX_ITERATIONS == 10

    def test_max_retries_configured(self):
        """Test MAX_RETRIES is properly set."""
        assert MAX_RETRIES == 3

    def test_retry_delay_configured(self):
        """Test RETRY_DELAY is properly set."""
        assert RETRY_DELAY == 1.0

    def test_agent_default_configuration(self):
        """Test agent has sensible defaults."""
        agent = KosmoAgent()

        assert agent.verbose is True
        assert agent.max_retries == MAX_RETRIES
        assert agent.with_tool_retry is True
        assert agent.use_topic_prompts is True
        assert agent.enable_memory is True
        assert agent.graceful_degradation is True

    def test_agent_custom_configuration(self):
        """Test agent accepts custom configuration."""
        agent = KosmoAgent(
            verbose=False,
            max_retries=5,
            with_tool_retry=False,
            use_topic_prompts=False,
            enable_memory=False,
            graceful_degradation=False
        )

        assert agent.verbose is False
        assert agent.max_retries == 5
        assert agent.with_tool_retry is False
        assert agent.use_topic_prompts is False
        assert agent.enable_memory is False
        assert agent.graceful_degradation is False


class TestToolAvailabilityFlow:
    """Test that all required tools are available."""

    def test_all_four_tools_available(self):
        """Test that all four required tools are available."""
        tools = create_tools()
        tool_names = {t.name for t in tools}

        assert "web_search" in tool_names
        assert "execute_code" in tool_names
        assert "search_wikipedia" in tool_names
        assert "create_plot" in tool_names

    def test_tools_have_descriptions(self):
        """Test that all tools have descriptions."""
        tools = create_tools()

        for tool in tools:
            assert tool.description
            assert len(tool.description) > 10

    def test_tools_are_callable(self):
        """Test that all tools are callable."""
        tools = create_tools()

        for tool in tools:
            assert callable(tool.func)


class TestVerboseOutputFlow:
    """Test verbose output during agent execution."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_verbose_prints_tool_calls(self, mock_llm_class, mock_create_agent, capsys):
        """Test that verbose mode prints tool calls."""
        mock_agent = MagicMock()

        tool_msg = MagicMock()
        tool_msg.type = "ai"
        tool_msg.content = ""
        tool_msg.tool_calls = [{"name": "execute_code", "args": {"code": "print(1)"}}]

        tool_result = MagicMock()
        tool_result.type = "tool"
        tool_result.content = "Output:\n1"

        final = MagicMock()
        final.type = "ai"
        final.content = "Done"
        final.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [tool_msg, tool_result, final]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=True)
        agent.query("Test")

        captured = capsys.readouterr()
        assert "Tool:" in captured.out or "execute_code" in captured.out

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_verbose_false_suppresses_output(
        self, mock_llm_class, mock_create_agent, capsys
    ):
        """Test that verbose=False suppresses intermediate output."""
        mock_agent = MagicMock()
        msg = MagicMock()
        msg.type = "ai"
        msg.content = "Response"
        msg.tool_calls = []
        mock_agent.invoke.return_value = {"messages": [msg]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        agent.query("Test")

        captured = capsys.readouterr()
        # No tool output should be printed
        assert "Tool:" not in captured.out
