"""Tests for the Hohmann transfer orbit simulation."""

import math
import os
import shutil
import tempfile
import unittest

from examples.hohmann_transfer import (
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


class TestConstants(unittest.TestCase):
    """Tests for physical constants."""

    def test_gravitational_constant(self):
        """Test gravitational constant value."""
        assert G == 6.67430e-11

    def test_solar_mass(self):
        """Test solar mass value."""
        assert M_SUN == 1.989e30

    def test_astronomical_unit(self):
        """Test astronomical unit value."""
        assert AU == 1.496e11

    def test_planets_dict_contains_expected_planets(self):
        """Test that PLANETS dict has expected entries."""
        expected = ["mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune"]
        for planet in expected:
            assert planet in PLANETS

    def test_earth_at_1_au(self):
        """Test that Earth is at 1 AU."""
        assert PLANETS["earth"] == 1.0

    def test_planets_in_order(self):
        """Test that planets are in correct order from the Sun."""
        distances = [PLANETS[p] for p in ["mercury", "venus", "earth", "mars", "jupiter"]]
        assert distances == sorted(distances)


class TestHohmannTransferResult(unittest.TestCase):
    """Tests for HohmannTransferResult dataclass."""

    def test_result_has_all_fields(self):
        """Test that result has all required fields."""
        result = HohmannTransferResult(
            r1=1.0 * AU,
            r2=1.524 * AU,
            semi_major_axis=1.262 * AU,
            eccentricity=0.2076,
            transfer_time=2.24e7,
            v1_circular=29780,
            v2_circular=24130,
            v_periapsis=32730,
            v_apoapsis=21480,
            delta_v1=2950,
            delta_v2=2650,
            total_delta_v=5600,
        )
        assert hasattr(result, "r1")
        assert hasattr(result, "r2")
        assert hasattr(result, "semi_major_axis")
        assert hasattr(result, "eccentricity")
        assert hasattr(result, "transfer_time")
        assert hasattr(result, "delta_v1")
        assert hasattr(result, "delta_v2")
        assert hasattr(result, "total_delta_v")

    def test_str_representation(self):
        """Test string representation of result."""
        result = HohmannTransferResult(
            r1=1.0 * AU,
            r2=1.524 * AU,
            semi_major_axis=1.262 * AU,
            eccentricity=0.2076,
            transfer_time=2.24e7,
            v1_circular=29780,
            v2_circular=24130,
            v_periapsis=32730,
            v_apoapsis=21480,
            delta_v1=2950,
            delta_v2=2650,
            total_delta_v=5600,
        )
        str_rep = str(result)
        assert "Hohmann Transfer Orbit Results" in str_rep
        assert "Inner orbit radius" in str_rep
        assert "Delta-v Requirements" in str_rep
        assert "km/s" in str_rep


class TestCalculateHohmannTransfer(unittest.TestCase):
    """Tests for calculate_hohmann_transfer function."""

    def test_earth_mars_transfer_time(self):
        """Test Earth to Mars transfer time is approximately correct."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        # Transfer time should be about 259 days (half of ellipse period)
        days = result.transfer_time / 86400
        assert 250 < days < 270

    def test_earth_mars_delta_v(self):
        """Test Earth to Mars total delta-v is reasonable."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        # Total delta-v should be about 5.6 km/s
        delta_v_km = result.total_delta_v / 1000
        assert 5.0 < delta_v_km < 6.5

    def test_semi_major_axis_is_average(self):
        """Test that transfer semi-major axis is average of two radii."""
        r1 = 1.0 * AU
        r2 = 2.0 * AU
        result = calculate_hohmann_transfer(r1, r2)
        expected_a = (r1 + r2) / 2
        assert abs(result.semi_major_axis - expected_a) < 1e-6

    def test_eccentricity_calculation(self):
        """Test eccentricity calculation is correct."""
        r1 = 1.0 * AU
        r2 = 2.0 * AU
        result = calculate_hohmann_transfer(r1, r2)
        expected_e = (r2 - r1) / (r2 + r1)
        assert abs(result.eccentricity - expected_e) < 1e-6

    def test_velocities_are_positive(self):
        """Test all velocities are positive."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        assert result.v1_circular > 0
        assert result.v2_circular > 0
        assert result.v_periapsis > 0
        assert result.v_apoapsis > 0

    def test_periapsis_velocity_greater_than_circular(self):
        """Test periapsis velocity is greater than circular (need to speed up)."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        assert result.v_periapsis > result.v1_circular

    def test_apoapsis_velocity_less_than_circular(self):
        """Test apoapsis velocity is less than circular at target (need to speed up)."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        assert result.v_apoapsis < result.v2_circular

    def test_delta_v1_is_positive_for_outward_transfer(self):
        """Test first delta-v is positive (accelerate to raise apoapsis)."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        assert result.delta_v1 > 0

    def test_delta_v2_is_positive_for_outward_transfer(self):
        """Test second delta-v is positive (accelerate to circularize)."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        assert result.delta_v2 > 0

    def test_total_delta_v_is_sum(self):
        """Test total delta-v is sum of two burns."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        assert abs(result.total_delta_v - (result.delta_v1 + result.delta_v2)) < 1e-6

    def test_raises_error_if_r1_greater_than_r2(self):
        """Test ValueError is raised if inner orbit is larger."""
        with self.assertRaises(ValueError) as context:
            calculate_hohmann_transfer(2.0 * AU, 1.0 * AU)
        assert "less than" in str(context.exception)

    def test_raises_error_if_r1_equals_r2(self):
        """Test ValueError is raised if orbits are equal."""
        with self.assertRaises(ValueError):
            calculate_hohmann_transfer(1.0 * AU, 1.0 * AU)

    def test_raises_error_for_negative_radius(self):
        """Test ValueError is raised for negative radius."""
        with self.assertRaises(ValueError):
            calculate_hohmann_transfer(-1.0 * AU, 1.0 * AU)

    def test_raises_error_for_zero_radius(self):
        """Test ValueError is raised for zero radius."""
        with self.assertRaises(ValueError):
            calculate_hohmann_transfer(0, 1.0 * AU)

    def test_custom_gravitational_parameter(self):
        """Test using custom gravitational parameter (e.g., for Earth orbit)."""
        # Earth's gravitational parameter
        mu_earth = G * 5.972e24
        # Low Earth orbit to geostationary orbit
        r_leo = 6.371e6 + 400e3  # 400 km altitude
        r_geo = 42164e3  # Geostationary orbit radius
        result = calculate_hohmann_transfer(r_leo, r_geo, mu=mu_earth)
        # Transfer time should be about 5-6 hours
        hours = result.transfer_time / 3600
        assert 5 < hours < 6

    def test_transfer_to_jupiter(self):
        """Test longer transfer to outer planet."""
        result = calculate_hohmann_transfer(1.0 * AU, PLANETS["jupiter"] * AU)
        # Transfer to Jupiter should take about 2.7 years
        years = result.transfer_time / (86400 * 365.25)
        assert 2.5 < years < 3.0


class TestCalculatePlanetaryTransfer(unittest.TestCase):
    """Tests for calculate_planetary_transfer function."""

    def test_earth_to_mars(self):
        """Test Earth to Mars transfer."""
        result = calculate_planetary_transfer("earth", "mars")
        assert result.r1 == PLANETS["earth"] * AU
        assert result.r2 == PLANETS["mars"] * AU

    def test_case_insensitive(self):
        """Test planet names are case-insensitive."""
        result1 = calculate_planetary_transfer("Earth", "Mars")
        result2 = calculate_planetary_transfer("EARTH", "MARS")
        result3 = calculate_planetary_transfer("earth", "mars")
        assert result1.total_delta_v == result2.total_delta_v
        assert result2.total_delta_v == result3.total_delta_v

    def test_inward_transfer_swaps_radii(self):
        """Test that inward transfers swap radii correctly."""
        result = calculate_planetary_transfer("mars", "earth")
        # Should swap to have Earth (1 AU) as r1 and Mars (1.524 AU) as r2
        assert result.r1 == PLANETS["earth"] * AU
        assert result.r2 == PLANETS["mars"] * AU

    def test_invalid_origin_planet(self):
        """Test error for invalid origin planet."""
        with self.assertRaises(ValueError) as context:
            calculate_planetary_transfer("pluto", "mars")
        assert "Unknown planet" in str(context.exception)
        assert "pluto" in str(context.exception).lower()

    def test_invalid_destination_planet(self):
        """Test error for invalid destination planet."""
        with self.assertRaises(ValueError) as context:
            calculate_planetary_transfer("earth", "pluto")
        assert "Unknown planet" in str(context.exception)
        assert "pluto" in str(context.exception).lower()

    def test_earth_to_venus(self):
        """Test inward transfer to Venus."""
        result = calculate_planetary_transfer("earth", "venus")
        assert result.r1 == PLANETS["venus"] * AU
        assert result.r2 == PLANETS["earth"] * AU


class TestGenerateTransferPlotCode(unittest.TestCase):
    """Tests for generate_transfer_plot_code function."""

    def test_returns_string(self):
        """Test that function returns a string."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        code = generate_transfer_plot_code(result)
        assert isinstance(code, str)

    def test_contains_matplotlib_commands(self):
        """Test that code contains matplotlib commands."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        code = generate_transfer_plot_code(result)
        assert "plt." in code
        assert "np." in code

    def test_contains_orbital_parameters(self):
        """Test that code uses correct orbital parameters."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        code = generate_transfer_plot_code(result)
        # Check that radii are in the code (as AU values)
        assert "1.0" in code or "1.000" in code
        assert "1.524" in code or "1.52" in code

    def test_custom_title(self):
        """Test custom title is included."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        code = generate_transfer_plot_code(result, title="My Custom Title")
        assert "My Custom Title" in code

    def test_planet_names_in_legend(self):
        """Test planet names appear in code."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        code = generate_transfer_plot_code(result, "Earth", "Mars")
        assert "Earth" in code
        assert "Mars" in code

    def test_code_is_syntactically_valid(self):
        """Test that generated code compiles without syntax errors."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        code = generate_transfer_plot_code(result)
        # This should not raise a SyntaxError
        compile(code, "<test>", "exec")


class TestGenerateTransferPlotCodeExecution(unittest.TestCase):
    """Tests for actually executing the generated plot code."""

    def setUp(self):
        """Create a temporary directory for test outputs."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_code_creates_valid_plot(self):
        """Test that generated code creates a valid plot."""
        from kosmo.tools.plotter import create_plot

        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        code = generate_transfer_plot_code(result, "Earth", "Mars")
        plot_result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in plot_result

        # Verify file was created
        files = os.listdir(self.test_dir)
        assert len(files) == 1
        assert files[0].endswith(".png")


class TestGetEarthMarsExample(unittest.TestCase):
    """Tests for get_earth_mars_example function."""

    def test_returns_tuple(self):
        """Test that function returns a tuple."""
        result = get_earth_mars_example()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_first_element_is_result(self):
        """Test first element is HohmannTransferResult."""
        result, code = get_earth_mars_example()
        assert isinstance(result, HohmannTransferResult)

    def test_second_element_is_string(self):
        """Test second element is plot code string."""
        result, code = get_earth_mars_example()
        assert isinstance(code, str)

    def test_result_is_earth_mars_transfer(self):
        """Test that result represents Earth-Mars transfer."""
        result, code = get_earth_mars_example()
        assert abs(result.r1 - PLANETS["earth"] * AU) < 1e6
        assert abs(result.r2 - PLANETS["mars"] * AU) < 1e6

    def test_code_mentions_earth_and_mars(self):
        """Test that code mentions Earth and Mars."""
        result, code = get_earth_mars_example()
        assert "Earth" in code
        assert "Mars" in code


class TestPhysicsAccuracy(unittest.TestCase):
    """Tests to verify physics calculations are accurate against known values."""

    def test_earth_orbital_velocity(self):
        """Test Earth's orbital velocity calculation."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        # Earth's orbital velocity is about 29.78 km/s
        v_earth_km = result.v1_circular / 1000
        assert abs(v_earth_km - 29.78) < 0.5

    def test_mars_orbital_velocity(self):
        """Test Mars' orbital velocity calculation."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        # Mars' orbital velocity is about 24.1 km/s
        v_mars_km = result.v2_circular / 1000
        assert abs(v_mars_km - 24.1) < 0.5

    def test_keplers_third_law(self):
        """Test that transfer orbit obeys Kepler's third law."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        # T² ∝ a³
        # Period = 2 * transfer_time (full ellipse)
        period = 2 * result.transfer_time
        a = result.semi_major_axis
        mu = G * M_SUN
        # Kepler's third law: T = 2π√(a³/μ)
        expected_period = 2 * math.pi * math.sqrt(a**3 / mu)
        assert abs(period - expected_period) / expected_period < 0.001

    def test_vis_viva_at_periapsis(self):
        """Test vis-viva equation at periapsis."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        # v² = μ(2/r - 1/a)
        mu = G * M_SUN
        r = result.r1
        a = result.semi_major_axis
        expected_v = math.sqrt(mu * (2 / r - 1 / a))
        assert abs(result.v_periapsis - expected_v) / expected_v < 0.001

    def test_vis_viva_at_apoapsis(self):
        """Test vis-viva equation at apoapsis."""
        result = calculate_hohmann_transfer(1.0 * AU, 1.524 * AU)
        # v² = μ(2/r - 1/a)
        mu = G * M_SUN
        r = result.r2
        a = result.semi_major_axis
        expected_v = math.sqrt(mu * (2 / r - 1 / a))
        assert abs(result.v_apoapsis - expected_v) / expected_v < 0.001


if __name__ == "__main__":
    unittest.main()
