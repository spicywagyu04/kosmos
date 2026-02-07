"""Tests for the plotting tool."""

import os
import shutil
import tempfile
import unittest

from kosmo.tools.plotter import create_plot


class TestCreatePlotBasic(unittest.TestCase):
    """Basic tests for create_plot function."""

    def setUp(self):
        """Create a temporary directory for test outputs."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_simple_line_plot(self):
        """Test creating a simple line plot."""
        code = """
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.title('Sine Wave')
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result
        assert self.test_dir in result

        # Verify file was created
        files = os.listdir(self.test_dir)
        assert len(files) == 1
        assert files[0].startswith("plot_")
        assert files[0].endswith(".png")

    def test_scatter_plot(self):
        """Test creating a scatter plot."""
        code = """
x = np.random.rand(50)
y = np.random.rand(50)
plt.scatter(x, y)
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result

    def test_plot_with_physics_constants(self):
        """Test that physics constants are available."""
        code = """
# Test that physics constants are accessible
print(f"G = {G}")
print(f"c = {c}")
print(f"M_sun = {M_sun}")

# Create a simple plot using constants
masses = np.linspace(1, 10, 10) * M_sun
schwarzschild = 2 * G * masses / c**2
plt.plot(masses / M_sun, schwarzschild / 1000)
plt.xlabel('Mass (Solar Masses)')
plt.ylabel('Schwarzschild Radius (km)')
plt.title('Schwarzschild Radius vs Mass')
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result

    def test_orbital_mechanics_plot(self):
        """Test creating an orbital mechanics visualization."""
        code = """
# Plot a simple elliptical orbit
theta = np.linspace(0, 2 * pi, 100)
a = 1.5 * AU  # Semi-major axis
e = 0.2  # Eccentricity
r = a * (1 - e**2) / (1 + e * np.cos(theta))

x = r * np.cos(theta) / AU
y = r * np.sin(theta) / AU

plt.figure(figsize=(8, 8))
plt.plot(x, y, 'b-', label='Orbit')
plt.plot(0, 0, 'yo', markersize=15, label='Star')
plt.axis('equal')
plt.xlabel('Distance (AU)')
plt.ylabel('Distance (AU)')
plt.title('Elliptical Orbit')
plt.legend()
plt.grid(True)
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result


class TestCreatePlotErrors(unittest.TestCase):
    """Tests for error handling in create_plot."""

    def setUp(self):
        """Create a temporary directory for test outputs."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_syntax_error(self):
        """Test that syntax errors are properly reported."""
        code = """
x = [1, 2, 3
plt.plot(x)
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Syntax Error" in result

    def test_runtime_error(self):
        """Test that runtime errors are properly reported."""
        code = """
x = undefined_variable
plt.plot(x)
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Error creating plot" in result

    def test_no_plot_created(self):
        """Test warning when no plot is created."""
        code = """
# Just some calculations, no plot
x = np.linspace(0, 10, 100)
y = np.sin(x)
result = np.sum(y)
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "No plot was created" in result

    def test_division_by_zero(self):
        """Test handling of division by zero."""
        code = """
x = 0
y = 1 / x
plt.plot([y])
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Error creating plot" in result
        assert "division by zero" in result.lower()


class TestCreatePlotOutputDir(unittest.TestCase):
    """Tests for output directory handling."""

    def setUp(self):
        """Create a temporary base directory."""
        self.base_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.base_dir, ignore_errors=True)

    def test_creates_output_directory(self):
        """Test that output directory is created if it doesn't exist."""
        new_dir = os.path.join(self.base_dir, "new_output_dir")
        assert not os.path.exists(new_dir)

        code = """
plt.plot([1, 2, 3], [1, 4, 9])
"""
        result = create_plot(code, output_dir=new_dir)
        assert "Plot saved successfully" in result
        assert os.path.exists(new_dir)

    def test_nested_output_directory(self):
        """Test creating nested output directories."""
        nested_dir = os.path.join(self.base_dir, "level1", "level2", "plots")

        code = """
plt.plot([1, 2, 3], [1, 4, 9])
"""
        result = create_plot(code, output_dir=nested_dir)
        assert "Plot saved successfully" in result
        assert os.path.exists(nested_dir)


class TestCreatePlotSandbox(unittest.TestCase):
    """Tests for sandbox security in create_plot."""

    def setUp(self):
        """Create a temporary directory for test outputs."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_import_blocked(self):
        """Test that arbitrary imports are blocked."""
        code = """
import subprocess
subprocess.run(['ls'])
plt.plot([1, 2, 3])
"""
        result = create_plot(code, output_dir=self.test_dir)
        # Should fail because import is not in safe builtins
        assert "Error" in result

    def test_open_blocked(self):
        """Test that file operations are blocked."""
        code = """
f = open('/etc/passwd', 'r')
data = f.read()
plt.plot([1, 2, 3])
"""
        result = create_plot(code, output_dir=self.test_dir)
        # Should fail because open is not in safe builtins
        assert "Error" in result

    def test_exec_blocked(self):
        """Test that exec is blocked."""
        code = """
exec("import os; os.system('ls')")
plt.plot([1, 2, 3])
"""
        result = create_plot(code, output_dir=self.test_dir)
        # Should fail because exec is not in safe builtins
        assert "Error" in result

    def test_safe_builtins_available(self):
        """Test that safe builtins are available."""
        code = """
# Use various safe builtins
data = list(range(10))
data = [abs(x - 5) for x in data]
data_sum = sum(data)
data_max = max(data)
data_min = min(data)
data_len = len(data)

plt.plot(data)
plt.title(f'Sum: {data_sum}, Max: {data_max}, Min: {data_min}')
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result


class TestCreatePlotVisualizationTypes(unittest.TestCase):
    """Tests for various visualization types."""

    def setUp(self):
        """Create a temporary directory for test outputs."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_bar_chart(self):
        """Test creating a bar chart."""
        code = """
categories = ['Mercury', 'Venus', 'Earth', 'Mars']
values = [0.39, 0.72, 1.0, 1.52]
plt.bar(categories, values)
plt.ylabel('Distance from Sun (AU)')
plt.title('Inner Planets Distances')
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result

    def test_histogram(self):
        """Test creating a histogram."""
        code = """
data = np.random.normal(0, 1, 1000)
plt.hist(data, bins=30)
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('Normal Distribution')
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result

    def test_subplot(self):
        """Test creating subplots."""
        code = """
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

x = np.linspace(0, 2 * pi, 100)
ax1.plot(x, np.sin(x))
ax1.set_title('Sine')

ax2.plot(x, np.cos(x))
ax2.set_title('Cosine')

plt.tight_layout()
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result

    def test_polar_plot(self):
        """Test creating a polar plot."""
        code = """
theta = np.linspace(0, 2 * pi, 100)
r = np.abs(np.cos(2 * theta))

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.plot(theta, r)
ax.set_title('Polar Plot')
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result


class TestCreatePlotCosmologyExamples(unittest.TestCase):
    """Tests for cosmology-specific plotting examples."""

    def setUp(self):
        """Create a temporary directory for test outputs."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_hubble_diagram(self):
        """Test creating a Hubble diagram style plot."""
        code = """
# Simplified Hubble diagram
H0 = 70  # km/s/Mpc
distances = np.linspace(1, 100, 50)  # Mpc
velocities = H0 * distances

plt.figure(figsize=(8, 6))
plt.plot(distances, velocities, 'b-')
plt.xlabel('Distance (Mpc)')
plt.ylabel('Recession Velocity (km/s)')
plt.title('Hubble Diagram')
plt.grid(True)
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result

    def test_galaxy_rotation_curve(self):
        """Test creating a galaxy rotation curve."""
        code = """
# Simplified galaxy rotation curve showing dark matter evidence
r = np.linspace(1, 50, 100)  # kpc

# Keplerian (visible matter only)
v_keplerian = 200 / np.sqrt(r)

# Observed (flat due to dark matter)
v_observed = 200 * np.ones_like(r)
v_observed[:20] = 200 * np.sqrt(r[:20] / 20)

plt.figure(figsize=(8, 6))
plt.plot(r, v_keplerian, 'b--', label='Expected (visible matter)')
plt.plot(r, v_observed, 'r-', label='Observed')
plt.xlabel('Radius (kpc)')
plt.ylabel('Rotation Velocity (km/s)')
plt.title('Galaxy Rotation Curve')
plt.legend()
plt.grid(True)
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result

    def test_escape_velocity_plot(self):
        """Test plotting escape velocity vs radius."""
        code = """
# Escape velocity from Earth at different altitudes
altitudes = np.linspace(0, 10000, 100)  # km
radii = R_earth + altitudes * 1000  # Convert to meters

# v_escape = sqrt(2GM/r)
v_escape = np.sqrt(2 * G * M_earth / radii) / 1000  # km/s

plt.figure(figsize=(8, 6))
plt.plot(altitudes, v_escape, 'g-')
plt.xlabel('Altitude (km)')
plt.ylabel('Escape Velocity (km/s)')
plt.title('Escape Velocity vs Altitude from Earth')
plt.axhline(y=11.186, color='r', linestyle='--', label='Surface escape velocity')
plt.legend()
plt.grid(True)
"""
        result = create_plot(code, output_dir=self.test_dir)
        assert "Plot saved successfully" in result


class TestCreatePlotAgentIntegration(unittest.TestCase):
    """Tests for integration with the agent tool system."""

    def test_plot_tool_exists_in_agent(self):
        """Test that create_plot tool is properly integrated in agent."""
        from kosmo.agent import create_tools

        tools = create_tools()
        tool_names = [t.name for t in tools]
        assert "create_plot" in tool_names

    def test_plot_tool_description(self):
        """Test that create_plot tool has proper description."""
        from kosmo.agent import create_tools

        tools = create_tools()
        plot_tool = next(t for t in tools if t.name == "create_plot")
        assert "matplotlib" in plot_tool.description.lower()
        assert "visualization" in plot_tool.description.lower()

    def test_plot_tool_callable(self):
        """Test that create_plot tool is callable."""
        from kosmo.agent import create_tools

        tools = create_tools()
        plot_tool = next(t for t in tools if t.name == "create_plot")
        assert callable(plot_tool.func)


if __name__ == "__main__":
    unittest.main()
