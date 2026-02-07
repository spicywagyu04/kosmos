"""
Hohmann Transfer Orbit Simulation

This module provides functions to calculate and visualize Hohmann transfer orbits,
which are the most fuel-efficient method for transferring between two circular orbits.

A Hohmann transfer uses two engine burns:
1. First burn: Raises the apoapsis to the target orbit altitude
2. Second burn: Circularizes the orbit at the target altitude

This is commonly used for interplanetary missions (e.g., Earth to Mars transfers).
"""

import math
from dataclasses import dataclass
from typing import Optional

# Physical constants
G = 6.67430e-11  # Gravitational constant (m³/kg/s²)
M_SUN = 1.989e30  # Solar mass (kg)
AU = 1.496e11  # Astronomical unit (m)

# Planetary data (semi-major axis in AU, for circular orbit approximation)
PLANETS = {
    "mercury": 0.387,
    "venus": 0.723,
    "earth": 1.000,
    "mars": 1.524,
    "jupiter": 5.203,
    "saturn": 9.537,
    "uranus": 19.191,
    "neptune": 30.069,
}


@dataclass
class HohmannTransferResult:
    """Results of a Hohmann transfer calculation."""

    # Orbital radii
    r1: float  # Inner orbit radius (m)
    r2: float  # Outer orbit radius (m)

    # Transfer orbit parameters
    semi_major_axis: float  # Transfer orbit semi-major axis (m)
    eccentricity: float  # Transfer orbit eccentricity
    transfer_time: float  # Transfer time (seconds)

    # Velocities
    v1_circular: float  # Circular velocity at inner orbit (m/s)
    v2_circular: float  # Circular velocity at outer orbit (m/s)
    v_periapsis: float  # Velocity at periapsis of transfer orbit (m/s)
    v_apoapsis: float  # Velocity at apoapsis of transfer orbit (m/s)

    # Delta-v requirements
    delta_v1: float  # First burn delta-v (m/s)
    delta_v2: float  # Second burn delta-v (m/s)
    total_delta_v: float  # Total delta-v (m/s)

    def __str__(self) -> str:
        """Return a formatted string representation of the results."""
        days = self.transfer_time / 86400
        return (
            f"Hohmann Transfer Orbit Results:\n"
            f"{'=' * 40}\n"
            f"Inner orbit radius: {self.r1 / AU:.3f} AU\n"
            f"Outer orbit radius: {self.r2 / AU:.3f} AU\n"
            f"\n"
            f"Transfer Orbit:\n"
            f"  Semi-major axis: {self.semi_major_axis / AU:.3f} AU\n"
            f"  Eccentricity: {self.eccentricity:.4f}\n"
            f"  Transfer time: {days:.1f} days ({days / 365.25:.2f} years)\n"
            f"\n"
            f"Velocities:\n"
            f"  Circular velocity at r1: {self.v1_circular / 1000:.2f} km/s\n"
            f"  Circular velocity at r2: {self.v2_circular / 1000:.2f} km/s\n"
            f"  Transfer periapsis velocity: {self.v_periapsis / 1000:.2f} km/s\n"
            f"  Transfer apoapsis velocity: {self.v_apoapsis / 1000:.2f} km/s\n"
            f"\n"
            f"Delta-v Requirements:\n"
            f"  First burn (departure): {self.delta_v1 / 1000:.2f} km/s\n"
            f"  Second burn (arrival): {self.delta_v2 / 1000:.2f} km/s\n"
            f"  Total delta-v: {self.total_delta_v / 1000:.2f} km/s\n"
        )


def calculate_hohmann_transfer(
    r1: float,
    r2: float,
    mu: float = G * M_SUN,
) -> HohmannTransferResult:
    """
    Calculate the parameters of a Hohmann transfer orbit.

    Args:
        r1: Radius of the inner (departure) circular orbit in meters
        r2: Radius of the outer (arrival) circular orbit in meters
        mu: Gravitational parameter (G * M) of the central body in m³/s²
            Defaults to heliocentric (Sun-centered) value.

    Returns:
        HohmannTransferResult containing all transfer parameters

    Raises:
        ValueError: If r1 >= r2 (inner orbit must be smaller than outer orbit)

    Example:
        >>> # Earth to Mars transfer
        >>> result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        >>> print(f"Transfer time: {result.transfer_time / 86400:.1f} days")
    """
    if r1 >= r2:
        raise ValueError("Inner orbit radius must be less than outer orbit radius")

    if r1 <= 0 or r2 <= 0:
        raise ValueError("Orbital radii must be positive")

    # Transfer orbit semi-major axis
    a_transfer = (r1 + r2) / 2

    # Transfer orbit eccentricity
    e_transfer = (r2 - r1) / (r2 + r1)

    # Circular velocities at each orbit
    v1_circular = math.sqrt(mu / r1)
    v2_circular = math.sqrt(mu / r2)

    # Velocities at periapsis and apoapsis of transfer orbit (vis-viva equation)
    v_periapsis = math.sqrt(mu * (2 / r1 - 1 / a_transfer))
    v_apoapsis = math.sqrt(mu * (2 / r2 - 1 / a_transfer))

    # Delta-v for each burn
    delta_v1 = v_periapsis - v1_circular  # Speed up to enter transfer orbit
    delta_v2 = v2_circular - v_apoapsis  # Speed up to circularize at target

    # Transfer time (half the orbital period of the transfer ellipse)
    transfer_time = math.pi * math.sqrt(a_transfer**3 / mu)

    return HohmannTransferResult(
        r1=r1,
        r2=r2,
        semi_major_axis=a_transfer,
        eccentricity=e_transfer,
        transfer_time=transfer_time,
        v1_circular=v1_circular,
        v2_circular=v2_circular,
        v_periapsis=v_periapsis,
        v_apoapsis=v_apoapsis,
        delta_v1=delta_v1,
        delta_v2=delta_v2,
        total_delta_v=delta_v1 + delta_v2,
    )


def calculate_planetary_transfer(
    origin: str,
    destination: str,
) -> HohmannTransferResult:
    """
    Calculate a Hohmann transfer between two planets in our solar system.

    Uses circular orbit approximations for simplicity.

    Args:
        origin: Name of the origin planet (case-insensitive)
        destination: Name of the destination planet (case-insensitive)

    Returns:
        HohmannTransferResult containing all transfer parameters

    Raises:
        ValueError: If planet names are invalid or origin orbit is larger than destination

    Example:
        >>> result = calculate_planetary_transfer("earth", "mars")
        >>> print(f"Total delta-v: {result.total_delta_v / 1000:.2f} km/s")
    """
    origin_lower = origin.lower()
    destination_lower = destination.lower()

    if origin_lower not in PLANETS:
        raise ValueError(
            f"Unknown planet: {origin}. Valid options: {list(PLANETS.keys())}"
        )
    if destination_lower not in PLANETS:
        raise ValueError(
            f"Unknown planet: {destination}. Valid options: {list(PLANETS.keys())}"
        )

    r1 = PLANETS[origin_lower] * AU
    r2 = PLANETS[destination_lower] * AU

    # Swap if going inward
    if r1 > r2:
        r1, r2 = r2, r1

    return calculate_hohmann_transfer(r1, r2)


def generate_transfer_plot_code(
    result: HohmannTransferResult,
    origin_name: str = "Origin",
    destination_name: str = "Destination",
    title: Optional[str] = None,
) -> str:
    """
    Generate matplotlib code to visualize a Hohmann transfer orbit.

    This code can be executed by the create_plot tool.

    Args:
        result: HohmannTransferResult from calculate_hohmann_transfer
        origin_name: Display name for the origin body
        destination_name: Display name for the destination body
        title: Optional custom title for the plot

    Returns:
        String containing Python/matplotlib code to generate the plot
    """
    r1_au = result.r1 / AU
    r2_au = result.r2 / AU
    a_au = result.semi_major_axis / AU
    e = result.eccentricity

    if title is None:
        title = f"Hohmann Transfer: {origin_name} to {destination_name}"

    code = f'''
# Hohmann Transfer Orbit Visualization
# Note: np, plt, and physics constants are pre-loaded by the plotter sandbox

# Orbital parameters
r1 = {r1_au}  # Inner orbit radius (AU)
r2 = {r2_au}  # Outer orbit radius (AU)
a = {a_au}  # Transfer orbit semi-major axis (AU)
e = {e}  # Transfer orbit eccentricity

# Create figure
fig, ax = plt.subplots(figsize=(10, 10))

# Draw the Sun at the center
ax.plot(0, 0, 'yo', markersize=20, label='Sun')

# Draw inner circular orbit (origin)
theta_circle = np.linspace(0, 2 * np.pi, 100)
x_inner = r1 * np.cos(theta_circle)
y_inner = r1 * np.sin(theta_circle)
ax.plot(x_inner, y_inner, 'b--', linewidth=1.5, label='{origin_name} Orbit')

# Draw outer circular orbit (destination)
x_outer = r2 * np.cos(theta_circle)
y_outer = r2 * np.sin(theta_circle)
ax.plot(x_outer, y_outer, 'r--', linewidth=1.5, label='{destination_name} Orbit')

# Draw transfer orbit (ellipse)
# The ellipse has the Sun at one focus, periapsis at r1, apoapsis at r2
# Only draw the transfer arc (half ellipse)
theta_transfer = np.linspace(0, np.pi, 100)
# Polar equation of ellipse with focus at origin
r_transfer = a * (1 - e**2) / (1 + e * np.cos(theta_transfer))
x_transfer = r_transfer * np.cos(theta_transfer)
y_transfer = r_transfer * np.sin(theta_transfer)
ax.plot(x_transfer, y_transfer, 'g-', linewidth=2.5, label='Transfer Orbit')

# Mark key points
# Departure point (periapsis)
ax.plot(r1, 0, 'bo', markersize=12, zorder=5)
ax.annotate('Departure\\n(Burn 1)', (r1, 0), textcoords="offset points",
            xytext=(15, 15), ha='left', fontsize=10,
            arrowprops=dict(arrowstyle='->', color='blue'))

# Arrival point (apoapsis)
ax.plot(-r2, 0, 'ro', markersize=12, zorder=5)
ax.annotate('Arrival\\n(Burn 2)', (-r2, 0), textcoords="offset points",
            xytext=(-15, 15), ha='right', fontsize=10,
            arrowprops=dict(arrowstyle='->', color='red'))

# Draw velocity vectors at departure
arrow_scale = 0.15
# Initial circular velocity
ax.annotate('', xy=(r1, arrow_scale), xytext=(r1, 0),
            arrowprops=dict(arrowstyle='->', color='blue', lw=2))
ax.text(r1 + 0.05, arrow_scale/2, 'v₁', fontsize=10, color='blue')

# Add direction arrow on transfer orbit
mid_idx = len(theta_transfer) // 2
ax.annotate('', xy=(x_transfer[mid_idx+5], y_transfer[mid_idx+5]),
            xytext=(x_transfer[mid_idx], y_transfer[mid_idx]),
            arrowprops=dict(arrowstyle='->', color='green', lw=2))

# Formatting
ax.set_xlim(-r2 * 1.3, r2 * 1.3)
ax.set_ylim(-r2 * 1.3, r2 * 1.3)
ax.set_aspect('equal')
ax.set_xlabel('Distance (AU)', fontsize=12)
ax.set_ylabel('Distance (AU)', fontsize=12)
ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, alpha=0.3)

# Add text box with transfer info
transfer_days = {result.transfer_time / 86400:.1f}
delta_v_kms = {result.total_delta_v / 1000:.2f}
textstr = 'Transfer Time: ' + str(transfer_days) + ' days\\nTotal Δv: ' + str(delta_v_kms) + ' km/s'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=props)

plt.tight_layout()
'''
    return code


def get_earth_mars_example() -> tuple[HohmannTransferResult, str]:
    """
    Get a complete example of an Earth-to-Mars Hohmann transfer.

    Returns:
        Tuple of (HohmannTransferResult, plot_code_string)

    Example:
        >>> result, plot_code = get_earth_mars_example()
        >>> print(result)
        >>> # Execute plot_code with create_plot to visualize
    """
    result = calculate_planetary_transfer("earth", "mars")
    plot_code = generate_transfer_plot_code(result, "Earth", "Mars")
    return result, plot_code


# Example usage when run directly
if __name__ == "__main__":
    print("=" * 60)
    print("HOHMANN TRANSFER ORBIT SIMULATION")
    print("=" * 60)
    print()

    # Earth to Mars example
    print("Example: Earth to Mars Transfer")
    print("-" * 40)
    result = calculate_planetary_transfer("earth", "mars")
    print(result)

    # Show other planetary transfers
    print("\nOther Planetary Transfer Examples:")
    print("-" * 40)

    transfers = [
        ("Earth", "Venus"),
        ("Earth", "Jupiter"),
        ("Mars", "Jupiter"),
    ]

    for origin, destination in transfers:
        try:
            r = calculate_planetary_transfer(origin, destination)
            print(f"{origin} to {destination}:")
            print(f"  Transfer time: {r.transfer_time / 86400:.1f} days")
            print(f"  Total Δv: {r.total_delta_v / 1000:.2f} km/s")
            print()
        except ValueError as e:
            print(f"{origin} to {destination}: {e}")
            print()
