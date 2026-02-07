"""Tests for diverse cosmology queries - PRD requirement.

This module tests the agent with 5+ diverse cosmology queries covering:
1. Orbital mechanics (escape velocity, orbital periods)
2. Black holes (Schwarzschild radius, event horizon)
3. Dark matter (rotation curves, density)
4. Exoplanets (habitable zone, detection methods)
5. Cosmic Microwave Background (temperature, anisotropies)
6. Stellar physics (stellar lifetimes, luminosity)
7. Cosmological parameters (Hubble constant, expansion)
"""

from unittest.mock import MagicMock, patch

from kosmo.agent import KosmoAgent, create_tools
from kosmo.prompts import REACT_SYSTEM_PROMPT, detect_topic, enhance_prompt_for_topic


class TestDiverseCosmologyQueries:
    """Integration tests for diverse cosmology queries."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_escape_velocity_query(self, mock_llm_class, mock_create_agent):
        """Test query: Calculate escape velocity from Earth."""
        mock_agent = MagicMock()

        # Simulate tool call for code execution
        tool_call_msg = MagicMock()
        tool_call_msg.type = "ai"
        tool_call_msg.content = ""
        tool_call_msg.tool_calls = [
            {"name": "execute_code", "args": {"code": "v = np.sqrt(2*G*M_earth/R_earth); print(v/1000)"}}
        ]

        tool_result_msg = MagicMock()
        tool_result_msg.type = "tool"
        tool_result_msg.content = "Output:\n11.186"

        final_msg = MagicMock()
        final_msg.type = "ai"
        final_msg.content = "The escape velocity from Earth is approximately 11.2 km/s. This is the minimum velocity an object needs to escape Earth's gravitational pull."
        final_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [tool_call_msg, tool_result_msg, final_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("Calculate escape velocity from Earth")

        assert "11.2" in result or "11.186" in result
        assert "escape velocity" in result.lower()
        assert mock_agent.invoke.called

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_schwarzschild_radius_query(self, mock_llm_class, mock_create_agent):
        """Test query: Calculate Schwarzschild radius of a 10 solar mass black hole."""
        mock_agent = MagicMock()

        tool_call_msg = MagicMock()
        tool_call_msg.type = "ai"
        tool_call_msg.content = ""
        tool_call_msg.tool_calls = [
            {"name": "execute_code", "args": {"code": "r_s = 2*G*10*M_sun/c**2; print(r_s/1000)"}}
        ]

        tool_result_msg = MagicMock()
        tool_result_msg.type = "tool"
        tool_result_msg.content = "Output:\n29.54"

        final_msg = MagicMock()
        final_msg.type = "ai"
        final_msg.content = "The Schwarzschild radius of a 10 solar mass black hole is approximately 29.5 km. This is the radius of the event horizon, beyond which nothing can escape."
        final_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [tool_call_msg, tool_result_msg, final_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("What is the Schwarzschild radius of a 10 solar mass black hole?")

        assert "29" in result
        assert "schwarzschild" in result.lower() or "radius" in result.lower()

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_dark_matter_query(self, mock_llm_class, mock_create_agent):
        """Test query: Explain dark matter and its evidence."""
        mock_agent = MagicMock()

        # Search for information first
        search_msg = MagicMock()
        search_msg.type = "ai"
        search_msg.content = ""
        search_msg.tool_calls = [
            {"name": "search_wikipedia", "args": {"query": "dark matter"}}
        ]

        search_result_msg = MagicMock()
        search_result_msg.type = "tool"
        search_result_msg.content = "Dark matter is a hypothetical form of matter that does not emit light..."

        final_msg = MagicMock()
        final_msg.type = "ai"
        final_msg.content = "Dark matter is a form of matter that doesn't interact with electromagnetic radiation. Key evidence includes galaxy rotation curves showing flat profiles at large radii, gravitational lensing observations, and cosmic microwave background anisotropies."
        final_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [search_msg, search_result_msg, final_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("What is dark matter and what evidence supports its existence?")

        assert "dark matter" in result.lower()
        assert any(evidence in result.lower() for evidence in ["rotation", "lensing", "evidence"])

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_exoplanet_habitable_zone_query(self, mock_llm_class, mock_create_agent):
        """Test query: Calculate habitable zone for a Sun-like star."""
        mock_agent = MagicMock()

        tool_call_msg = MagicMock()
        tool_call_msg.type = "ai"
        tool_call_msg.content = ""
        tool_call_msg.tool_calls = [
            {"name": "execute_code", "args": {"code": "L_sun = 1; r_inner = np.sqrt(L_sun/1.1); r_outer = np.sqrt(L_sun/0.53); print(f'{r_inner:.2f} AU to {r_outer:.2f} AU')"}}
        ]

        tool_result_msg = MagicMock()
        tool_result_msg.type = "tool"
        tool_result_msg.content = "Output:\n0.95 AU to 1.37 AU"

        final_msg = MagicMock()
        final_msg.type = "ai"
        final_msg.content = "The habitable zone (also called the Goldilocks zone) for a Sun-like star extends from approximately 0.95 AU to 1.37 AU. Earth at 1 AU is well within this zone where liquid water can exist on the surface."
        final_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [tool_call_msg, tool_result_msg, final_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("What is the habitable zone for a Sun-like star?")

        assert "habitable" in result.lower() or "goldilocks" in result.lower()
        assert "AU" in result or "au" in result.lower()

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_cmb_temperature_query(self, mock_llm_class, mock_create_agent):
        """Test query: What is the temperature of the CMB?"""
        mock_agent = MagicMock()

        search_msg = MagicMock()
        search_msg.type = "ai"
        search_msg.content = ""
        search_msg.tool_calls = [
            {"name": "search_wikipedia", "args": {"query": "cosmic microwave background temperature"}}
        ]

        search_result_msg = MagicMock()
        search_result_msg.type = "tool"
        search_result_msg.content = "The CMB has a thermal black body spectrum at a temperature of 2.725 K..."

        final_msg = MagicMock()
        final_msg.type = "ai"
        final_msg.content = "The Cosmic Microwave Background (CMB) has a temperature of 2.725 K (about -270.4°C). This is the remnant radiation from the early universe, approximately 380,000 years after the Big Bang when the universe became transparent to light."
        final_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [search_msg, search_result_msg, final_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("What is the temperature of the cosmic microwave background?")

        assert "2.725" in result or "2.7" in result
        assert "K" in result or "kelvin" in result.lower()

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_orbital_period_query(self, mock_llm_class, mock_create_agent):
        """Test query: Calculate orbital period of Mars."""
        mock_agent = MagicMock()

        tool_call_msg = MagicMock()
        tool_call_msg.type = "ai"
        tool_call_msg.content = ""
        tool_call_msg.tool_calls = [
            {"name": "execute_code", "args": {"code": "a_mars = 1.524 * AU; T = 2*np.pi*np.sqrt(a_mars**3/(G*M_sun)); print(f'{T/(365.25*24*3600):.2f} years')"}}
        ]

        tool_result_msg = MagicMock()
        tool_result_msg.type = "tool"
        tool_result_msg.content = "Output:\n1.88 years"

        final_msg = MagicMock()
        final_msg.type = "ai"
        final_msg.content = "The orbital period of Mars is approximately 1.88 Earth years, or about 687 Earth days. This is calculated using Kepler's third law with Mars' semi-major axis of 1.524 AU."
        final_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [tool_call_msg, tool_result_msg, final_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("What is the orbital period of Mars?")

        assert "1.88" in result or "687" in result or "1.9" in result
        assert "year" in result.lower() or "day" in result.lower()

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_hubble_constant_query(self, mock_llm_class, mock_create_agent):
        """Test query: What is the Hubble constant?"""
        mock_agent = MagicMock()

        search_msg = MagicMock()
        search_msg.type = "ai"
        search_msg.content = ""
        search_msg.tool_calls = [
            {"name": "web_search", "args": {"query": "Hubble constant current value"}}
        ]

        search_result_msg = MagicMock()
        search_result_msg.type = "tool"
        search_result_msg.content = "The Hubble constant is approximately 70 km/s/Mpc..."

        final_msg = MagicMock()
        final_msg.type = "ai"
        final_msg.content = "The Hubble constant (H₀) measures the universe's expansion rate. Current measurements give approximately 67-74 km/s/Mpc, with a tension between early universe (CMB) and late universe (supernovae) measurements."
        final_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [search_msg, search_result_msg, final_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("What is the Hubble constant and why is there tension in measurements?")

        assert "hubble" in result.lower()
        assert "km/s" in result.lower() or "mpc" in result.lower() or "expansion" in result.lower()


class TestTopicDetectionForQueries:
    """Test that topic detection works for diverse queries."""

    def test_detect_dark_matter_topic(self):
        """Test dark matter topic detection."""
        query = "What is the evidence for dark matter in galaxy rotation curves?"
        topic = detect_topic(query)
        assert topic == "dark_matter"

    def test_detect_exoplanet_topic(self):
        """Test exoplanet topic detection."""
        query = "How are exoplanets detected using the transit method?"
        topic = detect_topic(query)
        assert topic == "exoplanet"

    def test_detect_cmb_topic(self):
        """Test CMB topic detection."""
        query = "What do CMB anisotropies tell us about the early universe?"
        topic = detect_topic(query)
        assert topic == "cmb"

    def test_detect_general_cosmology_topic(self):
        """Test that general queries return None for topic."""
        query = "Calculate escape velocity from Earth"
        topic = detect_topic(query)
        # This is a general physics query, not topic-specific
        assert topic is None

    def test_detect_wimp_dark_matter(self):
        """Test WIMP keyword detection for dark matter."""
        query = "What are WIMPs and how do they relate to dark matter detection?"
        topic = detect_topic(query)
        assert topic == "dark_matter"


class TestPromptEnhancementForQueries:
    """Test that prompts are enhanced correctly for different topics."""

    def test_dark_matter_prompt_enhancement(self):
        """Test that dark matter queries get enhanced prompts."""
        query = "Explain dark matter rotation curves"
        enhanced = enhance_prompt_for_topic(REACT_SYSTEM_PROMPT, query)
        assert "dark matter" in enhanced.lower()
        assert len(enhanced) > len(REACT_SYSTEM_PROMPT)

    def test_exoplanet_prompt_enhancement(self):
        """Test that exoplanet queries get enhanced prompts."""
        query = "How do we detect exoplanets using transits?"
        enhanced = enhance_prompt_for_topic(REACT_SYSTEM_PROMPT, query)
        assert "exoplanet" in enhanced.lower() or "transit" in enhanced.lower()
        assert len(enhanced) > len(REACT_SYSTEM_PROMPT)

    def test_cmb_prompt_enhancement(self):
        """Test that CMB queries get enhanced prompts."""
        query = "What is the significance of CMB polarization?"
        enhanced = enhance_prompt_for_topic(REACT_SYSTEM_PROMPT, query)
        assert "cmb" in enhanced.lower() or "microwave" in enhanced.lower()
        assert len(enhanced) > len(REACT_SYSTEM_PROMPT)

    def test_general_query_no_enhancement(self):
        """Test that general queries don't get topic-specific enhancement."""
        query = "What is 2 + 2?"
        enhanced = enhance_prompt_for_topic(REACT_SYSTEM_PROMPT, query)
        assert enhanced == REACT_SYSTEM_PROMPT


class TestToolSelectionForQueries:
    """Test that appropriate tools are available for different query types."""

    def test_tools_include_code_executor(self):
        """Test that code executor is available for calculations."""
        tools = create_tools()
        tool_names = [t.name for t in tools]
        assert "execute_code" in tool_names

    def test_tools_include_web_search(self):
        """Test that web search is available for research queries."""
        tools = create_tools()
        tool_names = [t.name for t in tools]
        assert "web_search" in tool_names

    def test_tools_include_wikipedia(self):
        """Test that Wikipedia is available for knowledge queries."""
        tools = create_tools()
        tool_names = [t.name for t in tools]
        assert "search_wikipedia" in tool_names

    def test_tools_include_plotter(self):
        """Test that plotter is available for visualization queries."""
        tools = create_tools()
        tool_names = [t.name for t in tools]
        assert "create_plot" in tool_names


class TestMultiToolQueryFlow:
    """Test queries that require multiple tools."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_hohmann_transfer_query(self, mock_llm_class, mock_create_agent):
        """Test query: Simulate trajectory from Earth to Mars (multi-tool)."""
        mock_agent = MagicMock()

        # First tool call: calculate parameters
        calc_msg = MagicMock()
        calc_msg.type = "ai"
        calc_msg.content = ""
        calc_msg.tool_calls = [
            {"name": "execute_code", "args": {"code": "from examples.hohmann_transfer import calculate_planetary_transfer; result = calculate_planetary_transfer('Earth', 'Mars'); print(result)"}}
        ]

        calc_result_msg = MagicMock()
        calc_result_msg.type = "tool"
        calc_result_msg.content = "HohmannTransferResult(r1=1.496e11, r2=2.279e11, delta_v_total=5594.3, transfer_time=259.0)"

        # Second tool call: create visualization
        plot_msg = MagicMock()
        plot_msg.type = "ai"
        plot_msg.content = ""
        plot_msg.tool_calls = [
            {"name": "create_plot", "args": {"code": "plt.plot([0], [0]); plt.title('Hohmann Transfer')"}}
        ]

        plot_result_msg = MagicMock()
        plot_result_msg.type = "tool"
        plot_result_msg.content = "Plot saved to: plots/output.png"

        final_msg = MagicMock()
        final_msg.type = "ai"
        final_msg.content = "The Hohmann transfer from Earth to Mars requires a total delta-v of approximately 5.6 km/s and takes about 259 days. I've created a visualization showing the transfer orbit."
        final_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [calc_msg, calc_result_msg, plot_msg, plot_result_msg, final_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("Simulate the trajectory of a spacecraft from Earth to Mars")

        assert "transfer" in result.lower() or "delta" in result.lower()
        assert "mars" in result.lower()

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_research_and_calculate_query(self, mock_llm_class, mock_create_agent):
        """Test query that requires both research and calculation."""
        mock_agent = MagicMock()

        # Search for current data
        search_msg = MagicMock()
        search_msg.type = "ai"
        search_msg.content = ""
        search_msg.tool_calls = [
            {"name": "web_search", "args": {"query": "current black hole mass measurements"}}
        ]

        search_result_msg = MagicMock()
        search_result_msg.type = "tool"
        search_result_msg.content = "Sagittarius A* has a mass of about 4 million solar masses..."

        # Calculate based on research
        calc_msg = MagicMock()
        calc_msg.type = "ai"
        calc_msg.content = ""
        calc_msg.tool_calls = [
            {"name": "execute_code", "args": {"code": "r_s = 2*G*4e6*M_sun/c**2; print(f'{r_s/1000:.2e} km')"}}
        ]

        calc_result_msg = MagicMock()
        calc_result_msg.type = "tool"
        calc_result_msg.content = "Output:\n1.18e+07 km"

        final_msg = MagicMock()
        final_msg.type = "ai"
        final_msg.content = "Sagittarius A*, the supermassive black hole at the center of the Milky Way, has a mass of about 4 million solar masses. Its Schwarzschild radius is approximately 12 million km, about 17 times the radius of the Sun."
        final_msg.tool_calls = []

        mock_agent.invoke.return_value = {
            "messages": [search_msg, search_result_msg, calc_msg, calc_result_msg, final_msg]
        }
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        result = agent.query("What is the Schwarzschild radius of the black hole at the center of our galaxy?")

        assert "sagittarius" in result.lower() or "milky way" in result.lower() or "schwarzschild" in result.lower()
        assert any(unit in result for unit in ["km", "million", "solar"])


class TestQueryErrorHandling:
    """Test error handling for various query types."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch("kosmo.agent.time.sleep")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_query_recovers_from_tool_failure(
        self, mock_sleep, mock_llm_class, mock_create_agent
    ):
        """Test that query recovers when a tool fails."""
        mock_agent = MagicMock()

        # First attempt fails
        fail_msg = MagicMock()
        fail_msg.type = "ai"
        fail_msg.content = "I was unable to complete the search."

        # Second attempt succeeds with different approach
        success_msg = MagicMock()
        success_msg.type = "ai"
        success_msg.content = "Based on my knowledge, escape velocity from Earth is 11.2 km/s."

        mock_agent.invoke.side_effect = [
            {"messages": [fail_msg]},
            {"messages": [success_msg]},
        ]
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, max_retries=3)
        result = agent.query("What is escape velocity?")

        assert "11.2" in result or "escape" in result.lower()
        assert mock_agent.invoke.call_count == 2


class TestQuerySessionMemory:
    """Test session memory for multi-turn cosmology conversations."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_multi_turn_cosmology_conversation(self, mock_llm_class, mock_create_agent):
        """Test that agent maintains context across turns."""
        mock_agent = MagicMock()

        # First query
        first_msg = MagicMock()
        first_msg.type = "ai"
        first_msg.content = "The Schwarzschild radius formula is r_s = 2GM/c². For a 10 solar mass black hole, this gives about 30 km."
        first_msg.tool_calls = []

        # Second query (follow-up)
        second_msg = MagicMock()
        second_msg.type = "ai"
        second_msg.content = "For 100 solar masses, using the same formula, the Schwarzschild radius would be 10 times larger: about 300 km."
        second_msg.tool_calls = []

        mock_agent.invoke.side_effect = [
            {"messages": [first_msg]},
            {"messages": [second_msg]},
        ]
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, enable_memory=True)

        result1 = agent.query("What is the Schwarzschild radius of a 10 solar mass black hole?")
        result2 = agent.query("What about 100 solar masses?")

        assert "30" in result1 or "schwarzschild" in result1.lower()
        assert "300" in result2 or "10 times" in result2.lower() or "100" in result2

        # Verify both queries used the same session
        thread_id = agent.get_current_thread_id()
        session_info = agent.get_session_info(thread_id)
        assert session_info is not None
        assert session_info["query_count"] == 2
