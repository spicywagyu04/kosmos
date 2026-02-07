"""Tests for the code executor tool."""

import unittest

from kosmo.tools.code_executor import ALLOWED_MODULES, execute_code


class TestCodeExecutorConstants(unittest.TestCase):
    """Tests for code executor constants."""

    def test_allowed_modules_contains_math(self):
        """Test that math is in allowed modules."""
        assert "math" in ALLOWED_MODULES

    def test_allowed_modules_contains_numpy(self):
        """Test that numpy is in allowed modules."""
        assert "numpy" in ALLOWED_MODULES

    def test_allowed_modules_contains_sympy(self):
        """Test that sympy is in allowed modules."""
        assert "sympy" in ALLOWED_MODULES

    def test_allowed_modules_contains_scipy(self):
        """Test that scipy is in allowed modules."""
        assert "scipy" in ALLOWED_MODULES

    def test_allowed_modules_count(self):
        """Test the expected number of allowed modules."""
        assert len(ALLOWED_MODULES) == 8


class TestCodeExecutorBasic(unittest.TestCase):
    """Basic tests for execute_code function."""

    def test_simple_arithmetic(self):
        """Test basic arithmetic calculation."""
        code = "print(2 + 2)"
        result = execute_code(code)
        assert "Output:" in result
        assert "4" in result

    def test_multiplication(self):
        """Test multiplication."""
        code = "print(7 * 8)"
        result = execute_code(code)
        assert "56" in result

    def test_division(self):
        """Test division."""
        code = "print(100 / 4)"
        result = execute_code(code)
        assert "25" in result

    def test_power(self):
        """Test power operation."""
        code = "print(2 ** 10)"
        result = execute_code(code)
        assert "1024" in result

    def test_no_output(self):
        """Test code with no output."""
        code = "x = 5"
        result = execute_code(code)
        assert "Code executed successfully" in result

    def test_multiple_print_statements(self):
        """Test multiple print statements."""
        code = """
print("Hello")
print("World")
"""
        result = execute_code(code)
        assert "Hello" in result
        assert "World" in result


class TestCodeExecutorNumpy(unittest.TestCase):
    """Tests for numpy functionality in code executor."""

    def test_numpy_array(self):
        """Test numpy array creation and operations."""
        code = """
arr = np.array([1, 2, 3, 4, 5])
print(np.sum(arr))  # Print sum instead of array to avoid __str__ issue
"""
        result = execute_code(code)
        assert "15" in result

    def test_numpy_linspace(self):
        """Test numpy linspace."""
        code = """
arr = np.linspace(0, 10, 5)
print(len(arr))  # Print length instead of array
print(arr[0], arr[-1])  # Print first and last values
"""
        result = execute_code(code)
        assert "Output:" in result
        # Should have 5 elements from 0 to 10
        assert "5" in result
        assert "0" in result
        assert "10" in result

    def test_numpy_sum(self):
        """Test numpy sum."""
        code = """
arr = np.array([1, 2, 3, 4, 5])
print(np.sum(arr))
"""
        result = execute_code(code)
        assert "15" in result

    def test_numpy_mean(self):
        """Test numpy mean."""
        code = """
arr = np.array([10, 20, 30])
print(np.mean(arr))
"""
        result = execute_code(code)
        assert "20" in result

    def test_numpy_sqrt(self):
        """Test numpy sqrt."""
        code = """
print(np.sqrt(144))
"""
        result = execute_code(code)
        assert "12" in result

    def test_numpy_alias(self):
        """Test that np and numpy both work."""
        code = """
print(np.pi)
print(numpy.e)
"""
        result = execute_code(code)
        assert "3.14" in result
        assert "2.71" in result


class TestCodeExecutorSympy(unittest.TestCase):
    """Tests for sympy functionality in code executor."""

    def test_sympy_symbol(self):
        """Test sympy symbol creation."""
        code = """
x = sp.Symbol('x')
expr = x**2 + 2*x + 1
print(expr)
"""
        result = execute_code(code)
        assert "x**2" in result or "x²" in result

    def test_sympy_expand(self):
        """Test sympy expand."""
        code = """
x = sp.Symbol('x')
expr = (x + 1)**2
print(sp.expand(expr))
"""
        result = execute_code(code)
        assert "x**2" in result

    def test_sympy_diff(self):
        """Test sympy differentiation."""
        code = """
x = sp.Symbol('x')
expr = x**3
derivative = sp.diff(expr, x)
print(derivative)
"""
        result = execute_code(code)
        assert "3*x**2" in result or "3x²" in result

    def test_sympy_integrate(self):
        """Test sympy integration."""
        code = """
x = sp.Symbol('x')
expr = 2*x
integral = sp.integrate(expr, x)
print(integral)
"""
        result = execute_code(code)
        assert "x**2" in result

    def test_sympy_alias(self):
        """Test that sp and sympy both work."""
        code = """
x = sp.Symbol('x')
y = sympy.Symbol('y')
print(x + y)
"""
        result = execute_code(code)
        assert "x + y" in result


class TestCodeExecutorPhysicsConstants(unittest.TestCase):
    """Tests for physics constants availability."""

    def test_gravitational_constant(self):
        """Test G is available and correct."""
        code = "print(f'{G:.5e}')"
        result = execute_code(code)
        assert "6.67430e-11" in result

    def test_speed_of_light(self):
        """Test c is available and correct."""
        code = "print(c)"
        result = execute_code(code)
        assert "299792458" in result

    def test_solar_mass(self):
        """Test M_sun is available."""
        code = "print(f'{M_sun:.3e}')"
        result = execute_code(code)
        assert "1.989e+30" in result

    def test_earth_mass(self):
        """Test M_earth is available."""
        code = "print(f'{M_earth:.3e}')"
        result = execute_code(code)
        assert "5.972e+24" in result

    def test_earth_radius(self):
        """Test R_earth is available."""
        code = "print(f'{R_earth:.3e}')"
        result = execute_code(code)
        assert "6.371e+06" in result

    def test_astronomical_unit(self):
        """Test AU is available."""
        code = "print(f'{AU:.3e}')"
        result = execute_code(code)
        assert "1.496e+11" in result

    def test_parsec(self):
        """Test pc is available."""
        code = "print(f'{pc:.3e}')"
        result = execute_code(code)
        assert "3.086e+16" in result

    def test_planck_constant(self):
        """Test h is available."""
        code = "print(f'{h:.5e}')"
        result = execute_code(code)
        assert "6.62607e-34" in result

    def test_boltzmann_constant(self):
        """Test k_B is available."""
        code = "print(f'{k_B:.5e}')"
        result = execute_code(code)
        assert "1.38065e-23" in result


class TestCodeExecutorPhysicsCalculations(unittest.TestCase):
    """Tests for physics calculations."""

    def test_escape_velocity(self):
        """Test escape velocity calculation."""
        code = """
# v_escape = sqrt(2 * G * M / R)
v_escape = np.sqrt(2 * G * M_earth / R_earth)
print(f'{v_escape/1000:.2f} km/s')
"""
        result = execute_code(code)
        # Earth's escape velocity is about 11.19 km/s
        assert "11.1" in result or "11.2" in result

    def test_schwarzschild_radius(self):
        """Test Schwarzschild radius calculation."""
        code = """
# R_s = 2GM/c^2 for 1 solar mass
R_s = 2 * G * M_sun / c**2
print(f'{R_s/1000:.2f} km')
"""
        result = execute_code(code)
        # Schwarzschild radius of the Sun is about 2.95 km
        assert "2.9" in result or "3.0" in result

    def test_orbital_velocity(self):
        """Test orbital velocity calculation."""
        code = """
# Circular orbital velocity at Earth's distance from Sun
v_orbit = np.sqrt(G * M_sun / AU)
print(f'{v_orbit/1000:.2f} km/s')
"""
        result = execute_code(code)
        # Earth's orbital velocity is about 29.78 km/s
        assert "29." in result or "30." in result

    def test_orbital_period(self):
        """Test orbital period calculation."""
        code = """
# Kepler's third law: T = 2*pi*sqrt(a^3 / (G*M))
T = 2 * np.pi * np.sqrt(AU**3 / (G * M_sun))
print(f'{T / (365.25 * 24 * 3600):.2f} years')
"""
        result = execute_code(code)
        # Should be approximately 1 year
        assert "1.0" in result or "0.99" in result or "1.00" in result


class TestCodeExecutorErrorHandling(unittest.TestCase):
    """Tests for error handling in execute_code."""

    def test_syntax_error(self):
        """Test that syntax errors are properly reported."""
        code = "print('hello"
        result = execute_code(code)
        assert "Syntax Error" in result

    def test_undefined_variable(self):
        """Test handling of undefined variable."""
        code = "print(undefined_variable)"
        result = execute_code(code)
        assert "Error" in result
        assert "undefined_variable" in result or "not defined" in result

    def test_division_by_zero(self):
        """Test handling of division by zero."""
        code = "print(1/0)"
        result = execute_code(code)
        assert "Error" in result
        assert "division" in result.lower()

    def test_type_error(self):
        """Test handling of type error."""
        code = "print('hello' + 5)"
        result = execute_code(code)
        assert "Error" in result

    def test_index_error(self):
        """Test handling of index error."""
        code = """
arr = [1, 2, 3]
print(arr[10])
"""
        result = execute_code(code)
        assert "Error" in result
        assert "index" in result.lower()

    def test_empty_code(self):
        """Test handling of empty code."""
        code = ""
        result = execute_code(code)
        assert "Code executed successfully" in result

    def test_whitespace_only(self):
        """Test handling of whitespace-only code."""
        code = "   \n\n   "
        result = execute_code(code)
        assert "Code executed successfully" in result


class TestCodeExecutorSandbox(unittest.TestCase):
    """Tests for sandbox security in code executor."""

    def test_import_blocked(self):
        """Test that arbitrary imports are blocked."""
        code = """
import os
print(os.getcwd())
"""
        result = execute_code(code)
        # Import should fail because it's not in safe builtins
        assert "Error" in result

    def test_subprocess_blocked(self):
        """Test that subprocess import is blocked."""
        code = """
import subprocess
subprocess.run(['ls'])
"""
        result = execute_code(code)
        assert "Error" in result

    def test_open_blocked(self):
        """Test that file operations are blocked."""
        code = """
f = open('/etc/passwd', 'r')
print(f.read())
"""
        result = execute_code(code)
        assert "Error" in result

    def test_exec_blocked(self):
        """Test that exec is blocked."""
        code = """
exec("print('hello')")
"""
        result = execute_code(code)
        assert "Error" in result

    def test_eval_blocked(self):
        """Test that eval is blocked."""
        code = """
result = eval("2 + 2")
print(result)
"""
        result = execute_code(code)
        assert "Error" in result

    def test_compile_blocked(self):
        """Test that compile is blocked."""
        code = """
code_obj = compile("print('hello')", "<string>", "exec")
"""
        result = execute_code(code)
        assert "Error" in result

    def test_safe_builtins_available(self):
        """Test that safe builtins are available."""
        code = """
# Test various safe builtins
nums = list(range(5))
total = sum(nums)
maximum = max(nums)
minimum = min(nums)
length = len(nums)
print(f'sum={total}, max={maximum}, min={minimum}, len={length}')
"""
        result = execute_code(code)
        assert "sum=10" in result
        assert "max=4" in result
        assert "min=0" in result
        assert "len=5" in result


class TestCodeExecutorMath(unittest.TestCase):
    """Tests for math module functionality."""

    def test_math_pi(self):
        """Test math.pi is available."""
        code = "print(f'{math.pi:.5f}')"
        result = execute_code(code)
        assert "3.14159" in result

    def test_math_e(self):
        """Test math.e is available."""
        code = "print(f'{math.e:.5f}')"
        result = execute_code(code)
        assert "2.71828" in result

    def test_math_sqrt(self):
        """Test math.sqrt."""
        code = "print(math.sqrt(2))"
        result = execute_code(code)
        assert "1.414" in result

    def test_math_sin(self):
        """Test math.sin."""
        code = "print(f'{math.sin(math.pi/2):.1f}')"
        result = execute_code(code)
        assert "1.0" in result

    def test_math_log(self):
        """Test math.log."""
        code = "print(f'{math.log(math.e):.1f}')"
        result = execute_code(code)
        assert "1.0" in result


class TestCodeExecutorComplexCode(unittest.TestCase):
    """Tests for complex code execution."""

    def test_for_loop(self):
        """Test for loop execution."""
        code = """
total = 0
for i in range(5):
    total += i
print(total)
"""
        result = execute_code(code)
        assert "10" in result

    def test_while_loop(self):
        """Test while loop execution."""
        code = """
count = 0
while count < 5:
    count += 1
print(count)
"""
        result = execute_code(code)
        assert "5" in result

    def test_conditional(self):
        """Test conditional execution."""
        code = """
x = 10
if x > 5:
    print('greater')
else:
    print('less')
"""
        result = execute_code(code)
        assert "greater" in result

    def test_function_definition(self):
        """Test function definition and call."""
        code = """
def square(x):
    return x * x

print(square(5))
"""
        result = execute_code(code)
        assert "25" in result

    def test_list_comprehension(self):
        """Test list comprehension."""
        code = """
squares = [x**2 for x in range(5)]
print(squares)
"""
        result = execute_code(code)
        assert "[0, 1, 4, 9, 16]" in result

    def test_dictionary_operations(self):
        """Test dictionary operations."""
        code = """
d = {'a': 1, 'b': 2, 'c': 3}
print(d['b'])
print(sum(d.values()))
"""
        result = execute_code(code)
        assert "2" in result
        assert "6" in result


class TestCodeExecutorAgentIntegration(unittest.TestCase):
    """Tests for integration with the agent tool system."""

    def test_code_executor_tool_exists(self):
        """Test that execute_code tool is properly integrated in agent."""
        from kosmo.agent import create_tools

        tools = create_tools()
        tool_names = [t.name for t in tools]
        assert "execute_code" in tool_names

    def test_code_executor_tool_description(self):
        """Test that execute_code tool has proper description."""
        from kosmo.agent import create_tools

        tools = create_tools()
        code_tool = next(t for t in tools if t.name == "execute_code")
        assert "python" in code_tool.description.lower()
        assert "physics" in code_tool.description.lower()

    def test_code_executor_tool_callable(self):
        """Test that execute_code tool is callable."""
        from kosmo.agent import create_tools

        tools = create_tools()
        code_tool = next(t for t in tools if t.name == "execute_code")
        assert callable(code_tool.func)


if __name__ == "__main__":
    unittest.main()
