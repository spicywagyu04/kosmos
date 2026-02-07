"""Tests for cosmology-specific prompt templates."""

from kosmo.prompts import (
    CMB_CONTEXT,
    CMB_KEYWORDS,
    DARK_MATTER_CONTEXT,
    DARK_MATTER_KEYWORDS,
    EXOPLANET_CONTEXT,
    EXOPLANET_KEYWORDS,
    REACT_SYSTEM_PROMPT,
    detect_topic,
    enhance_prompt_for_topic,
    get_topic_context,
)


class TestCosmologyContextTemplates:
    """Tests for the cosmology context templates."""

    def test_dark_matter_context_exists(self):
        """Test that dark matter context template is defined."""
        assert DARK_MATTER_CONTEXT is not None
        assert len(DARK_MATTER_CONTEXT) > 100

    def test_dark_matter_context_has_key_concepts(self):
        """Test that dark matter context includes key concepts."""
        assert "WIMP" in DARK_MATTER_CONTEXT
        assert "CDM" in DARK_MATTER_CONTEXT or "Cold Dark Matter" in DARK_MATTER_CONTEXT
        assert "rotation curve" in DARK_MATTER_CONTEXT.lower()
        assert "NFW" in DARK_MATTER_CONTEXT

    def test_dark_matter_context_has_equations(self):
        """Test that dark matter context includes relevant equations."""
        assert "ρ" in DARK_MATTER_CONTEXT or "rho" in DARK_MATTER_CONTEXT.lower()
        assert "virial" in DARK_MATTER_CONTEXT.lower()

    def test_exoplanet_context_exists(self):
        """Test that exoplanet context template is defined."""
        assert EXOPLANET_CONTEXT is not None
        assert len(EXOPLANET_CONTEXT) > 100

    def test_exoplanet_context_has_detection_methods(self):
        """Test that exoplanet context includes detection methods."""
        assert "transit" in EXOPLANET_CONTEXT.lower()
        assert "radial velocity" in EXOPLANET_CONTEXT.lower()
        assert "direct imaging" in EXOPLANET_CONTEXT.lower()

    def test_exoplanet_context_has_missions(self):
        """Test that exoplanet context includes key missions."""
        assert "Kepler" in EXOPLANET_CONTEXT
        assert "TESS" in EXOPLANET_CONTEXT
        assert "JWST" in EXOPLANET_CONTEXT or "James Webb" in EXOPLANET_CONTEXT

    def test_exoplanet_context_has_habitability_concepts(self):
        """Test that exoplanet context includes habitability concepts."""
        assert "habitable zone" in EXOPLANET_CONTEXT.lower()
        assert "equilibrium temperature" in EXOPLANET_CONTEXT.lower()

    def test_cmb_context_exists(self):
        """Test that CMB context template is defined."""
        assert CMB_CONTEXT is not None
        assert len(CMB_CONTEXT) > 100

    def test_cmb_context_has_key_values(self):
        """Test that CMB context includes key values."""
        assert "2.725" in CMB_CONTEXT  # Temperature
        assert "1100" in CMB_CONTEXT  # Redshift at recombination
        assert "10⁻⁵" in CMB_CONTEXT or "10^-5" in CMB_CONTEXT  # Anisotropy scale

    def test_cmb_context_has_experiments(self):
        """Test that CMB context includes key experiments."""
        assert "COBE" in CMB_CONTEXT
        assert "WMAP" in CMB_CONTEXT
        assert "Planck" in CMB_CONTEXT

    def test_cmb_context_has_power_spectrum_info(self):
        """Test that CMB context includes power spectrum information."""
        assert "power spectrum" in CMB_CONTEXT.lower()
        assert "acoustic" in CMB_CONTEXT.lower()


class TestCosmologyKeywords:
    """Tests for the topic detection keywords."""

    def test_dark_matter_keywords_exist(self):
        """Test that dark matter keywords list is defined."""
        assert len(DARK_MATTER_KEYWORDS) > 5
        assert "dark matter" in DARK_MATTER_KEYWORDS
        assert "wimp" in DARK_MATTER_KEYWORDS

    def test_exoplanet_keywords_exist(self):
        """Test that exoplanet keywords list is defined."""
        assert len(EXOPLANET_KEYWORDS) > 5
        assert "exoplanet" in EXOPLANET_KEYWORDS
        assert "habitable zone" in EXOPLANET_KEYWORDS

    def test_cmb_keywords_exist(self):
        """Test that CMB keywords list is defined."""
        assert len(CMB_KEYWORDS) > 5
        assert "cmb" in CMB_KEYWORDS
        assert "cosmic microwave background" in CMB_KEYWORDS

    def test_keywords_are_lowercase(self):
        """Test that all keywords are lowercase for case-insensitive matching."""
        for kw in DARK_MATTER_KEYWORDS:
            assert kw == kw.lower(), f"Dark matter keyword '{kw}' is not lowercase"
        for kw in EXOPLANET_KEYWORDS:
            assert kw == kw.lower(), f"Exoplanet keyword '{kw}' is not lowercase"
        for kw in CMB_KEYWORDS:
            assert kw == kw.lower(), f"CMB keyword '{kw}' is not lowercase"


class TestDetectTopic:
    """Tests for the detect_topic function."""

    def test_detect_dark_matter_explicit(self):
        """Test detection of explicit dark matter queries."""
        assert detect_topic("What is dark matter?") == "dark_matter"
        assert detect_topic("Explain WIMPs and their properties") == "dark_matter"

    def test_detect_dark_matter_rotation_curves(self):
        """Test detection of rotation curve queries."""
        assert detect_topic("Why do galactic rotation curves suggest dark matter?") == "dark_matter"

    def test_detect_exoplanet_explicit(self):
        """Test detection of explicit exoplanet queries."""
        assert detect_topic("How many exoplanets have been discovered?") == "exoplanet"
        assert detect_topic("What is the habitable zone?") == "exoplanet"

    def test_detect_exoplanet_transit_method(self):
        """Test detection of transit-related queries."""
        assert detect_topic("Explain the transit photometry method") == "exoplanet"

    def test_detect_exoplanet_kepler(self):
        """Test detection of Kepler mission queries."""
        assert detect_topic("What did the Kepler mission discover?") == "exoplanet"

    def test_detect_cmb_explicit(self):
        """Test detection of explicit CMB queries."""
        assert detect_topic("What is the cosmic microwave background?") == "cmb"
        assert detect_topic("Analyze CMB anisotropies") == "cmb"

    def test_detect_cmb_planck(self):
        """Test detection of Planck satellite queries."""
        assert detect_topic("What did the Planck satellite measure?") == "cmb"

    def test_detect_cmb_recombination(self):
        """Test detection of recombination epoch queries."""
        assert detect_topic("When did recombination occur in the early universe?") == "cmb"

    def test_detect_no_topic_general(self):
        """Test that general queries return None."""
        assert detect_topic("Calculate escape velocity from Earth") is None
        assert detect_topic("What is a black hole?") is None

    def test_detect_no_topic_empty(self):
        """Test that empty queries return None."""
        assert detect_topic("") is None

    def test_detect_topic_case_insensitive(self):
        """Test that detection is case insensitive."""
        assert detect_topic("DARK MATTER evidence") == "dark_matter"
        assert detect_topic("EXOPLANET detection") == "exoplanet"
        assert detect_topic("CMB ANISOTROPY") == "cmb"


class TestGetTopicContext:
    """Tests for the get_topic_context function."""

    def test_get_dark_matter_context(self):
        """Test getting dark matter context."""
        context = get_topic_context("dark_matter")
        assert context == DARK_MATTER_CONTEXT
        assert len(context) > 0

    def test_get_exoplanet_context(self):
        """Test getting exoplanet context."""
        context = get_topic_context("exoplanet")
        assert context == EXOPLANET_CONTEXT
        assert len(context) > 0

    def test_get_cmb_context(self):
        """Test getting CMB context."""
        context = get_topic_context("cmb")
        assert context == CMB_CONTEXT
        assert len(context) > 0

    def test_get_unknown_topic_returns_empty(self):
        """Test that unknown topic returns empty string."""
        context = get_topic_context("unknown_topic")
        assert context == ""

    def test_get_none_topic_returns_empty(self):
        """Test that None topic returns empty string."""
        context = get_topic_context(None)
        assert context == ""


class TestEnhancePromptForTopic:
    """Tests for the enhance_prompt_for_topic function."""

    def test_enhance_with_dark_matter_query(self):
        """Test that dark matter queries enhance the prompt."""
        base = REACT_SYSTEM_PROMPT
        enhanced = enhance_prompt_for_topic(base, "What is dark matter?")
        assert len(enhanced) > len(base)
        assert DARK_MATTER_CONTEXT in enhanced
        assert base in enhanced

    def test_enhance_with_exoplanet_query(self):
        """Test that exoplanet queries enhance the prompt."""
        base = REACT_SYSTEM_PROMPT
        enhanced = enhance_prompt_for_topic(base, "How do we detect exoplanets?")
        assert len(enhanced) > len(base)
        assert EXOPLANET_CONTEXT in enhanced
        assert base in enhanced

    def test_enhance_with_cmb_query(self):
        """Test that CMB queries enhance the prompt."""
        base = REACT_SYSTEM_PROMPT
        enhanced = enhance_prompt_for_topic(base, "Explain the cosmic microwave background")
        assert len(enhanced) > len(base)
        assert CMB_CONTEXT in enhanced
        assert base in enhanced

    def test_no_enhancement_for_general_query(self):
        """Test that general queries don't change the prompt."""
        base = REACT_SYSTEM_PROMPT
        enhanced = enhance_prompt_for_topic(base, "Calculate escape velocity from Mars")
        assert enhanced == base

    def test_enhancement_preserves_base_prompt(self):
        """Test that enhancement doesn't remove base prompt content."""
        base = "Test base prompt with specific content XYZ123"
        enhanced = enhance_prompt_for_topic(base, "Tell me about dark matter")
        assert "Test base prompt" in enhanced
        assert "XYZ123" in enhanced


class TestAgentTopicPromptIntegration:
    """Tests for agent integration with topic prompts."""

    def test_agent_default_uses_topic_prompts(self):
        """Test that agent defaults to using topic prompts."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent()
        assert agent.use_topic_prompts is True

    def test_agent_can_disable_topic_prompts(self):
        """Test that agent can disable topic prompts."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent(use_topic_prompts=False)
        assert agent.use_topic_prompts is False

    def test_agent_caches_agents_by_prompt(self):
        """Test that agent caches different agents for different prompts."""
        from kosmo.agent import KosmoAgent
        agent = KosmoAgent()
        assert agent._agents == {}  # Empty cache initially
