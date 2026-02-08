"""Tests for documentation completeness and content validation."""

from pathlib import Path

import pytest

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class TestEthicalUsageDocumentation:
    """Tests for ethical usage and simulation disclaimers documentation."""

    def test_ethical_usage_file_exists(self):
        """Test that ethical_usage.md exists in docs folder."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        assert ethical_usage_path.exists(), "docs/ethical_usage.md should exist"

    def test_ethical_usage_file_not_empty(self):
        """Test that ethical_usage.md is not empty."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        content = ethical_usage_path.read_text()
        assert len(content) > 0, "docs/ethical_usage.md should not be empty"

    def test_ethical_usage_has_title(self):
        """Test that ethical_usage.md has a proper title."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        content = ethical_usage_path.read_text()
        assert "# Ethical Usage" in content or "# ETHICAL USAGE" in content.upper()

    def test_ethical_usage_has_simulation_disclaimers_section(self):
        """Test that ethical_usage.md has a simulation disclaimers section."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        content = ethical_usage_path.read_text()
        assert "Simulation Disclaimer" in content or "simulation disclaimer" in content.lower()

    def test_ethical_usage_has_purpose_section(self):
        """Test that ethical_usage.md describes the purpose and scope."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        content = ethical_usage_path.read_text()
        assert "Purpose" in content or "Scope" in content

    def test_ethical_usage_mentions_educational_purpose(self):
        """Test that the document mentions educational purpose."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        content = ethical_usage_path.read_text()
        assert "educational" in content.lower()

    def test_ethical_usage_mentions_verification(self):
        """Test that the document mentions verification/validation."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        content = ethical_usage_path.read_text()
        assert "verify" in content.lower() or "validation" in content.lower()

    def test_ethical_usage_mentions_limitations(self):
        """Test that the document mentions limitations."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        content = ethical_usage_path.read_text()
        assert "limitation" in content.lower()

    def test_ethical_usage_mentions_no_warranty(self):
        """Test that the document includes no warranty disclaimer."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        content = ethical_usage_path.read_text()
        # Check for warranty disclaimer language
        assert "warranty" in content.lower() or "as-is" in content.lower()

    def test_ethical_usage_mentions_not_for_mission_critical(self):
        """Test that the document warns against mission-critical use."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        content = ethical_usage_path.read_text()
        assert "mission" in content.lower() or "critical" in content.lower()

    def test_ethical_usage_has_data_sources_section(self):
        """Test that the document describes data sources."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        content = ethical_usage_path.read_text()
        assert "Data Source" in content or "data source" in content.lower()

    def test_ethical_usage_mentions_llm_limitations(self):
        """Test that the document mentions LLM limitations."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        content = ethical_usage_path.read_text()
        assert "LLM" in content or "language model" in content.lower()

    def test_ethical_usage_has_best_practices(self):
        """Test that the document includes best practices."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        content = ethical_usage_path.read_text()
        assert "Best Practice" in content or "best practice" in content.lower()


class TestReadmeDisclaimer:
    """Tests for README disclaimer section."""

    def test_readme_exists(self):
        """Test that README.md exists."""
        readme_path = PROJECT_ROOT / "README.md"
        assert readme_path.exists(), "README.md should exist"

    def test_readme_has_disclaimer_section(self):
        """Test that README.md has a disclaimer section."""
        readme_path = PROJECT_ROOT / "README.md"
        content = readme_path.read_text()
        assert "## Disclaimer" in content or "## DISCLAIMER" in content.upper()

    def test_readme_mentions_educational_purpose(self):
        """Test that README mentions educational purpose."""
        readme_path = PROJECT_ROOT / "README.md"
        content = readme_path.read_text()
        assert "educational" in content.lower()

    def test_readme_mentions_verification(self):
        """Test that README mentions verification."""
        readme_path = PROJECT_ROOT / "README.md"
        content = readme_path.read_text()
        assert "verify" in content.lower() or "verification" in content.lower()

    def test_readme_links_to_ethical_usage(self):
        """Test that README links to ethical usage documentation."""
        readme_path = PROJECT_ROOT / "README.md"
        content = readme_path.read_text()
        assert "ethical_usage.md" in content or "ethical-usage" in content.lower()

    def test_readme_mentions_simulation_accuracy(self):
        """Test that README mentions simulation accuracy concerns."""
        readme_path = PROJECT_ROOT / "README.md"
        content = readme_path.read_text()
        assert "accuracy" in content.lower() or "simplified" in content.lower()

    def test_readme_mentions_no_warranty(self):
        """Test that README includes no warranty statement."""
        readme_path = PROJECT_ROOT / "README.md"
        content = readme_path.read_text()
        assert "warranty" in content.lower() or "as-is" in content.lower()

    def test_readme_warns_against_mission_critical_use(self):
        """Test that README warns against mission-critical use."""
        readme_path = PROJECT_ROOT / "README.md"
        content = readme_path.read_text()
        assert "mission-critical" in content.lower() or "not for" in content.lower()


class TestDocumentationStructure:
    """Tests for overall documentation structure."""

    def test_docs_directory_exists(self):
        """Test that docs directory exists."""
        docs_path = PROJECT_ROOT / "docs"
        assert docs_path.exists(), "docs/ directory should exist"
        assert docs_path.is_dir(), "docs should be a directory"

    def test_architecture_doc_exists(self):
        """Test that architecture.md exists."""
        arch_path = PROJECT_ROOT / "docs" / "architecture.md"
        assert arch_path.exists(), "docs/architecture.md should exist"

    def test_all_required_docs_exist(self):
        """Test that all required documentation files exist."""
        required_docs = [
            "docs/architecture.md",
            "docs/ethical_usage.md",
        ]
        for doc in required_docs:
            doc_path = PROJECT_ROOT / doc
            assert doc_path.exists(), f"{doc} should exist"


class TestEthicalUsageContent:
    """Detailed content tests for ethical usage documentation."""

    @pytest.fixture
    def ethical_content(self):
        """Load ethical usage content."""
        ethical_usage_path = PROJECT_ROOT / "docs" / "ethical_usage.md"
        return ethical_usage_path.read_text()

    def test_has_table_of_contents(self, ethical_content):
        """Test that document has a table of contents."""
        assert "Table of Contents" in ethical_content or "Contents" in ethical_content

    def test_mentions_api_privacy(self, ethical_content):
        """Test that document mentions API/data privacy."""
        assert "privacy" in ethical_content.lower() or "API" in ethical_content

    def test_mentions_academic_integrity(self, ethical_content):
        """Test that document mentions academic integrity."""
        assert "academic" in ethical_content.lower() or "integrity" in ethical_content.lower()

    def test_mentions_citation_requirements(self, ethical_content):
        """Test that document discusses citation requirements."""
        assert "cit" in ethical_content.lower()  # cite, citation, citing

    def test_mentions_simplified_models(self, ethical_content):
        """Test that document explains simplified models."""
        assert "simplified" in ethical_content.lower() or "idealized" in ethical_content.lower()

    def test_mentions_physical_constants(self, ethical_content):
        """Test that document discusses physical constants."""
        assert "constant" in ethical_content.lower()

    def test_mentions_orbital_mechanics_limitations(self, ethical_content):
        """Test that document mentions orbital mechanics limitations."""
        assert "orbital" in ethical_content.lower() or "orbit" in ethical_content.lower()

    def test_provides_guidance_for_students(self, ethical_content):
        """Test that document provides guidance for students."""
        assert "student" in ethical_content.lower()

    def test_provides_guidance_for_researchers(self, ethical_content):
        """Test that document provides guidance for researchers."""
        assert "researcher" in ethical_content.lower()

    def test_mentions_cross_reference_tools(self, ethical_content):
        """Test that document mentions cross-reference tools."""
        assert "NASA" in ethical_content or "GMAT" in ethical_content or "STK" in ethical_content

    def test_has_contact_or_feedback_section(self, ethical_content):
        """Test that document has contact or feedback information."""
        assert "contact" in ethical_content.lower() or "feedback" in ethical_content.lower()

    def test_has_last_updated_date(self, ethical_content):
        """Test that document has a last updated date."""
        assert "2026" in ethical_content or "updated" in ethical_content.lower()


class TestLicenseFile:
    """Tests for MIT LICENSE file."""

    def test_license_file_exists(self):
        """Test that LICENSE file exists in project root."""
        license_path = PROJECT_ROOT / "LICENSE"
        assert license_path.exists(), "LICENSE file should exist in project root"

    def test_license_file_not_empty(self):
        """Test that LICENSE file is not empty."""
        license_path = PROJECT_ROOT / "LICENSE"
        content = license_path.read_text()
        assert len(content) > 0, "LICENSE file should not be empty"

    def test_license_is_mit(self):
        """Test that LICENSE file contains MIT License."""
        license_path = PROJECT_ROOT / "LICENSE"
        content = license_path.read_text()
        assert "MIT License" in content, "LICENSE should be MIT License"

    def test_license_has_copyright_notice(self):
        """Test that LICENSE has copyright notice."""
        license_path = PROJECT_ROOT / "LICENSE"
        content = license_path.read_text()
        assert "Copyright" in content, "LICENSE should have copyright notice"

    def test_license_has_year(self):
        """Test that LICENSE has a year in copyright."""
        license_path = PROJECT_ROOT / "LICENSE"
        content = license_path.read_text()
        assert "2026" in content, "LICENSE should have current year (2026)"

    def test_license_has_permission_grant(self):
        """Test that LICENSE has permission grant clause."""
        license_path = PROJECT_ROOT / "LICENSE"
        content = license_path.read_text()
        assert "Permission is hereby granted" in content

    def test_license_has_no_warranty(self):
        """Test that LICENSE has no warranty clause."""
        license_path = PROJECT_ROOT / "LICENSE"
        content = license_path.read_text()
        assert "WITHOUT WARRANTY" in content or "AS IS" in content

    def test_license_allows_commercial_use(self):
        """Test that LICENSE allows commercial use (MIT characteristic)."""
        license_path = PROJECT_ROOT / "LICENSE"
        content = license_path.read_text()
        # MIT license allows selling copies
        assert "sell" in content.lower()

    def test_license_requires_attribution(self):
        """Test that LICENSE requires attribution (MIT characteristic)."""
        license_path = PROJECT_ROOT / "LICENSE"
        content = license_path.read_text()
        # MIT requires including copyright notice
        assert "copyright notice" in content.lower() or "permission notice" in content.lower()

    def test_license_has_liability_disclaimer(self):
        """Test that LICENSE has liability disclaimer."""
        license_path = PROJECT_ROOT / "LICENSE"
        content = license_path.read_text()
        assert "LIABILITY" in content or "liable" in content.lower()
