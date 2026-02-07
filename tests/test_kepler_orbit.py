"""Tests for the Kepler orbit calculator."""

import math
import shutil
import tempfile
import unittest

from examples.kepler_orbit import (
    AU,
    M_EARTH,
    M_SUN,
    SECONDS_PER_DAY,
    SECONDS_PER_YEAR,
    G,
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


class TestConstants(unittest.TestCase):
    """Tests for physical constants."""

    def test_gravitational_constant(self):
        """Test gravitational constant value."""
        assert G == 6.67430e-11

    def test_solar_mass(self):
        """Test solar mass value."""
        assert M_SUN == 1.989e30

    def test_earth_mass(self):
        """Test Earth mass value."""
        assert M_EARTH == 5.972e24

    def test_astronomical_unit(self):
        """Test astronomical unit value."""
        assert AU == 1.496e11

    def test_seconds_per_day(self):
        """Test seconds per day value."""
        assert SECONDS_PER_DAY == 86400

    def test_seconds_per_year(self):
        """Test seconds per year value."""
        assert SECONDS_PER_YEAR == 365.25 * 86400


class TestOrbitType(unittest.TestCase):
    """Tests for OrbitType enum."""

    def test_orbit_types_exist(self):
        """Test that all orbit types exist."""
        assert OrbitType.CIRCULAR.value == "circular"
        assert OrbitType.ELLIPTICAL.value == "elliptical"
        assert OrbitType.PARABOLIC.value == "parabolic"
        assert OrbitType.HYPERBOLIC.value == "hyperbolic"


class TestKeplerOrbit(unittest.TestCase):
    """Tests for KeplerOrbit dataclass."""

    def test_circular_orbit(self):
        """Test circular orbit creation."""
        orbit = KeplerOrbit(
            semi_major_axis=1.0 * AU,
            eccentricity=0.0,
        )
        assert orbit.orbit_type == OrbitType.CIRCULAR
        assert orbit.semi_minor_axis == orbit.semi_major_axis
        assert orbit.periapsis == orbit.semi_major_axis
        assert orbit.apoapsis == orbit.semi_major_axis

    def test_elliptical_orbit(self):
        """Test elliptical orbit creation."""
        orbit = KeplerOrbit(
            semi_major_axis=1.0 * AU,
            eccentricity=0.5,
        )
        assert orbit.orbit_type == OrbitType.ELLIPTICAL
        assert orbit.periapsis == 0.5 * AU
        assert orbit.apoapsis == 1.5 * AU

    def test_hyperbolic_orbit(self):
        """Test hyperbolic orbit creation."""
        orbit = KeplerOrbit(
            semi_major_axis=-1.0 * AU,  # Negative for hyperbolic
            eccentricity=1.5,
        )
        assert orbit.orbit_type == OrbitType.HYPERBOLIC
        assert orbit.apoapsis == float("inf")
        assert orbit.orbital_period == float("inf")

    def test_semi_minor_axis_calculation(self):
        """Test semi-minor axis is calculated correctly."""
        a = 2.0 * AU
        e = 0.5
        orbit = KeplerOrbit(semi_major_axis=a, eccentricity=e)
        expected_b = a * math.sqrt(1 - e**2)
        assert abs(orbit.semi_minor_axis - expected_b) < 1e-6

    def test_orbital_period_calculation(self):
        """Test orbital period is calculated using Kepler's third law."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.0)
        # Earth's period should be about 1 year
        period_years = orbit.period_in_years()
        assert abs(period_years - 1.0) < 0.01

    def test_mean_motion_calculation(self):
        """Test mean motion is calculated correctly."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.0)
        expected_n = 2 * math.pi / orbit.orbital_period
        assert abs(orbit.mean_motion - expected_n) < 1e-15

    def test_specific_orbital_energy(self):
        """Test specific orbital energy calculation."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.0)
        mu = G * M_SUN
        expected_energy = -mu / (2 * 1.0 * AU)
        assert abs(orbit.specific_orbital_energy - expected_energy) < 1e6

    def test_radius_at_true_anomaly(self):
        """Test radius calculation at various true anomalies."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.5)
        # At periapsis (nu = 0)
        r_peri = orbit.radius_at_true_anomaly(0)
        assert abs(r_peri - orbit.periapsis) < 1e6
        # At apoapsis (nu = pi)
        r_apo = orbit.radius_at_true_anomaly(math.pi)
        assert abs(r_apo - orbit.apoapsis) < 1e6

    def test_velocity_at_radius(self):
        """Test velocity calculation using vis-viva."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.0)
        v = orbit.velocity_at_radius(1.0 * AU)
        # Circular velocity at 1 AU should be about 29.78 km/s
        v_km = v / 1000
        assert abs(v_km - 29.78) < 0.5

    def test_velocity_at_true_anomaly(self):
        """Test velocity at true anomaly."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.5)
        v_peri = orbit.velocity_at_true_anomaly(0)
        v_apo = orbit.velocity_at_true_anomaly(math.pi)
        # Velocity at periapsis should be greater than at apoapsis
        assert v_peri > v_apo

    def test_position_at_true_anomaly(self):
        """Test position calculation."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.0)
        x, y = orbit.position_at_true_anomaly(0)
        assert abs(x - 1.0 * AU) < 1e6
        assert abs(y) < 1e6

    def test_period_in_days(self):
        """Test period conversion to days."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.0)
        days = orbit.period_in_days()
        assert abs(days - 365.25) < 1

    def test_period_in_years(self):
        """Test period conversion to years."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.0)
        years = orbit.period_in_years()
        assert abs(years - 1.0) < 0.01

    def test_str_representation(self):
        """Test string representation."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.5)
        str_rep = str(orbit)
        assert "Keplerian Orbit" in str_rep
        assert "Elliptical" in str_rep
        assert "Semi-major axis" in str_rep
        assert "Eccentricity" in str_rep

    def test_str_representation_hyperbolic(self):
        """Test string representation for hyperbolic orbit."""
        orbit = KeplerOrbit(semi_major_axis=-1.0 * AU, eccentricity=1.5)
        str_rep = str(orbit)
        assert "Hyperbolic" in str_rep
        assert "∞" in str_rep or "unbound" in str_rep


class TestCalculateOrbitFromPeriod(unittest.TestCase):
    """Tests for calculate_orbit_from_period function."""

    def test_earth_orbit(self):
        """Test calculating Earth's orbit from period."""
        orbit = calculate_orbit_from_period(365.25)
        # Semi-major axis should be about 1 AU
        a_au = orbit.semi_major_axis / AU
        assert abs(a_au - 1.0) < 0.01

    def test_mercury_orbit(self):
        """Test calculating Mercury's orbit from period."""
        # Mercury's period is about 88 days
        orbit = calculate_orbit_from_period(88)
        a_au = orbit.semi_major_axis / AU
        # Mercury is at about 0.387 AU
        assert abs(a_au - 0.387) < 0.02

    def test_with_eccentricity(self):
        """Test orbit calculation with non-zero eccentricity."""
        orbit = calculate_orbit_from_period(365.25, eccentricity=0.5)
        assert orbit.eccentricity == 0.5
        assert orbit.periapsis < orbit.semi_major_axis

    def test_with_custom_central_mass(self):
        """Test orbit with custom central mass."""
        # Use Earth mass for satellite orbit
        orbit = calculate_orbit_from_period(
            1.0,  # 1 day period
            eccentricity=0.0,
            central_mass=M_EARTH,
        )
        # Should be roughly geostationary-ish orbit
        assert orbit.semi_major_axis > 0

    def test_raises_error_for_negative_period(self):
        """Test error for negative period."""
        with self.assertRaises(ValueError) as context:
            calculate_orbit_from_period(-365)
        assert "positive" in str(context.exception).lower()

    def test_raises_error_for_zero_period(self):
        """Test error for zero period."""
        with self.assertRaises(ValueError):
            calculate_orbit_from_period(0)

    def test_raises_error_for_negative_eccentricity(self):
        """Test error for negative eccentricity."""
        with self.assertRaises(ValueError) as context:
            calculate_orbit_from_period(365, eccentricity=-0.5)
        assert "eccentricity" in str(context.exception).lower()

    def test_raises_error_for_unbound_eccentricity(self):
        """Test error for e >= 1."""
        with self.assertRaises(ValueError):
            calculate_orbit_from_period(365, eccentricity=1.0)
        with self.assertRaises(ValueError):
            calculate_orbit_from_period(365, eccentricity=1.5)


class TestCalculateOrbitFromRadii(unittest.TestCase):
    """Tests for calculate_orbit_from_radii function."""

    def test_circular_orbit(self):
        """Test circular orbit from equal radii."""
        orbit = calculate_orbit_from_radii(1.0 * AU, 1.0 * AU)
        assert orbit.eccentricity == 0.0
        assert orbit.periapsis == orbit.apoapsis

    def test_elliptical_orbit(self):
        """Test elliptical orbit from different radii."""
        periapsis = 0.5 * AU
        apoapsis = 1.5 * AU
        orbit = calculate_orbit_from_radii(periapsis, apoapsis)
        assert abs(orbit.semi_major_axis - 1.0 * AU) < 1e6
        assert abs(orbit.eccentricity - 0.5) < 0.01

    def test_halley_comet(self):
        """Test Halley's Comet orbit (highly eccentric)."""
        # Halley: periapsis ~0.586 AU, apoapsis ~35.1 AU
        orbit = calculate_orbit_from_radii(0.586 * AU, 35.1 * AU)
        # Semi-major axis should be about 17.8 AU
        a_au = orbit.semi_major_axis / AU
        assert abs(a_au - 17.8) < 0.5
        # Eccentricity should be about 0.967
        assert abs(orbit.eccentricity - 0.967) < 0.01

    def test_raises_error_for_negative_periapsis(self):
        """Test error for negative periapsis."""
        with self.assertRaises(ValueError):
            calculate_orbit_from_radii(-1.0 * AU, 2.0 * AU)

    def test_raises_error_for_negative_apoapsis(self):
        """Test error for negative apoapsis."""
        with self.assertRaises(ValueError):
            calculate_orbit_from_radii(1.0 * AU, -2.0 * AU)

    def test_raises_error_for_periapsis_greater_than_apoapsis(self):
        """Test error when periapsis > apoapsis."""
        with self.assertRaises(ValueError) as context:
            calculate_orbit_from_radii(2.0 * AU, 1.0 * AU)
        assert "periapsis" in str(context.exception).lower()


class TestCalculateOrbitFromState(unittest.TestCase):
    """Tests for calculate_orbit_from_state function."""

    def test_circular_orbit(self):
        """Test circular orbit from state vector."""
        r = 1.0 * AU
        v = math.sqrt(G * M_SUN / r)  # Circular velocity
        orbit = calculate_orbit_from_state(r, v, flight_path_angle=0)
        # Should be nearly circular
        assert orbit.eccentricity < 0.01

    def test_elliptical_orbit(self):
        """Test elliptical orbit from state vector."""
        r = 1.0 * AU
        v = 35000  # Higher than circular velocity
        orbit = calculate_orbit_from_state(r, v, flight_path_angle=0)
        assert orbit.eccentricity > 0
        assert orbit.eccentricity < 1

    def test_escape_velocity(self):
        """Test orbit at escape velocity."""
        r = 1.0 * AU
        v = math.sqrt(2 * G * M_SUN / r)  # Escape velocity
        orbit = calculate_orbit_from_state(r, v, flight_path_angle=0)
        # Should be parabolic (e = 1) or nearly so
        assert abs(orbit.eccentricity - 1.0) < 0.01

    def test_raises_error_for_negative_radius(self):
        """Test error for negative radius."""
        with self.assertRaises(ValueError):
            calculate_orbit_from_state(-1.0 * AU, 30000)

    def test_raises_error_for_negative_velocity(self):
        """Test error for negative velocity."""
        with self.assertRaises(ValueError):
            calculate_orbit_from_state(1.0 * AU, -30000)


class TestCalculateEscapeVelocity(unittest.TestCase):
    """Tests for calculate_escape_velocity function."""

    def test_earth_surface_escape_velocity(self):
        """Test escape velocity from Earth's surface."""
        r_earth = 6.371e6  # Earth radius in meters
        v_esc = calculate_escape_velocity(r_earth, M_EARTH)
        # Should be about 11.2 km/s
        v_km = v_esc / 1000
        assert abs(v_km - 11.2) < 0.2

    def test_sun_at_1_au(self):
        """Test escape velocity from Sun at 1 AU."""
        v_esc = calculate_escape_velocity(1.0 * AU, M_SUN)
        # Should be about 42.1 km/s
        v_km = v_esc / 1000
        assert abs(v_km - 42.1) < 0.5

    def test_raises_error_for_negative_radius(self):
        """Test error for negative radius."""
        with self.assertRaises(ValueError):
            calculate_escape_velocity(-1.0 * AU)

    def test_raises_error_for_zero_radius(self):
        """Test error for zero radius."""
        with self.assertRaises(ValueError):
            calculate_escape_velocity(0)


class TestCalculateCircularVelocity(unittest.TestCase):
    """Tests for calculate_circular_velocity function."""

    def test_earth_orbital_velocity(self):
        """Test Earth's circular orbital velocity."""
        v = calculate_circular_velocity(1.0 * AU, M_SUN)
        # Should be about 29.78 km/s
        v_km = v / 1000
        assert abs(v_km - 29.78) < 0.5

    def test_escape_velocity_relation(self):
        """Test that v_escape = sqrt(2) * v_circular."""
        r = 1.0 * AU
        v_circ = calculate_circular_velocity(r)
        v_esc = calculate_escape_velocity(r)
        ratio = v_esc / v_circ
        assert abs(ratio - math.sqrt(2)) < 0.01

    def test_raises_error_for_negative_radius(self):
        """Test error for negative radius."""
        with self.assertRaises(ValueError):
            calculate_circular_velocity(-1.0 * AU)


class TestCalculateOrbitalElements(unittest.TestCase):
    """Tests for calculate_orbital_elements function."""

    def test_with_mass_and_period_ratio(self):
        """Test calculation with mass and period ratios."""
        result = calculate_orbital_elements(mass_ratio=1.0, period_ratio=1.0)
        assert "semi_major_axis_au" in result
        assert abs(result["semi_major_axis_au"] - 1.0) < 0.01

    def test_period_only(self):
        """Test calculation with period ratio only."""
        result = calculate_orbital_elements(period_ratio=2.0)
        assert "period_days" in result
        assert abs(result["period_days"] - 730.5) < 0.5

    def test_empty_result(self):
        """Test that empty input returns empty result."""
        result = calculate_orbital_elements()
        assert "semi_major_axis_au" not in result


class TestGenerateOrbitPlotCode(unittest.TestCase):
    """Tests for generate_orbit_plot_code function."""

    def test_returns_string(self):
        """Test that function returns a string."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.5)
        code = generate_orbit_plot_code(orbit)
        assert isinstance(code, str)

    def test_contains_matplotlib_commands(self):
        """Test that code contains matplotlib commands."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.5)
        code = generate_orbit_plot_code(orbit)
        assert "plt." in code
        assert "np." in code

    def test_custom_title(self):
        """Test custom title is included."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.5)
        code = generate_orbit_plot_code(orbit, title="My Custom Title")
        assert "My Custom Title" in code

    def test_body_names_in_code(self):
        """Test body names appear in code."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.5)
        code = generate_orbit_plot_code(
            orbit, body_name="Mars", central_body_name="Sun"
        )
        assert "Mars" in code
        assert "Sun" in code

    def test_velocity_vectors_option(self):
        """Test velocity vectors option."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.5)
        code = generate_orbit_plot_code(orbit, show_velocity_vectors=True)
        assert "km/s" in code

    def test_code_is_syntactically_valid(self):
        """Test that generated code compiles without syntax errors."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.5)
        code = generate_orbit_plot_code(orbit)
        compile(code, "<test>", "exec")

    def test_hyperbolic_orbit_code(self):
        """Test code generation for hyperbolic orbit."""
        orbit = KeplerOrbit(semi_major_axis=-1.0 * AU, eccentricity=1.5)
        code = generate_orbit_plot_code(orbit)
        assert "Hyperbolic" in code or "hyperbolic" in code
        compile(code, "<test>", "exec")


class TestGenerateOrbitPlotCodeExecution(unittest.TestCase):
    """Tests for executing the generated orbit plot code."""

    def setUp(self):
        """Create temporary directory for test outputs."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove temporary directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_elliptical_orbit_plot(self):
        """Test that elliptical orbit code creates a valid plot."""
        from kosmo.tools.plotter import create_plot

        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.5)
        code = generate_orbit_plot_code(orbit)
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result

    def test_circular_orbit_plot(self):
        """Test that circular orbit code creates a valid plot."""
        from kosmo.tools.plotter import create_plot

        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.0)
        code = generate_orbit_plot_code(orbit)
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result


class TestGetExoplanetExample(unittest.TestCase):
    """Tests for get_exoplanet_example function."""

    def test_returns_tuple(self):
        """Test that function returns a tuple."""
        result = get_exoplanet_example()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_first_element_is_orbit(self):
        """Test first element is KeplerOrbit."""
        orbit, code = get_exoplanet_example()
        assert isinstance(orbit, KeplerOrbit)

    def test_second_element_is_string(self):
        """Test second element is plot code string."""
        orbit, code = get_exoplanet_example()
        assert isinstance(code, str)

    def test_kepler_442b(self):
        """Test Kepler-442b example."""
        orbit, code = get_exoplanet_example("Kepler-442b")
        # Period should be about 112 days
        assert abs(orbit.period_in_days() - 112.3) < 5
        assert "Kepler-442b" in code

    def test_proxima_centauri_b(self):
        """Test Proxima Centauri b example."""
        orbit, code = get_exoplanet_example("Proxima Centauri b")
        # Period should be about 11 days
        assert abs(orbit.period_in_days() - 11.2) < 1
        assert "Proxima" in code

    def test_trappist_1e(self):
        """Test TRAPPIST-1e example."""
        orbit, code = get_exoplanet_example("TRAPPIST-1e")
        # Period should be about 6 days
        assert abs(orbit.period_in_days() - 6.1) < 0.5
        assert "TRAPPIST" in code

    def test_case_insensitive(self):
        """Test planet names are case-insensitive."""
        orbit1, _ = get_exoplanet_example("kepler-442b")
        orbit2, _ = get_exoplanet_example("KEPLER-442B")
        assert abs(orbit1.semi_major_axis - orbit2.semi_major_axis) < 1

    def test_invalid_planet_raises_error(self):
        """Test error for unknown exoplanet."""
        with self.assertRaises(ValueError) as context:
            get_exoplanet_example("Unknown Planet")
        assert "Unknown exoplanet" in str(context.exception)


class TestPhysicsAccuracy(unittest.TestCase):
    """Tests to verify physics calculations are accurate."""

    def test_keplers_third_law(self):
        """Test Kepler's third law: T² ∝ a³."""
        # Earth's orbit
        orbit = calculate_orbit_from_period(365.25)
        a = orbit.semi_major_axis
        T = orbit.orbital_period
        mu = G * M_SUN
        # T² = 4π²a³/μ
        T_calculated = 2 * math.pi * math.sqrt(a**3 / mu)
        assert abs(T - T_calculated) / T < 0.001

    def test_vis_viva_equation(self):
        """Test vis-viva equation: v² = μ(2/r - 1/a)."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.5)
        r = orbit.periapsis
        v = orbit.velocity_at_radius(r)
        mu = G * M_SUN
        v_expected = math.sqrt(mu * (2 / r - 1 / orbit.semi_major_axis))
        assert abs(v - v_expected) / v < 0.001

    def test_angular_momentum_conservation(self):
        """Test that h = r * v * cos(gamma) is constant."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.5)
        # At periapsis and apoapsis, velocity is perpendicular to radius
        h_peri = orbit.periapsis * orbit.velocity_at_radius(orbit.periapsis)
        h_apo = orbit.apoapsis * orbit.velocity_at_radius(orbit.apoapsis)
        # Should be equal (angular momentum conservation)
        assert abs(h_peri - h_apo) / h_peri < 0.001

    def test_energy_conservation(self):
        """Test that specific orbital energy is constant."""
        orbit = KeplerOrbit(semi_major_axis=1.0 * AU, eccentricity=0.5)
        mu = G * M_SUN
        # Calculate energy at periapsis
        r_peri = orbit.periapsis
        v_peri = orbit.velocity_at_radius(r_peri)
        epsilon_peri = v_peri**2 / 2 - mu / r_peri
        # Calculate energy at apoapsis
        r_apo = orbit.apoapsis
        v_apo = orbit.velocity_at_radius(r_apo)
        epsilon_apo = v_apo**2 / 2 - mu / r_apo
        # Should be equal (energy conservation)
        assert abs(epsilon_peri - epsilon_apo) / abs(epsilon_peri) < 0.001

    def test_mars_orbital_period(self):
        """Test Mars orbital period calculation."""
        # Mars is at about 1.524 AU
        orbit = KeplerOrbit(semi_major_axis=1.524 * AU, eccentricity=0.093)
        # Mars period is about 687 days
        period_days = orbit.period_in_days()
        assert abs(period_days - 687) < 10

    def test_jupiter_orbital_period(self):
        """Test Jupiter orbital period calculation."""
        # Jupiter is at about 5.2 AU
        orbit = KeplerOrbit(semi_major_axis=5.2 * AU, eccentricity=0.048)
        # Jupiter period is about 4333 days (11.86 years)
        period_years = orbit.period_in_years()
        assert abs(period_years - 11.86) < 0.5


if __name__ == "__main__":
    unittest.main()
