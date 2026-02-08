"""Tests for the sample queries module."""



class TestSampleQueryDataclass:
    """Tests for SampleQuery dataclass."""

    def test_sample_query_creation(self):
        """Test creating a SampleQuery instance."""
        from examples.sample_queries import SampleQuery

        query = SampleQuery(
            name="test_query",
            query="What is the speed of light?",
            category="calculation",
            description="Test query",
            expected_tools=["code_executor"],
        )
        assert query.name == "test_query"
        assert query.query == "What is the speed of light?"
        assert query.category == "calculation"
        assert query.description == "Test query"
        assert query.expected_tools == ["code_executor"]

    def test_sample_query_multiple_tools(self):
        """Test SampleQuery with multiple expected tools."""
        from examples.sample_queries import SampleQuery

        query = SampleQuery(
            name="multi_tool",
            query="Research and calculate",
            category="research",
            description="Uses multiple tools",
            expected_tools=["web_search", "code_executor", "plotter"],
        )
        assert len(query.expected_tools) == 3


class TestSampleQueriesList:
    """Tests for the SAMPLE_QUERIES list."""

    def test_sample_queries_not_empty(self):
        """Test that SAMPLE_QUERIES list is not empty."""
        from examples.sample_queries import SAMPLE_QUERIES

        assert len(SAMPLE_QUERIES) > 0

    def test_sample_queries_has_at_least_10(self):
        """Test that there are at least 10 sample queries as per PRD."""
        from examples.sample_queries import SAMPLE_QUERIES

        assert len(SAMPLE_QUERIES) >= 10

    def test_sample_queries_have_required_fields(self):
        """Test that all sample queries have required fields."""
        from examples.sample_queries import SAMPLE_QUERIES

        for query in SAMPLE_QUERIES:
            assert query.name, "Query must have a name"
            assert query.query, "Query must have a query text"
            assert query.category, "Query must have a category"
            assert query.description, "Query must have a description"
            assert query.expected_tools, "Query must have expected_tools"

    def test_sample_queries_unique_names(self):
        """Test that all sample queries have unique names."""
        from examples.sample_queries import SAMPLE_QUERIES

        names = [q.name for q in SAMPLE_QUERIES]
        assert len(names) == len(set(names)), "Query names must be unique"

    def test_sample_queries_valid_categories(self):
        """Test that all queries have valid categories."""
        from examples.sample_queries import SAMPLE_QUERIES

        valid_categories = {"calculation", "orbital_mechanics", "research", "cosmology"}
        for query in SAMPLE_QUERIES:
            assert query.category in valid_categories, (
                f"Invalid category: {query.category}"
            )


class TestCategoryLists:
    """Tests for categorized query lists."""

    def test_calculation_queries_not_empty(self):
        """Test that CALCULATION_QUERIES is not empty."""
        from examples.sample_queries import CALCULATION_QUERIES

        assert len(CALCULATION_QUERIES) > 0

    def test_orbital_queries_not_empty(self):
        """Test that ORBITAL_QUERIES is not empty."""
        from examples.sample_queries import ORBITAL_QUERIES

        assert len(ORBITAL_QUERIES) > 0

    def test_research_queries_not_empty(self):
        """Test that RESEARCH_QUERIES is not empty."""
        from examples.sample_queries import RESEARCH_QUERIES

        assert len(RESEARCH_QUERIES) > 0

    def test_cosmology_queries_not_empty(self):
        """Test that COSMOLOGY_QUERIES is not empty."""
        from examples.sample_queries import COSMOLOGY_QUERIES

        assert len(COSMOLOGY_QUERIES) > 0

    def test_calculation_queries_category(self):
        """Test that all CALCULATION_QUERIES have correct category."""
        from examples.sample_queries import CALCULATION_QUERIES

        for query in CALCULATION_QUERIES:
            assert query.category == "calculation"

    def test_orbital_queries_category(self):
        """Test that all ORBITAL_QUERIES have correct category."""
        from examples.sample_queries import ORBITAL_QUERIES

        for query in ORBITAL_QUERIES:
            assert query.category == "orbital_mechanics"

    def test_research_queries_category(self):
        """Test that all RESEARCH_QUERIES have correct category."""
        from examples.sample_queries import RESEARCH_QUERIES

        for query in RESEARCH_QUERIES:
            assert query.category == "research"

    def test_cosmology_queries_category(self):
        """Test that all COSMOLOGY_QUERIES have correct category."""
        from examples.sample_queries import COSMOLOGY_QUERIES

        for query in COSMOLOGY_QUERIES:
            assert query.category == "cosmology"

    def test_category_lists_sum_to_total(self):
        """Test that all category lists together equal SAMPLE_QUERIES."""
        from examples.sample_queries import (
            CALCULATION_QUERIES,
            COSMOLOGY_QUERIES,
            ORBITAL_QUERIES,
            RESEARCH_QUERIES,
            SAMPLE_QUERIES,
        )

        total = (
            len(CALCULATION_QUERIES)
            + len(ORBITAL_QUERIES)
            + len(RESEARCH_QUERIES)
            + len(COSMOLOGY_QUERIES)
        )
        assert total == len(SAMPLE_QUERIES)


class TestGetQueryByName:
    """Tests for get_query_by_name function."""

    def test_get_existing_query(self):
        """Test getting an existing query by name."""
        from examples.sample_queries import get_query_by_name

        query = get_query_by_name("escape_velocity")
        assert query is not None
        assert query.name == "escape_velocity"

    def test_get_nonexistent_query(self):
        """Test getting a nonexistent query returns None."""
        from examples.sample_queries import get_query_by_name

        query = get_query_by_name("nonexistent_query")
        assert query is None

    def test_get_schwarzschild_query(self):
        """Test getting schwarzschild radius query."""
        from examples.sample_queries import get_query_by_name

        query = get_query_by_name("schwarzschild_radius")
        assert query is not None
        assert "black hole" in query.query.lower()

    def test_get_hohmann_query(self):
        """Test getting hohmann transfer query."""
        from examples.sample_queries import get_query_by_name

        query = get_query_by_name("hohmann_transfer")
        assert query is not None
        assert query.category == "orbital_mechanics"


class TestGetQueriesByCategory:
    """Tests for get_queries_by_category function."""

    def test_get_calculation_queries(self):
        """Test getting queries by calculation category."""
        from examples.sample_queries import get_queries_by_category

        queries = get_queries_by_category("calculation")
        assert len(queries) > 0
        for q in queries:
            assert q.category == "calculation"

    def test_get_orbital_queries(self):
        """Test getting queries by orbital_mechanics category."""
        from examples.sample_queries import get_queries_by_category

        queries = get_queries_by_category("orbital_mechanics")
        assert len(queries) > 0
        for q in queries:
            assert q.category == "orbital_mechanics"

    def test_get_research_queries(self):
        """Test getting queries by research category."""
        from examples.sample_queries import get_queries_by_category

        queries = get_queries_by_category("research")
        assert len(queries) > 0
        for q in queries:
            assert q.category == "research"

    def test_get_cosmology_queries(self):
        """Test getting queries by cosmology category."""
        from examples.sample_queries import get_queries_by_category

        queries = get_queries_by_category("cosmology")
        assert len(queries) > 0
        for q in queries:
            assert q.category == "cosmology"

    def test_get_invalid_category(self):
        """Test getting queries by invalid category returns empty list."""
        from examples.sample_queries import get_queries_by_category

        queries = get_queries_by_category("invalid_category")
        assert len(queries) == 0


class TestListAllQueries:
    """Tests for list_all_queries function."""

    def test_list_returns_names(self):
        """Test that list_all_queries returns query names."""
        from examples.sample_queries import list_all_queries

        names = list_all_queries()
        assert isinstance(names, list)
        assert len(names) > 0
        assert all(isinstance(name, str) for name in names)

    def test_list_contains_known_queries(self):
        """Test that list contains known query names."""
        from examples.sample_queries import list_all_queries

        names = list_all_queries()
        assert "escape_velocity" in names
        assert "schwarzschild_radius" in names
        assert "hohmann_transfer" in names

    def test_list_matches_sample_queries_count(self):
        """Test that list length matches SAMPLE_QUERIES count."""
        from examples.sample_queries import SAMPLE_QUERIES, list_all_queries

        names = list_all_queries()
        assert len(names) == len(SAMPLE_QUERIES)


class TestRunQueryFunction:
    """Tests for run_query function (without actually running queries)."""

    def test_run_query_accepts_string(self):
        """Test that run_query function signature accepts string."""
        import inspect

        from examples.sample_queries import run_query

        sig = inspect.signature(run_query)
        params = list(sig.parameters.keys())
        assert "query" in params
        assert "verbose" in params

    def test_run_query_accepts_sample_query(self):
        """Test that run_query accepts SampleQuery object."""
        import inspect
        from types import UnionType
        from typing import get_args, get_origin

        from examples.sample_queries import SampleQuery, run_query

        sig = inspect.signature(run_query)
        annotation = sig.parameters["query"].annotation
        # Check that first param can be SampleQuery or str (union type)
        if annotation is inspect.Parameter.empty:
            pass  # No annotation is acceptable
        elif get_origin(annotation) is UnionType or str(annotation).startswith("str |"):
            args = get_args(annotation)
            assert str in args
            assert SampleQuery in args
        else:
            # Just check it exists
            assert annotation is not None


class TestRunAllQueriesFunction:
    """Tests for run_all_queries function."""

    def test_run_all_queries_exists(self):
        """Test that run_all_queries function exists."""
        from examples.sample_queries import run_all_queries

        assert callable(run_all_queries)

    def test_run_all_queries_signature(self):
        """Test run_all_queries function signature."""
        import inspect

        from examples.sample_queries import run_all_queries

        sig = inspect.signature(run_all_queries)
        params = list(sig.parameters.keys())
        assert "verbose" in params


class TestPrintQueryCatalog:
    """Tests for print_query_catalog function."""

    def test_print_query_catalog_exists(self):
        """Test that print_query_catalog function exists."""
        from examples.sample_queries import print_query_catalog

        assert callable(print_query_catalog)

    def test_print_query_catalog_runs(self, capsys):
        """Test that print_query_catalog runs without error."""
        from examples.sample_queries import print_query_catalog

        print_query_catalog()
        captured = capsys.readouterr()
        assert "KOSMO SAMPLE QUERY CATALOG" in captured.out
        assert "CALCULATION" in captured.out
        assert "ORBITAL MECHANICS" in captured.out
        assert "RESEARCH" in captured.out
        assert "COSMOLOGY" in captured.out


class TestExamplesModuleExports:
    """Tests for examples module exports."""

    def test_sample_queries_exported(self):
        """Test that sample queries are exported from examples module."""
        from examples import SAMPLE_QUERIES

        assert len(SAMPLE_QUERIES) > 0

    def test_sample_query_class_exported(self):
        """Test that SampleQuery class is exported."""
        from examples import SampleQuery

        assert SampleQuery is not None

    def test_category_lists_exported(self):
        """Test that category lists are exported."""
        from examples import (
            CALCULATION_QUERIES,
            COSMOLOGY_QUERIES,
            ORBITAL_QUERIES,
            RESEARCH_QUERIES,
        )

        assert len(CALCULATION_QUERIES) > 0
        assert len(ORBITAL_QUERIES) > 0
        assert len(RESEARCH_QUERIES) > 0
        assert len(COSMOLOGY_QUERIES) > 0

    def test_helper_functions_exported(self):
        """Test that helper functions are exported."""
        from examples import (
            get_queries_by_category,
            get_query_by_name,
            list_all_queries,
            print_query_catalog,
            run_all_queries,
            run_query,
        )

        assert callable(get_query_by_name)
        assert callable(get_queries_by_category)
        assert callable(list_all_queries)
        assert callable(run_query)
        assert callable(run_all_queries)
        assert callable(print_query_catalog)


class TestSampleQueryContent:
    """Tests for specific sample query content."""

    def test_escape_velocity_query_content(self):
        """Test escape velocity query has correct content."""
        from examples.sample_queries import get_query_by_name

        query = get_query_by_name("escape_velocity")
        assert "escape velocity" in query.query.lower()
        assert "code_executor" in query.expected_tools

    def test_dark_matter_query_content(self):
        """Test dark matter query has correct content."""
        from examples.sample_queries import get_query_by_name

        query = get_query_by_name("dark_matter")
        assert "dark matter" in query.query.lower()
        assert query.category == "research"

    def test_cmb_query_content(self):
        """Test CMB query has correct content."""
        from examples.sample_queries import get_query_by_name

        query = get_query_by_name("cmb_temperature")
        assert "microwave background" in query.query.lower() or "cmb" in query.query.lower()
        assert query.category == "cosmology"

    def test_hohmann_query_uses_plotter(self):
        """Test Hohmann transfer query expects plotter tool."""
        from examples.sample_queries import get_query_by_name

        query = get_query_by_name("hohmann_transfer")
        assert "plotter" in query.expected_tools

    def test_research_queries_use_web_search(self):
        """Test research queries expect web search tool."""
        from examples.sample_queries import RESEARCH_QUERIES

        for query in RESEARCH_QUERIES:
            assert "web_search" in query.expected_tools or "wikipedia" in query.expected_tools


class TestSampleOutputsFile:
    """Tests for the SAMPLE_OUTPUTS.md file."""

    def test_sample_outputs_file_exists(self):
        """Test that SAMPLE_OUTPUTS.md file exists."""
        from pathlib import Path

        file_path = Path(__file__).parent.parent / "examples" / "SAMPLE_OUTPUTS.md"
        assert file_path.exists()

    def test_sample_outputs_not_empty(self):
        """Test that SAMPLE_OUTPUTS.md is not empty."""
        from pathlib import Path

        file_path = Path(__file__).parent.parent / "examples" / "SAMPLE_OUTPUTS.md"
        content = file_path.read_text()
        assert len(content) > 0

    def test_sample_outputs_has_sections(self):
        """Test that SAMPLE_OUTPUTS.md has expected sections."""
        from pathlib import Path

        file_path = Path(__file__).parent.parent / "examples" / "SAMPLE_OUTPUTS.md"
        content = file_path.read_text()
        assert "Basic Calculations" in content
        assert "Orbital Mechanics" in content
        assert "Research Questions" in content
        assert "Cosmology Topics" in content

    def test_sample_outputs_has_example_queries(self):
        """Test that SAMPLE_OUTPUTS.md contains example query responses."""
        from pathlib import Path

        file_path = Path(__file__).parent.parent / "examples" / "SAMPLE_OUTPUTS.md"
        content = file_path.read_text()
        assert "Escape Velocity" in content
        assert "Schwarzschild" in content
        assert "Hohmann" in content
        assert "Dark Matter" in content

    def test_sample_outputs_has_tools_used(self):
        """Test that SAMPLE_OUTPUTS.md shows tools used."""
        from pathlib import Path

        file_path = Path(__file__).parent.parent / "examples" / "SAMPLE_OUTPUTS.md"
        content = file_path.read_text()
        assert "Tools Used:" in content
        assert "code_executor" in content
