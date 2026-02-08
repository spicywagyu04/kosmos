# Kosmo - Cosmology Research Agent

An autonomous AI-powered research assistant for cosmology and astrophysics exploration. Kosmo uses a ReAct (Reason-Act) loop to break down complex scientific queries, leverage integrated tools, and generate comprehensive answers with calculations, visualizations, and citations.

## Features

- **ReAct Agent Loop**: Autonomous multi-step reasoning with Thought-Action-Observation cycles
- **Web Search**: Query arXiv papers, NASA data, and scientific databases via Tavily
- **Code Execution**: Run Python physics calculations with NumPy, SymPy, and SciPy
- **Knowledge Base**: Quick scientific fact retrieval via Wikipedia
- **Visualization**: Generate orbital plots, trajectories, and data charts with Matplotlib
- **Session Memory**: Multi-turn conversation support with context retention
- **Graceful Degradation**: Automatic error recovery and fallback handling

## Installation

### Prerequisites

- Python 3.9 or higher
- OpenAI API key
- Tavily API key (for web search)

### Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/kosmo.git
cd kosmo
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -e .
```

4. Configure API keys:

```bash
cp .env.example .env
# Edit .env and add your API keys
```

Your `.env` file should contain:

```
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## Usage

### Interactive Mode

Start an interactive session to ask multiple questions:

```bash
kosmo
```

This launches the Kosmo CLI where you can type questions and receive answers in a conversational format.

### Single Query Mode

Ask a single question from the command line:

```bash
kosmo "Calculate the escape velocity from Earth"
```

Or use the `-q` flag:

```bash
kosmo -q "What is dark matter?"
```

### Command Line Options

```
kosmo [query]              Start interactive mode or run a single query
  -q, --query QUERY        Query to run (alternative to positional argument)
  --quiet                  Suppress intermediate reasoning output
  -v, --version            Show version number
  -h, --help               Show help message
```

### Interactive Commands

When in interactive mode:

- Type your question and press Enter
- `quit` or `exit` - Exit the program
- `clear` - Clear conversation history
- `help` - Show help message

## Example Queries

### Basic Calculations

```
Calculate the escape velocity from Earth
```

```
What is the Schwarzschild radius of a 10 solar mass black hole?
```

### Orbital Mechanics

```
Simulate the trajectory of a spacecraft from Earth to Mars
```

```
Plot the orbit of an exoplanet with 2x Earth mass at 1.5 AU
```

### Research Questions

```
Analyze recent data on black holes
```

```
What is dark matter and how do we detect it?
```

```
Explain the cosmic microwave background radiation
```

## Python API

Use Kosmo programmatically in your Python code:

```python
from kosmo import KosmoAgent

# Create an agent
agent = KosmoAgent(verbose=True)

# Ask a question
response = agent.query("Calculate the orbital period of Mars")
print(response)

# Multi-turn conversation (memory is enabled by default)
response1 = agent.query("What is the mass of Jupiter?")
response2 = agent.query("How does that compare to Saturn?")

# Start a new session
agent.new_session()
```

### Agent Configuration

```python
agent = KosmoAgent(
    verbose=True,              # Show intermediate reasoning steps
    max_retries=3,             # Maximum retries for failed operations
    enable_memory=True,        # Enable session memory
    use_topic_prompts=True,    # Use topic-specific prompt enhancements
    graceful_degradation=True  # Enable graceful error handling
)
```

## Examples Module

Kosmo includes example simulations for orbital mechanics:

### Hohmann Transfer Orbits

```python
from examples import calculate_planetary_transfer, generate_transfer_plot_code

# Calculate Earth to Mars transfer
result = calculate_planetary_transfer("Earth", "Mars")
print(f"Transfer time: {result.transfer_time / 86400:.1f} days")
print(f"Total delta-v: {result.total_delta_v / 1000:.2f} km/s")

# Generate visualization code
plot_code = generate_transfer_plot_code(result)
```

### Kepler Orbits

```python
from examples import calculate_orbit_from_period, get_exoplanet_example

# Calculate orbit from period
orbit = calculate_orbit_from_period(365.25 * 86400)  # Earth's orbital period
print(f"Semi-major axis: {orbit.semi_major_axis / 1.496e11:.2f} AU")

# Get pre-defined exoplanet examples
kepler_442b = get_exoplanet_example("Kepler-442b")
```

## Architecture

Kosmo follows a modular three-layer agent architecture. For a detailed architecture overview, see [docs/architecture.md](docs/architecture.md).

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│              (CLI / Python API / Streamlit)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Agent Core Layer                          │
│                  (ReAct Reasoning Engine)                    │
│                                                              │
│   ┌──────────┐    ┌──────────┐    ┌───────────────┐         │
│   │  Thought │ -> │  Action  │ -> │  Observation  │         │
│   └──────────┘    └──────────┘    └───────────────┘         │
│         ^                                    │                │
│         └────────────────────────────────────┘                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      Tool Layer                              │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌─────────┐      │
│  │   Web   │  │   Code   │  │ Knowledge │  │ Plotter │      │
│  │ Search  │  │ Executor │  │   Base    │  │         │      │
│  └─────────┘  └──────────┘  └───────────┘  └─────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### ReAct Loop

Each iteration follows the Thought-Action-Observation pattern:

1. **Thought**: Agent reasons about what information is needed
2. **Action**: Agent calls a specific tool with parameters
3. **Observation**: Tool returns results for the agent to evaluate
4. **Termination**: Loop ends when the agent has sufficient information (max 10 iterations)

## Project Structure

```
kosmo/
├── src/
│   └── kosmo/
│       ├── __init__.py      # Package exports
│       ├── __main__.py      # Module entry point
│       ├── agent.py         # ReAct agent implementation
│       ├── cli.py           # Command-line interface
│       ├── errors.py        # Error handling and graceful degradation
│       ├── prompts/         # System prompts and topic templates
│       └── tools/           # Tool implementations
├── examples/
│   ├── hohmann_transfer.py  # Hohmann transfer orbit simulation
│   └── kepler_orbit.py      # Kepler orbit calculator
├── tests/                   # Comprehensive test suite
├── docs/                    # Documentation
├── pyproject.toml           # Package configuration
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Linting

```bash
ruff check src tests
```

## Disclaimer and Ethical Usage

Kosmo is designed for **educational and research exploration purposes only**. Please read and understand these important points:

### Simulation Accuracy

- **Simplified Models**: Calculations use idealized physics models that may not account for gravitational perturbations, relativistic effects, atmospheric drag, or other real-world factors.
- **Approximate Constants**: Physical constants are suitable for educational purposes but may not meet precision requirements for scientific publications or mission planning.
- **No Warranty**: All outputs are provided "as-is" without warranty. Verify critical calculations through authoritative sources.

### Responsible Use

- **Verification Required**: Always cross-reference results with established tools (NASA GMAT, STK) and peer-reviewed literature.
- **Not for Mission-Critical Use**: Do not use for spacecraft navigation, engineering decisions, or safety-critical applications.
- **Academic Integrity**: Follow your institution's policies on AI-assisted work and cite AI usage appropriately.
- **Data Privacy**: Avoid submitting personal or confidential information in queries.

### AI Limitations

- The underlying LLM may occasionally generate incorrect or hallucinated information
- Web search results include non-peer-reviewed sources (arXiv preprints, news articles)
- Always verify key facts against primary scientific sources

For comprehensive guidelines, see [docs/ethical_usage.md](docs/ethical_usage.md).

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Acknowledgments

- Built with [LangChain](https://www.langchain.com/) and [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by OpenAI GPT models
- Web search via [Tavily](https://tavily.com/)
