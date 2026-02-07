"""Plotting tool using Matplotlib."""

import io
import os
import traceback
import uuid
from contextlib import redirect_stderr, redirect_stdout


def create_plot(code: str, output_dir: str = "outputs") -> str:
    """
    Generate a visualization using Matplotlib.

    The code should create a matplotlib figure. The function will automatically
    save it and return the filename.

    Args:
        code: Python code that creates a matplotlib figure
        output_dir: Directory to save plots (default: "outputs")

    Returns:
        Path to the saved plot or error message
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate unique filename
    filename = f"plot_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(output_dir, filename)

    # Create isolated namespace
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

    try:
        import matplotlib
        import numpy as np
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt

        namespace["np"] = np
        namespace["numpy"] = np
        namespace["plt"] = plt
        namespace["matplotlib"] = matplotlib

        # Physics constants
        namespace["G"] = 6.67430e-11
        namespace["c"] = 299792458
        namespace["M_sun"] = 1.989e30
        namespace["M_earth"] = 5.972e24
        namespace["R_earth"] = 6.371e6
        namespace["AU"] = 1.496e11
        namespace["pi"] = np.pi

    except ImportError as e:
        return f"Error: Required module not available: {e}"

    # Capture output
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # Clear any existing figures
            plt.close('all')

            # Execute the plotting code
            compiled = compile(code, "<plot_code>", "exec")
            exec(compiled, namespace)

            # Save the current figure
            fig = plt.gcf()
            if fig.get_axes():
                fig.savefig(filepath, dpi=150, bbox_inches='tight',
                           facecolor='white', edgecolor='none')
                plt.close('all')
                return f"Plot saved successfully: {filepath}"
            else:
                return "Warning: No plot was created. Make sure your code calls plt.plot() or similar."

    except SyntaxError as e:
        return f"Syntax Error in plotting code: {e}"
    except Exception as e:
        tb = traceback.format_exc()
        return f"Error creating plot: {e}\n\nTraceback:\n{tb}"
