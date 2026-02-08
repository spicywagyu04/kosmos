"""
Kosmo Examples

Example simulations and calculations demonstrating the capabilities of the
Kosmo cosmology research agent.
"""

from .hohmann_transfer import (
    AU,
    M_SUN,
    PLANETS,
    G,
    HohmannTransferResult,
    calculate_hohmann_transfer,
    calculate_planetary_transfer,
    generate_transfer_plot_code,
    get_earth_mars_example,
)
from .kepler_orbit import (
    M_EARTH,
    SECONDS_PER_DAY,
    SECONDS_PER_YEAR,
    KeplerOrbit,
    OrbitType,
    calculate_circular_velocity,
    calculate_escape_velocity,
    calculate_orbit_from_period,
    calculate_orbit_from_radii,
    calculate_orbit_from_state,
    calculate_orbital_elements,
    generate_orbit_plot_code,
    get_exoplanet_example,
)
from .sample_queries import (
    CALCULATION_QUERIES,
    COSMOLOGY_QUERIES,
    ORBITAL_QUERIES,
    RESEARCH_QUERIES,
    SAMPLE_QUERIES,
    SampleQuery,
    get_queries_by_category,
    get_query_by_name,
    list_all_queries,
    print_query_catalog,
    run_all_queries,
    run_query,
)

__all__ = [
    # Sample queries
    "SampleQuery",
    "SAMPLE_QUERIES",
    "CALCULATION_QUERIES",
    "ORBITAL_QUERIES",
    "RESEARCH_QUERIES",
    "COSMOLOGY_QUERIES",
    "get_query_by_name",
    "get_queries_by_category",
    "list_all_queries",
    "run_query",
    "run_all_queries",
    "print_query_catalog",
    # Constants
    "G",
    "M_SUN",
    "M_EARTH",
    "AU",
    "SECONDS_PER_DAY",
    "SECONDS_PER_YEAR",
    "PLANETS",
    # Hohmann transfer
    "HohmannTransferResult",
    "calculate_hohmann_transfer",
    "calculate_planetary_transfer",
    "generate_transfer_plot_code",
    "get_earth_mars_example",
    # Kepler orbit
    "OrbitType",
    "KeplerOrbit",
    "calculate_orbit_from_period",
    "calculate_orbit_from_radii",
    "calculate_orbit_from_state",
    "calculate_escape_velocity",
    "calculate_circular_velocity",
    "calculate_orbital_elements",
    "generate_orbit_plot_code",
    "get_exoplanet_example",
]
