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

__all__ = [
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
