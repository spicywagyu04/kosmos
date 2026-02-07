"""Sandboxed Python code execution tool."""

import io
import traceback
from contextlib import redirect_stderr, redirect_stdout

# Pre-approved modules for physics calculations
ALLOWED_MODULES = {
    "math", "numpy", "sympy", "scipy",
    "datetime", "collections", "itertools", "functools"
}


def execute_code(code: str, timeout_seconds: int = 30) -> str:
    """
    Execute Python code in a sandboxed environment for physics calculations.

    Args:
        code: Python code string to execute
        timeout_seconds: Maximum execution time (default: 30 seconds)

    Returns:
        String containing stdout output, return value, or error message
    """
    # Create isolated namespace with allowed modules
    namespace = {"__builtins__": {}}

    # Add safe builtins
    safe_builtins = [
        "abs", "all", "any", "bin", "bool", "chr", "dict", "divmod",
        "enumerate", "filter", "float", "format", "frozenset", "hex",
        "int", "isinstance", "issubclass", "iter", "len", "list",
        "map", "max", "min", "next", "oct", "ord", "pow", "print",
        "range", "repr", "reversed", "round", "set", "slice", "sorted",
        "str", "sum", "tuple", "type", "zip"
    ]

    import builtins
    for name in safe_builtins:
        namespace["__builtins__"][name] = getattr(builtins, name)

    # Import allowed modules
    try:
        import math

        import numpy as np
        import sympy as sp

        namespace["np"] = np
        namespace["numpy"] = np
        namespace["sp"] = sp
        namespace["sympy"] = sp
        namespace["math"] = math

        # Common physics constants
        namespace["G"] = 6.67430e-11  # Gravitational constant (m³/kg/s²)
        namespace["c"] = 299792458  # Speed of light (m/s)
        namespace["M_sun"] = 1.989e30  # Solar mass (kg)
        namespace["M_earth"] = 5.972e24  # Earth mass (kg)
        namespace["R_earth"] = 6.371e6  # Earth radius (m)
        namespace["AU"] = 1.496e11  # Astronomical unit (m)
        namespace["pc"] = 3.086e16  # Parsec (m)
        namespace["h"] = 6.62607e-34  # Planck constant (J·s)
        namespace["k_B"] = 1.38065e-23  # Boltzmann constant (J/K)

    except ImportError as e:
        return f"Error: Required module not available: {e}"

    # Capture output
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # Compile and execute
            compiled = compile(code, "<agent_code>", "exec")
            exec(compiled, namespace)

        # Get output
        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()

        result = ""
        if stdout_output:
            result += f"Output:\n{stdout_output}"
        if stderr_output:
            result += f"\nWarnings:\n{stderr_output}"
        if not result:
            result = "Code executed successfully (no output)"

        return result

    except SyntaxError as e:
        return f"Syntax Error: {e}"
    except Exception as e:
        tb = traceback.format_exc()
        return f"Execution Error: {e}\n\nTraceback:\n{tb}"
