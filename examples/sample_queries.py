"""
Sample Queries for Kosmo Cosmology Research Agent

This module provides example queries demonstrating the various capabilities
of the Kosmo agent. Each example shows how to use the Python API to ask
different types of cosmology questions.

Usage:
    python -m examples.sample_queries

Or import specific examples:
    from examples.sample_queries import SAMPLE_QUERIES, run_query
"""

from dataclasses import dataclass


@dataclass
class SampleQuery:
    """Represents a sample query with metadata."""

    name: str
    query: str
    category: str
    description: str
    expected_tools: list[str]


# Sample queries organized by category
SAMPLE_QUERIES: list[SampleQuery] = [
    # Basic Calculations
    SampleQuery(
        name="escape_velocity",
        query="Calculate the escape velocity from Earth",
        category="calculation",
        description="Uses code executor to compute v = sqrt(2GM/R)",
        expected_tools=["code_executor"],
    ),
    SampleQuery(
        name="schwarzschild_radius",
        query="What is the Schwarzschild radius of a 10 solar mass black hole?",
        category="calculation",
        description="Calculates the event horizon radius using Rs = 2GM/c^2",
        expected_tools=["code_executor"],
    ),
    SampleQuery(
        name="orbital_period",
        query="Calculate the orbital period of Mars around the Sun",
        category="calculation",
        description="Uses Kepler's third law: T = 2*pi*sqrt(a^3/GM)",
        expected_tools=["code_executor"],
    ),

    # Orbital Mechanics
    SampleQuery(
        name="hohmann_transfer",
        query="Simulate the trajectory of a spacecraft from Earth to Mars using a Hohmann transfer orbit",
        category="orbital_mechanics",
        description="Calculates transfer orbit parameters and delta-v requirements",
        expected_tools=["code_executor", "plotter"],
    ),
    SampleQuery(
        name="exoplanet_orbit",
        query="Plot the orbit of an exoplanet with 2x Earth mass at 1.5 AU from its star",
        category="orbital_mechanics",
        description="Generates orbital visualization using Kepler's laws",
        expected_tools=["code_executor", "plotter"],
    ),
    SampleQuery(
        name="satellite_velocity",
        query="What is the orbital velocity of a satellite in low Earth orbit at 400 km altitude?",
        category="orbital_mechanics",
        description="Calculates circular orbital velocity at specified altitude",
        expected_tools=["code_executor"],
    ),

    # Research Questions
    SampleQuery(
        name="black_hole_research",
        query="What are the latest discoveries about supermassive black holes?",
        category="research",
        description="Searches scientific sources for recent black hole research",
        expected_tools=["web_search"],
    ),
    SampleQuery(
        name="dark_matter",
        query="What is dark matter and what evidence do we have for its existence?",
        category="research",
        description="Retrieves information about dark matter from knowledge base",
        expected_tools=["wikipedia", "web_search"],
    ),
    SampleQuery(
        name="gravitational_waves",
        query="How do LIGO and Virgo detect gravitational waves?",
        category="research",
        description="Explains gravitational wave detection methods",
        expected_tools=["wikipedia", "web_search"],
    ),

    # Cosmology Topics
    SampleQuery(
        name="cmb_temperature",
        query="What is the temperature of the cosmic microwave background and why is it significant?",
        category="cosmology",
        description="Explains CMB temperature and cosmological implications",
        expected_tools=["wikipedia"],
    ),
    SampleQuery(
        name="hubble_constant",
        query="What is the Hubble constant and why is there tension in its measurements?",
        category="cosmology",
        description="Discusses the Hubble tension between different measurement methods",
        expected_tools=["wikipedia", "web_search"],
    ),
    SampleQuery(
        name="expansion_rate",
        query="Calculate the age of the universe given a Hubble constant of 70 km/s/Mpc",
        category="cosmology",
        description="Computes Hubble time as an approximation of universe age",
        expected_tools=["code_executor"],
    ),
]


# Categorized query sets for different use cases
CALCULATION_QUERIES = [q for q in SAMPLE_QUERIES if q.category == "calculation"]
ORBITAL_QUERIES = [q for q in SAMPLE_QUERIES if q.category == "orbital_mechanics"]
RESEARCH_QUERIES = [q for q in SAMPLE_QUERIES if q.category == "research"]
COSMOLOGY_QUERIES = [q for q in SAMPLE_QUERIES if q.category == "cosmology"]


def get_query_by_name(name: str) -> SampleQuery | None:
    """Get a sample query by its name.

    Args:
        name: The name identifier of the query

    Returns:
        The SampleQuery object if found, None otherwise
    """
    for query in SAMPLE_QUERIES:
        if query.name == name:
            return query
    return None


def get_queries_by_category(category: str) -> list[SampleQuery]:
    """Get all sample queries in a specific category.

    Args:
        category: One of 'calculation', 'orbital_mechanics', 'research', 'cosmology'

    Returns:
        List of SampleQuery objects in that category
    """
    return [q for q in SAMPLE_QUERIES if q.category == category]


def list_all_queries() -> list[str]:
    """List all available sample query names.

    Returns:
        List of query name strings
    """
    return [q.name for q in SAMPLE_QUERIES]


def run_query(query: str | SampleQuery, verbose: bool = True) -> str:
    """Run a sample query using the Kosmo agent.

    This function creates a KosmoAgent instance and executes the query,
    returning the agent's response.

    Args:
        query: Either a query string or a SampleQuery object
        verbose: Whether to show intermediate reasoning steps

    Returns:
        The agent's response as a string

    Raises:
        ImportError: If kosmo package is not installed
    """
    try:
        from kosmo import KosmoAgent
    except ImportError as e:
        raise ImportError(
            "kosmo package not found. Install with: pip install -e ."
        ) from e

    query_text = query.query if isinstance(query, SampleQuery) else query

    agent = KosmoAgent(verbose=verbose)
    return agent.query(query_text)


def run_all_queries(verbose: bool = False) -> dict[str, str]:
    """Run all sample queries and collect responses.

    Args:
        verbose: Whether to show intermediate reasoning steps

    Returns:
        Dictionary mapping query names to responses
    """
    results = {}
    for sample in SAMPLE_QUERIES:
        print(f"Running query: {sample.name}...")
        try:
            results[sample.name] = run_query(sample, verbose=verbose)
        except Exception as e:
            results[sample.name] = f"Error: {e}"
    return results


def print_query_catalog():
    """Print a formatted catalog of all sample queries."""
    print("\n" + "=" * 60)
    print("KOSMO SAMPLE QUERY CATALOG")
    print("=" * 60)

    categories = ["calculation", "orbital_mechanics", "research", "cosmology"]

    for category in categories:
        queries = get_queries_by_category(category)
        print(f"\n## {category.upper().replace('_', ' ')}")
        print("-" * 40)
        for q in queries:
            print(f"\n  Name: {q.name}")
            print(f"  Query: \"{q.query}\"")
            print(f"  Tools: {', '.join(q.expected_tools)}")
            print(f"  Description: {q.description}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print_query_catalog()

    print("\n\nTo run a specific query:")
    print("  from examples.sample_queries import run_query, get_query_by_name")
    print("  query = get_query_by_name('escape_velocity')")
    print("  response = run_query(query)")
    print("  print(response)")
