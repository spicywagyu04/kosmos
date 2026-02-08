"""Tests for demo script documentation."""

import os

import pytest

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
DEMO_SCRIPT_PATH = os.path.join(DOCS_DIR, "DEMO_SCRIPT.md")


class TestDemoScriptExists:
    """Tests for demo script file existence."""

    def test_demo_script_file_exists(self):
        """Test that DEMO_SCRIPT.md exists in docs directory."""
        assert os.path.exists(DEMO_SCRIPT_PATH), "DEMO_SCRIPT.md should exist in docs/"

    def test_demo_script_is_not_empty(self):
        """Test that demo script file is not empty."""
        with open(DEMO_SCRIPT_PATH) as f:
            content = f.read()
        assert len(content) > 0, "DEMO_SCRIPT.md should not be empty"


class TestDemoScriptContent:
    """Tests for demo script content."""

    @pytest.fixture
    def demo_content(self):
        """Load demo script content."""
        with open(DEMO_SCRIPT_PATH) as f:
            return f.read()

    def test_has_title(self, demo_content):
        """Test that demo script has a title."""
        assert "# Demo Recording Script" in demo_content

    def test_has_recording_setup_section(self, demo_content):
        """Test that demo script has recording setup section."""
        assert "## Recording Setup" in demo_content

    def test_has_prerequisites(self, demo_content):
        """Test that demo script lists prerequisites."""
        assert "Prerequisites" in demo_content or "prerequisite" in demo_content.lower()

    def test_has_demo_script_section(self, demo_content):
        """Test that demo script has main demo script section."""
        assert "## Demo Script" in demo_content

    def test_includes_help_command(self, demo_content):
        """Test that demo includes help command demonstration."""
        assert "kosmo --help" in demo_content or "--help" in demo_content

    def test_includes_single_query_demo(self, demo_content):
        """Test that demo includes single query demonstration."""
        assert "-q" in demo_content or "--query" in demo_content

    def test_includes_escape_velocity_example(self, demo_content):
        """Test that demo includes escape velocity example."""
        assert "escape velocity" in demo_content.lower()

    def test_includes_interactive_mode_demo(self, demo_content):
        """Test that demo includes interactive mode demonstration."""
        assert "interactive" in demo_content.lower() or "Interactive" in demo_content

    def test_includes_verbose_mode(self, demo_content):
        """Test that demo shows verbose mode."""
        assert "-v" in demo_content or "--verbose" in demo_content

    def test_includes_recording_tips(self, demo_content):
        """Test that demo includes recording tips."""
        assert "Recording Tips" in demo_content or "Tips" in demo_content


class TestDemoScriptSections:
    """Tests for demo script section structure."""

    @pytest.fixture
    def demo_content(self):
        """Load demo script content."""
        with open(DEMO_SCRIPT_PATH) as f:
            return f.read()

    def test_has_introduction_section(self, demo_content):
        """Test that demo has introduction section."""
        assert "Introduction" in demo_content or "introduction" in demo_content.lower()

    def test_has_installation_section(self, demo_content):
        """Test that demo covers installation."""
        assert "Installation" in demo_content or "pip" in demo_content

    def test_has_calculation_demo(self, demo_content):
        """Test that demo includes calculation example."""
        assert "Calculation" in demo_content or "Calculate" in demo_content

    def test_has_orbital_mechanics_demo(self, demo_content):
        """Test that demo includes orbital mechanics example."""
        assert "Hohmann" in demo_content or "orbital" in demo_content.lower()

    def test_has_post_processing_section(self, demo_content):
        """Test that demo has post-processing instructions."""
        assert "Post-Processing" in demo_content or "GIF" in demo_content


class TestDemoScriptTechnical:
    """Tests for technical accuracy of demo script."""

    @pytest.fixture
    def demo_content(self):
        """Load demo script content."""
        with open(DEMO_SCRIPT_PATH) as f:
            return f.read()

    def test_mentions_api_keys(self, demo_content):
        """Test that demo mentions API key configuration."""
        assert ".env" in demo_content or "API" in demo_content

    def test_mentions_virtual_environment(self, demo_content):
        """Test that demo mentions virtual environment."""
        assert "virtual environment" in demo_content.lower() or "venv" in demo_content

    def test_includes_code_blocks(self, demo_content):
        """Test that demo includes code blocks."""
        assert "```" in demo_content

    def test_includes_bash_examples(self, demo_content):
        """Test that demo includes bash command examples."""
        assert "```bash" in demo_content or "$ " in demo_content

    def test_shows_expected_output(self, demo_content):
        """Test that demo shows expected output."""
        assert "Expected" in demo_content or "output" in demo_content.lower()

    def test_mentions_asciinema(self, demo_content):
        """Test that demo mentions asciinema as recording option."""
        assert "asciinema" in demo_content.lower()

    def test_mentions_gif_conversion(self, demo_content):
        """Test that demo explains GIF conversion."""
        assert "GIF" in demo_content or "gif" in demo_content


class TestDemoScriptReActLoop:
    """Tests for ReAct loop demonstration in demo script."""

    @pytest.fixture
    def demo_content(self):
        """Load demo script content."""
        with open(DEMO_SCRIPT_PATH) as f:
            return f.read()

    def test_shows_thought_step(self, demo_content):
        """Test that demo shows Thought step of ReAct loop."""
        assert "Thought:" in demo_content or "thought" in demo_content.lower()

    def test_shows_action_step(self, demo_content):
        """Test that demo shows Action step of ReAct loop."""
        assert "Action:" in demo_content or "action" in demo_content.lower()

    def test_shows_observation_step(self, demo_content):
        """Test that demo shows Observation step of ReAct loop."""
        assert "Observation:" in demo_content or "observation" in demo_content.lower()

    def test_mentions_react_cycle(self, demo_content):
        """Test that demo mentions the ReAct cycle."""
        assert "Thought-Action-Observation" in demo_content or "ReAct" in demo_content
