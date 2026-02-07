"""Command-line interface for Kosmo - Cosmology Research Agent."""

import argparse
import sys

from . import __version__


def print_banner():
    """Print the Kosmo welcome banner."""
    banner = f"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🌌  KOSMO - Cosmology Research Agent  v{__version__:<18}║
║                                                               ║
║   An autonomous AI system for universe exploration            ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║   Commands:                                                   ║
║     Type your question and press Enter                        ║
║     'quit' or 'exit' - Exit the program                       ║
║     'clear' - Clear conversation history                      ║
║     'help' - Show this help message                           ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_help():
    """Print help information."""
    help_text = """
Available Commands:
  <question>  - Ask any cosmology or astrophysics question
  quit/exit   - Exit Kosmo
  clear       - Clear conversation history
  help        - Show this help message

Example Questions:
  - Calculate escape velocity from Earth
  - What is dark matter?
  - Simulate trajectory of a spacecraft to Mars
  - Plot the orbit of an exoplanet with 2x Earth mass at 1.5 AU
"""
    print(help_text)


def run_interactive(verbose: bool = True):
    """Run the interactive CLI loop.

    Args:
        verbose: Whether to show intermediate reasoning steps
    """
    from .agent import KosmoAgent

    print_banner()

    try:
        agent = KosmoAgent(verbose=verbose)
    except ValueError as e:
        print(f"\nError: {e}")
        print("Please set your OPENAI_API_KEY environment variable.")
        sys.exit(1)

    while True:
        try:
            # Get user input
            user_input = input("\n🔭 You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ("quit", "exit"):
                print("\n✨ Thank you for exploring the cosmos with Kosmo!")
                break

            if user_input.lower() == "clear":
                agent.clear_memory()
                print("🧹 Conversation history cleared.")
                continue

            if user_input.lower() == "help":
                print_help()
                continue

            # Process the query
            print("\n🌟 Kosmo is thinking...\n")
            response = agent.query(user_input)
            print(f"\n🌌 Kosmo: {response}")

        except KeyboardInterrupt:
            print("\n\n✨ Thank you for exploring the cosmos with Kosmo!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def run_single_query(query: str, verbose: bool = True) -> str:
    """Run a single query and return the response.

    Args:
        query: The question to ask
        verbose: Whether to show intermediate steps

    Returns:
        The agent's response
    """
    from .agent import KosmoAgent

    agent = KosmoAgent(verbose=verbose)
    return agent.query(query)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Kosmo - Cosmology Research Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kosmo                                    # Start interactive mode
  kosmo "What is dark matter?"             # Single query
  kosmo -q "Calculate escape velocity"     # Single query with -q flag
  kosmo --quiet "Explain black holes"      # Single query without verbose output
"""
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Optional query to run (if not provided, starts interactive mode)"
    )

    parser.add_argument(
        "-q", "--query",
        dest="query_flag",
        help="Query to run (alternative to positional argument)"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress intermediate reasoning output"
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"Kosmo {__version__}"
    )

    args = parser.parse_args()

    # Determine the query (positional or flag)
    query = args.query or args.query_flag
    verbose = not args.quiet

    if query:
        # Single query mode
        try:
            response = run_single_query(query, verbose=verbose)
            print(f"\n🌌 Kosmo: {response}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        # Interactive mode
        run_interactive(verbose=verbose)


if __name__ == "__main__":
    main()
