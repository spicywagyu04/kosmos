"""Tests for the CLI module."""

import sys
from unittest.mock import patch

import pytest

from kosmo import __version__
from kosmo.cli import main, print_banner, print_help


class TestPrintBanner:
    """Tests for print_banner function."""

    def test_print_banner_contains_version(self, capsys):
        """Test that banner includes version number."""
        print_banner()
        captured = capsys.readouterr()
        assert __version__ in captured.out

    def test_print_banner_contains_name(self, capsys):
        """Test that banner includes product name."""
        print_banner()
        captured = capsys.readouterr()
        assert "KOSMO" in captured.out
        assert "Cosmology Research Agent" in captured.out

    def test_print_banner_contains_commands(self, capsys):
        """Test that banner includes available commands."""
        print_banner()
        captured = capsys.readouterr()
        assert "quit" in captured.out or "exit" in captured.out
        assert "clear" in captured.out
        assert "help" in captured.out


class TestPrintHelp:
    """Tests for print_help function."""

    def test_print_help_contains_commands(self, capsys):
        """Test that help includes command descriptions."""
        print_help()
        captured = capsys.readouterr()
        assert "quit" in captured.out.lower() or "exit" in captured.out.lower()
        assert "clear" in captured.out.lower()
        assert "help" in captured.out.lower()

    def test_print_help_contains_examples(self, capsys):
        """Test that help includes example questions."""
        print_help()
        captured = capsys.readouterr()
        assert "Example" in captured.out


class TestMainCLI:
    """Tests for main CLI entry point."""

    def test_version_flag(self, capsys):
        """Test --version flag prints version and exits."""
        with patch.object(sys, 'argv', ['kosmo', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert __version__ in captured.out

    def test_help_flag(self, capsys):
        """Test --help flag prints help and exits."""
        with patch.object(sys, 'argv', ['kosmo', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Cosmology Research Agent" in captured.out

    @patch('kosmo.cli.run_single_query')
    def test_single_query_positional(self, mock_query):
        """Test running a single query via positional argument."""
        mock_query.return_value = "Test response"
        with patch.object(sys, 'argv', ['kosmo', 'What is dark matter?']):
            main()
        mock_query.assert_called_once_with('What is dark matter?', verbose=True)

    @patch('kosmo.cli.run_single_query')
    def test_single_query_with_flag(self, mock_query):
        """Test running a single query via -q flag."""
        mock_query.return_value = "Test response"
        with patch.object(sys, 'argv', ['kosmo', '-q', 'Calculate escape velocity']):
            main()
        mock_query.assert_called_once_with('Calculate escape velocity', verbose=True)

    @patch('kosmo.cli.run_single_query')
    def test_quiet_mode(self, mock_query):
        """Test --quiet flag suppresses verbose output."""
        mock_query.return_value = "Test response"
        with patch.object(sys, 'argv', ['kosmo', '--quiet', 'Test query']):
            main()
        mock_query.assert_called_once_with('Test query', verbose=False)

    @patch('kosmo.cli.run_interactive')
    def test_interactive_mode_no_args(self, mock_interactive):
        """Test that no arguments starts interactive mode."""
        with patch.object(sys, 'argv', ['kosmo']):
            main()
        mock_interactive.assert_called_once_with(verbose=True)

    @patch('kosmo.cli.run_single_query')
    def test_error_handling_missing_api_key(self, mock_query, capsys):
        """Test error handling when API key is missing."""
        mock_query.side_effect = ValueError("OPENAI_API_KEY not found")
        with patch.object(sys, 'argv', ['kosmo', 'Test query']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error" in captured.out
