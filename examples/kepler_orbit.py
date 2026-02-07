"""
Kepler Orbit Calculator

This module provides functions to calculate and visualize Keplerian orbits
using Kepler's laws of planetary motion.

Kepler's Laws:
1. First Law: Planets move in elliptical orbits with the Sun at one focus
2. Second Law: A line from the Sun to a planet sweeps equal areas in equal times
3. Third Law: T² ∝ a³ (orbital period squared is proportional to semi-major axis cubed)

This module supports:
- Calculating orbital parameters from various input combinations
- Computing position and velocity at any point in the orbit
- Generating visualization code for orbits
- Exoplanet orbit calculations
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Physical constants
G = 6.67430e-11  # Gravitational constant (m³/kg/s²)
M_SUN = 1.989e30  # Solar mass (kg)
M_EARTH = 5.972e24  # Earth mass (kg)
AU = 1.496e11  # Astronomical unit (m)
SECONDS_PER_DAY = 86400
SECONDS_PER_YEAR = 365.25 * SECONDS_PER_DAY


class OrbitType(Enum):
    """Classification of orbit types based on eccentricity."""

    CIRCULAR = "circular"  # e = 0
    ELLIPTICAL = "elliptical"  # 0 < e < 1
    PARABOLIC = "parabolic"  # e = 1
    HYPERBOLIC = "hyperbolic"  # e > 1


@dataclass
class KeplerOrbit:
    """Represents a Keplerian orbit with all orbital elements."""

    # Primary orbital elements
    semi_major_axis: float  # a (m)
    eccentricity: float  # e (dimensionless)
    inclination: float = 0.0  # i (radians)
    longitude_ascending_node: float = 0.0  # Ω (radians)
    argument_of_periapsis: float = 0.0  # ω (radians)
    true_anomaly: float = 0.0  # ν (radians) - position at epoch

    # Central body properties
    central_mass: float = M_SUN  # Mass of central body (kg)

    # Derived properties (calculated in __post_init__)
    semi_minor_axis: float = 0.0  # b (m)
    periapsis: float = 0.0  # Closest approach (m)
    apoapsis: float = 0.0  # Farthest distance (m) - only for bound orbits
    orbital_period: float = 0.0  # T (seconds) - only for bound orbits
    mean_motion: float = 0.0  # n (rad/s) - only for bound orbits
    specific_orbital_energy: float = 0.0  # ε (J/kg)
    specific_angular_momentum: float = 0.0  # h (m²/s)

    def __post_init__(self) -> None:
        """Calculate derived orbital properties."""
        a = self.semi_major_axis
        e = self.eccentricity
        mu = G * self.central_mass

        # Semi-minor axis (only meaningful for elliptical orbits)
        if e < 1:
            self.semi_minor_axis = a * math.sqrt(1 - e**2)
        else:
            # For hyperbolic orbits, b is imaginary; we use |b|
            self.semi_minor_axis = abs(a) * math.sqrt(abs(e**2 - 1))

        # Periapsis distance
        self.periapsis = a * (1 - e)

        # Apoapsis distance (only for bound orbits)
        if e < 1:
            self.apoapsis = a * (1 + e)
        else:
            self.apoapsis = float("inf")

        # Orbital period (Kepler's third law) - only for bound orbits
        if e < 1:
            self.orbital_period = 2 * math.pi * math.sqrt(a**3 / mu)
            self.mean_motion = 2 * math.pi / self.orbital_period
        else:
            self.orbital_period = float("inf")
            self.mean_motion = 0.0

        # Specific orbital energy (vis-viva)
        self.specific_orbital_energy = -mu / (2 * a)

        # Specific angular momentum
        self.specific_angular_momentum = math.sqrt(mu * a * (1 - e**2))

    @property
    def orbit_type(self) -> OrbitType:
        """Classify the orbit based on eccentricity."""
        if self.eccentricity == 0:
            return OrbitType.CIRCULAR
        elif self.eccentricity < 1:
            return OrbitType.ELLIPTICAL
        elif self.eccentricity == 1:
            return OrbitType.PARABOLIC
        else:
            return OrbitType.HYPERBOLIC

    def radius_at_true_anomaly(self, nu: float) -> float:
        """
        Calculate the orbital radius at a given true anomaly.

        Args:
            nu: True anomaly in radians

        Returns:
            Radius in meters
        """
        a = self.semi_major_axis
        e = self.eccentricity
        return a * (1 - e**2) / (1 + e * math.cos(nu))

    def velocity_at_radius(self, r: float) -> float:
        """
        Calculate the orbital velocity at a given radius using vis-viva equation.

        Args:
            r: Radius in meters

        Returns:
            Velocity in m/s
        """
        mu = G * self.central_mass
        a = self.semi_major_axis
        return math.sqrt(mu * (2 / r - 1 / a))

    def velocity_at_true_anomaly(self, nu: float) -> float:
        """
        Calculate the orbital velocity at a given true anomaly.

        Args:
            nu: True anomaly in radians

        Returns:
            Velocity in m/s
        """
        r = self.radius_at_true_anomaly(nu)
        return self.velocity_at_radius(r)

    def position_at_true_anomaly(self, nu: float) -> tuple[float, float]:
        """
        Calculate the x, y position in the orbital plane at a given true anomaly.

        Args:
            nu: True anomaly in radians

        Returns:
            Tuple of (x, y) coordinates in meters
        """
        r = self.radius_at_true_anomaly(nu)
        x = r * math.cos(nu)
        y = r * math.sin(nu)
        return x, y

    def period_in_days(self) -> float:
        """Return the orbital period in Earth days."""
        return self.orbital_period / SECONDS_PER_DAY

    def period_in_years(self) -> float:
        """Return the orbital period in Earth years."""
        return self.orbital_period / SECONDS_PER_YEAR

    def __str__(self) -> str:
        """Return a formatted string representation of the orbit."""
        orbit_type = self.orbit_type.value.capitalize()
        lines = [
            f"Keplerian Orbit ({orbit_type})",
            "=" * 40,
            f"Semi-major axis (a): {self.semi_major_axis / AU:.6f} AU",
            f"Eccentricity (e): {self.eccentricity:.6f}",
        ]

        if self.eccentricity < 1:
            lines.extend(
                [
                    f"Semi-minor axis (b): {self.semi_minor_axis / AU:.6f} AU",
                    f"Periapsis: {self.periapsis / AU:.6f} AU",
                    f"Apoapsis: {self.apoapsis / AU:.6f} AU",
                    f"Orbital period: {self.period_in_days():.2f} days "
                    f"({self.period_in_years():.4f} years)",
                ]
            )
        else:
            lines.extend(
                [
                    f"Periapsis: {self.periapsis / AU:.6f} AU",
                    "Apoapsis: ∞ (unbound orbit)",
                ]
            )

        lines.extend(
            [
                "",
                "Velocities:",
                f"  At periapsis: {self.velocity_at_radius(self.periapsis) / 1000:.3f} km/s",
            ]
        )

        if self.eccentricity < 1:
            lines.append(
                f"  At apoapsis: {self.velocity_at_radius(self.apoapsis) / 1000:.3f} km/s"
            )

        return "\n".join(lines)


def calculate_orbit_from_period(
    period_days: float,
    eccentricity: float = 0.0,
    central_mass: float = M_SUN,
) -> KeplerOrbit:
    """
    Calculate orbital parameters given the orbital period.

    Uses Kepler's third law: T² = (4π²/GM) * a³

    Args:
        period_days: Orbital period in Earth days
        eccentricity: Orbital eccentricity (0 for circular)
        central_mass: Mass of the central body in kg

    Returns:
        KeplerOrbit with calculated parameters

    Raises:
        ValueError: If period is not positive or eccentricity is invalid
    """
    if period_days <= 0:
        raise ValueError("Orbital period must be positive")
    if eccentricity < 0:
        raise ValueError("Eccentricity cannot be negative")
    if eccentricity >= 1:
        raise ValueError("Bound orbits must have eccentricity < 1")

    period_seconds = period_days * SECONDS_PER_DAY
    mu = G * central_mass

    # Kepler's third law solved for a
    a = (mu * (period_seconds / (2 * math.pi)) ** 2) ** (1 / 3)

    return KeplerOrbit(
        semi_major_axis=a,
        eccentricity=eccentricity,
        central_mass=central_mass,
    )


def calculate_orbit_from_radii(
    periapsis: float,
    apoapsis: float,
    central_mass: float = M_SUN,
) -> KeplerOrbit:
    """
    Calculate orbital parameters from periapsis and apoapsis distances.

    Args:
        periapsis: Closest approach distance in meters
        apoapsis: Farthest distance in meters
        central_mass: Mass of the central body in kg

    Returns:
        KeplerOrbit with calculated parameters

    Raises:
        ValueError: If distances are invalid
    """
    if periapsis <= 0 or apoapsis <= 0:
        raise ValueError("Distances must be positive")
    if periapsis > apoapsis:
        raise ValueError("Periapsis must be less than or equal to apoapsis")

    # Calculate semi-major axis and eccentricity
    a = (periapsis + apoapsis) / 2
    e = (apoapsis - periapsis) / (apoapsis + periapsis)

    return KeplerOrbit(
        semi_major_axis=a,
        eccentricity=e,
        central_mass=central_mass,
    )


def calculate_orbit_from_state(
    radius: float,
    velocity: float,
    flight_path_angle: float = 0.0,
    central_mass: float = M_SUN,
) -> KeplerOrbit:
    """
    Calculate orbital parameters from position and velocity (state vector).

    Args:
        radius: Distance from central body in meters
        velocity: Orbital velocity in m/s
        flight_path_angle: Angle between velocity vector and local horizontal (radians)
        central_mass: Mass of the central body in kg

    Returns:
        KeplerOrbit with calculated parameters

    Raises:
        ValueError: If radius or velocity are not positive
    """
    if radius <= 0:
        raise ValueError("Radius must be positive")
    if velocity <= 0:
        raise ValueError("Velocity must be positive")

    mu = G * central_mass

    # Specific orbital energy (vis-viva)
    epsilon = velocity**2 / 2 - mu / radius

    # Semi-major axis
    a = -mu / (2 * epsilon)

    # Specific angular momentum
    h = radius * velocity * math.cos(flight_path_angle)

    # Eccentricity
    e_squared = 1 + (2 * epsilon * h**2) / (mu**2)
    e = math.sqrt(max(0, e_squared))  # Clamp to handle numerical errors

    return KeplerOrbit(
        semi_major_axis=a,
        eccentricity=e,
        central_mass=central_mass,
    )


def calculate_escape_velocity(radius: float, central_mass: float = M_SUN) -> float:
    """
    Calculate the escape velocity at a given distance from a body.

    Args:
        radius: Distance from the center of the body in meters
        central_mass: Mass of the body in kg

    Returns:
        Escape velocity in m/s

    Raises:
        ValueError: If radius is not positive
    """
    if radius <= 0:
        raise ValueError("Radius must be positive")

    return math.sqrt(2 * G * central_mass / radius)


def calculate_circular_velocity(radius: float, central_mass: float = M_SUN) -> float:
    """
    Calculate the circular orbital velocity at a given distance.

    Args:
        radius: Distance from the center of the body in meters
        central_mass: Mass of the body in kg

    Returns:
        Circular velocity in m/s

    Raises:
        ValueError: If radius is not positive
    """
    if radius <= 0:
        raise ValueError("Radius must be positive")

    return math.sqrt(G * central_mass / radius)


def calculate_orbital_elements(
    mass_ratio: Optional[float] = None,
    period_ratio: Optional[float] = None,
    reference_period: float = 365.25,
    reference_semi_major_axis: float = 1.0,
) -> dict:
    """
    Calculate orbital elements using Kepler's third law ratios.

    Useful for comparing exoplanet orbits to Earth's orbit.

    Args:
        mass_ratio: Ratio of star mass to Sun mass (M_star / M_sun)
        period_ratio: Ratio of orbital period to reference (P / P_ref)
        reference_period: Reference orbital period in days (default: Earth's year)
        reference_semi_major_axis: Reference semi-major axis in AU (default: 1 AU)

    Returns:
        Dictionary containing calculated orbital elements
    """
    result = {}

    if mass_ratio is not None and period_ratio is not None:
        # Using T² ∝ a³/M, we get: a = (M * T²)^(1/3)
        # For ratio form: a/a_ref = (M/M_ref * (T/T_ref)²)^(1/3)
        a_ratio = (mass_ratio * period_ratio**2) ** (1 / 3)
        result["semi_major_axis_au"] = reference_semi_major_axis * a_ratio
        result["semi_major_axis_m"] = result["semi_major_axis_au"] * AU

    if period_ratio is not None:
        result["period_days"] = reference_period * period_ratio
        result["period_years"] = result["period_days"] / 365.25

    return result


def generate_orbit_plot_code(
    orbit: KeplerOrbit,
    body_name: str = "Orbiting Body",
    central_body_name: str = "Central Body",
    title: Optional[str] = None,
    show_velocity_vectors: bool = False,
    num_points: int = 100,
) -> str:
    """
    Generate matplotlib code to visualize a Keplerian orbit.

    Args:
        orbit: KeplerOrbit object to visualize
        body_name: Display name for the orbiting body
        central_body_name: Display name for the central body
        title: Optional custom title for the plot
        show_velocity_vectors: Whether to show velocity vectors at key points
        num_points: Number of points to use for plotting the orbit

    Returns:
        String containing Python/matplotlib code to generate the plot
    """
    a_au = orbit.semi_major_axis / AU
    e = orbit.eccentricity
    orbit_type = orbit.orbit_type.value

    if title is None:
        title = f"Keplerian Orbit of {body_name}"

    # Determine plot limits
    if e < 1:
        limit = orbit.apoapsis / AU * 1.2
    else:
        limit = orbit.periapsis / AU * 3  # For hyperbolic, show a reasonable range

    code = f'''
# Keplerian Orbit Visualization
# Note: np, plt, and physics constants are pre-loaded by the plotter sandbox

# Orbital parameters
a = {a_au}  # Semi-major axis (AU)
e = {e}  # Eccentricity
orbit_type = "{orbit_type}"

# Create figure
fig, ax = plt.subplots(figsize=(10, 10))

# Draw the central body
ax.plot(0, 0, 'yo', markersize=20, label='{central_body_name}')

# Generate orbit points
'''

    if e < 1:
        code += f'''
# Elliptical orbit - full 360 degrees
theta = np.linspace(0, 2 * np.pi, {num_points})
r = a * (1 - e**2) / (1 + e * np.cos(theta))
x = r * np.cos(theta)
y = r * np.sin(theta)
ax.plot(x, y, 'b-', linewidth=2, label='{body_name} Orbit')
'''
    else:
        code += f'''
# Hyperbolic orbit - limited range
# Find the asymptotic angle
theta_max = np.arccos(-1/e) - 0.1  # Slightly less than asymptote
theta = np.linspace(-theta_max, theta_max, {num_points})
r = abs(a) * (e**2 - 1) / (1 + e * np.cos(theta))
x = r * np.cos(theta)
y = r * np.sin(theta)
ax.plot(x, y, 'b-', linewidth=2, label='{body_name} Orbit')
'''

    code += f'''
# Mark periapsis
periapsis_au = {orbit.periapsis / AU}
ax.plot(periapsis_au, 0, 'go', markersize=10, label='Periapsis', zorder=5)
ax.annotate('Periapsis', (periapsis_au, 0), textcoords="offset points",
            xytext=(10, 10), ha='left', fontsize=10)
'''

    if e < 1 and e > 0:
        code += f'''
# Mark apoapsis (for elliptical orbits)
apoapsis_au = {orbit.apoapsis / AU}
ax.plot(-apoapsis_au, 0, 'ro', markersize=10, label='Apoapsis', zorder=5)
ax.annotate('Apoapsis', (-apoapsis_au, 0), textcoords="offset points",
            xytext=(-10, 10), ha='right', fontsize=10)
'''

    if show_velocity_vectors and e < 1:
        v_peri = orbit.velocity_at_radius(orbit.periapsis) / 1000
        v_apo = orbit.velocity_at_radius(orbit.apoapsis) / 1000
        code += f'''
# Show velocity vectors (scaled for visibility)
v_periapsis = {v_peri}  # km/s
v_apoapsis = {v_apo}  # km/s
arrow_scale = {limit} * 0.1

# Velocity at periapsis (pointing up, perpendicular to radius)
ax.annotate('', xy=(periapsis_au, arrow_scale), xytext=(periapsis_au, 0),
            arrowprops=dict(arrowstyle='->', color='green', lw=2))
ax.text(periapsis_au + 0.05, arrow_scale/2, f'v={{v_periapsis:.1f}} km/s', fontsize=9, color='green')

# Velocity at apoapsis
ax.annotate('', xy=(-apoapsis_au, -arrow_scale), xytext=(-apoapsis_au, 0),
            arrowprops=dict(arrowstyle='->', color='red', lw=2))
ax.text(-apoapsis_au - 0.05, -arrow_scale/2, f'v={{v_apoapsis:.1f}} km/s', fontsize=9, color='red', ha='right')
'''

    code += f'''
# Formatting
limit = {limit}
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.set_aspect('equal')
ax.set_xlabel('Distance (AU)', fontsize=12)
ax.set_ylabel('Distance (AU)', fontsize=12)
ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)

# Add text box with orbital info
'''

    if e < 1:
        period_days = orbit.period_in_days()
        code += f'''
textstr = f'Semi-major axis: {{a:.3f}} AU\\nEccentricity: {{e:.4f}}\\nPeriod: {period_days:.1f} days'
'''
    else:
        code += '''
textstr = f'Semi-major axis: {a:.3f} AU\\nEccentricity: {e:.4f}\\nOrbit type: Hyperbolic'
'''

    code += '''
props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=props)

plt.tight_layout()
'''

    return code


def get_exoplanet_example(
    planet_name: str = "Kepler-442b",
) -> tuple[KeplerOrbit, str]:
    """
    Get an example orbit calculation for a known exoplanet.

    Args:
        planet_name: Name of the exoplanet (currently supports a few examples)

    Returns:
        Tuple of (KeplerOrbit, plot_code_string)

    Supported planets:
        - Kepler-442b: A super-Earth in the habitable zone
        - Proxima Centauri b: Closest known exoplanet
        - TRAPPIST-1e: One of the TRAPPIST-1 system planets
    """
    # Exoplanet data (approximate values)
    exoplanets = {
        "kepler-442b": {
            "period_days": 112.3,
            "eccentricity": 0.04,
            "star_mass": 0.61 * M_SUN,
            "display_name": "Kepler-442b",
        },
        "proxima centauri b": {
            "period_days": 11.2,
            "eccentricity": 0.11,
            "star_mass": 0.12 * M_SUN,
            "display_name": "Proxima Centauri b",
        },
        "trappist-1e": {
            "period_days": 6.1,
            "eccentricity": 0.005,
            "star_mass": 0.089 * M_SUN,
            "display_name": "TRAPPIST-1e",
        },
    }

    key = planet_name.lower()
    if key not in exoplanets:
        available = ", ".join(exoplanets.keys())
        raise ValueError(f"Unknown exoplanet: {planet_name}. Available: {available}")

    data = exoplanets[key]
    orbit = calculate_orbit_from_period(
        period_days=data["period_days"],
        eccentricity=data["eccentricity"],
        central_mass=data["star_mass"],
    )

    plot_code = generate_orbit_plot_code(
        orbit,
        body_name=data["display_name"],
        central_body_name="Host Star",
        show_velocity_vectors=True,
    )

    return orbit, plot_code


# Example usage when run directly
if __name__ == "__main__":
    print("=" * 60)
    print("KEPLER ORBIT CALCULATOR")
    print("=" * 60)
    print()

    # Example 1: Earth's orbit
    print("Example 1: Earth's Orbit")
    print("-" * 40)
    earth_orbit = calculate_orbit_from_period(365.25, eccentricity=0.0167)
    print(earth_orbit)
    print()

    # Example 2: Halley's Comet
    print("Example 2: Halley's Comet")
    print("-" * 40)
    halley = calculate_orbit_from_radii(
        periapsis=0.586 * AU,
        apoapsis=35.1 * AU,
    )
    print(halley)
    print()

    # Example 3: Exoplanet
    print("Example 3: Kepler-442b (Exoplanet in Habitable Zone)")
    print("-" * 40)
    kepler_442b, _ = get_exoplanet_example("Kepler-442b")
    print(kepler_442b)
    print()

    # Example 4: Velocities
    print("Example 4: Key Velocities at Earth's Distance")
    print("-" * 40)
    r_earth = 1.0 * AU
    v_circular = calculate_circular_velocity(r_earth)
    v_escape = calculate_escape_velocity(r_earth)
    print("Distance from Sun: 1.0 AU")
    print(f"Circular velocity: {v_circular / 1000:.2f} km/s")
    print(f"Escape velocity: {v_escape / 1000:.2f} km/s")
