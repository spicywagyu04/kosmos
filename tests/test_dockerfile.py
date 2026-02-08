"""Tests for Dockerfile and containerization configuration."""

from pathlib import Path

import pytest

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class TestDockerfileExists:
    """Tests for Dockerfile existence and basic structure."""

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists in project root."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        assert dockerfile_path.exists(), "Dockerfile should exist in project root"

    def test_dockerfile_not_empty(self):
        """Test that Dockerfile is not empty."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        content = dockerfile_path.read_text()
        assert len(content) > 0, "Dockerfile should not be empty"


class TestDockerfileBaseImage:
    """Tests for Dockerfile base image configuration."""

    @pytest.fixture
    def dockerfile_content(self):
        """Load Dockerfile content."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        return dockerfile_path.read_text()

    def test_uses_python_base_image(self, dockerfile_content):
        """Test that Dockerfile uses Python base image."""
        assert "FROM python:" in dockerfile_content

    def test_uses_python_39_or_higher(self, dockerfile_content):
        """Test that Dockerfile uses Python 3.9 or higher."""
        # Check for Python 3.9, 3.10, 3.11, or 3.12
        valid_versions = ["3.9", "3.10", "3.11", "3.12"]
        has_valid_version = any(
            f"python:{v}" in dockerfile_content for v in valid_versions
        )
        assert has_valid_version, "Dockerfile should use Python 3.9+"

    def test_uses_slim_image(self, dockerfile_content):
        """Test that Dockerfile uses slim image for smaller footprint."""
        assert "slim" in dockerfile_content.lower(), "Dockerfile should use slim image"


class TestDockerfileEnvironment:
    """Tests for Dockerfile environment configuration."""

    @pytest.fixture
    def dockerfile_content(self):
        """Load Dockerfile content."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        return dockerfile_path.read_text()

    def test_sets_pythondontwritebytecode(self, dockerfile_content):
        """Test that Dockerfile sets PYTHONDONTWRITEBYTECODE."""
        assert "PYTHONDONTWRITEBYTECODE" in dockerfile_content

    def test_sets_pythonunbuffered(self, dockerfile_content):
        """Test that Dockerfile sets PYTHONUNBUFFERED."""
        assert "PYTHONUNBUFFERED" in dockerfile_content

    def test_sets_working_directory(self, dockerfile_content):
        """Test that Dockerfile sets WORKDIR."""
        assert "WORKDIR" in dockerfile_content


class TestDockerfileDependencies:
    """Tests for Dockerfile dependency installation."""

    @pytest.fixture
    def dockerfile_content(self):
        """Load Dockerfile content."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        return dockerfile_path.read_text()

    def test_copies_requirements(self, dockerfile_content):
        """Test that Dockerfile copies requirements.txt."""
        assert "requirements.txt" in dockerfile_content

    def test_installs_pip_dependencies(self, dockerfile_content):
        """Test that Dockerfile installs pip dependencies."""
        assert "pip install" in dockerfile_content

    def test_copies_source_code(self, dockerfile_content):
        """Test that Dockerfile copies src directory."""
        assert "COPY" in dockerfile_content and "src/" in dockerfile_content

    def test_copies_pyproject(self, dockerfile_content):
        """Test that Dockerfile copies pyproject.toml."""
        assert "pyproject.toml" in dockerfile_content


class TestDockerfileSecurity:
    """Tests for Dockerfile security configuration."""

    @pytest.fixture
    def dockerfile_content(self):
        """Load Dockerfile content."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        return dockerfile_path.read_text()

    def test_creates_non_root_user(self, dockerfile_content):
        """Test that Dockerfile creates non-root user for security."""
        assert "useradd" in dockerfile_content or "adduser" in dockerfile_content

    def test_switches_to_non_root_user(self, dockerfile_content):
        """Test that Dockerfile switches to non-root user."""
        assert "USER" in dockerfile_content

    def test_uses_no_cache_for_pip(self, dockerfile_content):
        """Test that Dockerfile uses --no-cache-dir for pip."""
        assert "--no-cache-dir" in dockerfile_content or "PIP_NO_CACHE_DIR" in dockerfile_content


class TestDockerfileEntrypoint:
    """Tests for Dockerfile entrypoint configuration."""

    @pytest.fixture
    def dockerfile_content(self):
        """Load Dockerfile content."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        return dockerfile_path.read_text()

    def test_has_entrypoint_or_cmd(self, dockerfile_content):
        """Test that Dockerfile has ENTRYPOINT or CMD."""
        assert "ENTRYPOINT" in dockerfile_content or "CMD" in dockerfile_content

    def test_entrypoint_runs_kosmo(self, dockerfile_content):
        """Test that ENTRYPOINT runs kosmo CLI."""
        assert "kosmo" in dockerfile_content.lower()


class TestDockerfileLabels:
    """Tests for Dockerfile metadata labels."""

    @pytest.fixture
    def dockerfile_content(self):
        """Load Dockerfile content."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        return dockerfile_path.read_text()

    def test_has_labels(self, dockerfile_content):
        """Test that Dockerfile has LABEL instructions."""
        assert "LABEL" in dockerfile_content

    def test_has_title_label(self, dockerfile_content):
        """Test that Dockerfile has title label."""
        assert "title" in dockerfile_content.lower() or "description" in dockerfile_content.lower()

    def test_has_version_label(self, dockerfile_content):
        """Test that Dockerfile has version label."""
        assert "version" in dockerfile_content.lower()


class TestDockerignoreFile:
    """Tests for .dockerignore file."""

    def test_dockerignore_exists(self):
        """Test that .dockerignore exists."""
        dockerignore_path = PROJECT_ROOT / ".dockerignore"
        assert dockerignore_path.exists(), ".dockerignore should exist"

    def test_dockerignore_not_empty(self):
        """Test that .dockerignore is not empty."""
        dockerignore_path = PROJECT_ROOT / ".dockerignore"
        content = dockerignore_path.read_text()
        assert len(content) > 0, ".dockerignore should not be empty"

    @pytest.fixture
    def dockerignore_content(self):
        """Load .dockerignore content."""
        dockerignore_path = PROJECT_ROOT / ".dockerignore"
        return dockerignore_path.read_text()

    def test_ignores_git_directory(self, dockerignore_content):
        """Test that .dockerignore excludes .git directory."""
        assert ".git" in dockerignore_content

    def test_ignores_venv(self, dockerignore_content):
        """Test that .dockerignore excludes virtual environment."""
        assert "venv" in dockerignore_content.lower() or ".venv" in dockerignore_content

    def test_ignores_pycache(self, dockerignore_content):
        """Test that .dockerignore excludes __pycache__."""
        assert "__pycache__" in dockerignore_content

    def test_ignores_pytest_cache(self, dockerignore_content):
        """Test that .dockerignore excludes pytest cache."""
        assert ".pytest_cache" in dockerignore_content

    def test_ignores_env_files(self, dockerignore_content):
        """Test that .dockerignore excludes .env files."""
        assert ".env" in dockerignore_content

    def test_ignores_ide_files(self, dockerignore_content):
        """Test that .dockerignore excludes IDE files."""
        has_ide_exclusion = (
            ".idea" in dockerignore_content or
            ".vscode" in dockerignore_content
        )
        assert has_ide_exclusion, ".dockerignore should exclude IDE files"


class TestDockerfileBuildContext:
    """Tests for Dockerfile build context optimization."""

    @pytest.fixture
    def dockerfile_content(self):
        """Load Dockerfile content."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        return dockerfile_path.read_text()

    def test_copies_requirements_before_source(self, dockerfile_content):
        """Test that requirements are copied before source for better caching."""
        lines = dockerfile_content.split('\n')
        req_line = -1
        src_line = -1
        for i, line in enumerate(lines):
            if "COPY" in line and "requirements.txt" in line:
                req_line = i
            if "COPY" in line and "src/" in line:
                if src_line == -1:
                    src_line = i
        if req_line != -1 and src_line != -1:
            assert req_line < src_line, "requirements.txt should be copied before src/"

    def test_installs_deps_before_copying_source(self, dockerfile_content):
        """Test that pip install comes before copying source code."""
        lines = dockerfile_content.split('\n')
        pip_install_line = -1
        copy_src_line = -1
        for i, line in enumerate(lines):
            if "pip install" in line and "requirements" in line.lower():
                pip_install_line = i
            if "COPY" in line and "src/" in line:
                if copy_src_line == -1:
                    copy_src_line = i
        if pip_install_line != -1 and copy_src_line != -1:
            assert pip_install_line < copy_src_line


class TestDockerfileOptimizations:
    """Tests for Dockerfile optimizations."""

    @pytest.fixture
    def dockerfile_content(self):
        """Load Dockerfile content."""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        return dockerfile_path.read_text()

    def test_cleans_apt_cache(self, dockerfile_content):
        """Test that Dockerfile cleans apt cache after install."""
        if "apt-get" in dockerfile_content:
            assert "rm -rf /var/lib/apt/lists" in dockerfile_content

    def test_uses_no_install_recommends(self, dockerfile_content):
        """Test that apt-get uses --no-install-recommends."""
        if "apt-get install" in dockerfile_content:
            assert "--no-install-recommends" in dockerfile_content

    def test_copies_examples_directory(self, dockerfile_content):
        """Test that Dockerfile includes examples directory."""
        assert "examples/" in dockerfile_content
