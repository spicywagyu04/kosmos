# Kosmo Architecture Overview

This document provides a detailed overview of the Kosmo Cosmology Research Agent architecture.

## High-Level Architecture

Kosmo follows a modular three-layer architecture designed for extensibility and maintainability:

```
                              ┌─────────────────────┐
                              │       User          │
                              └──────────┬──────────┘
                                         │
                                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │   CLI Interface  │  │   Python API     │  │   Streamlit (optional)   │  │
│  │   (cli.py)       │  │   (KosmoAgent)   │  │                          │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────────┬─────────────┘  │
│           │                     │                          │                │
│           └─────────────────────┼──────────────────────────┘                │
│                                 │                                           │
└─────────────────────────────────┼───────────────────────────────────────────┘
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                            AGENT CORE LAYER                                 │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     ReAct Reasoning Engine                             │ │
│  │                        (agent.py)                                      │ │
│  │                                                                        │ │
│  │   ┌─────────────┐      ┌─────────────┐      ┌─────────────────────┐   │ │
│  │   │   THOUGHT   │ ───► │   ACTION    │ ───► │    OBSERVATION      │   │ │
│  │   │             │      │             │      │                     │   │ │
│  │   │  "I need to │      │ web_search( │      │  "Found 5 papers    │   │ │
│  │   │   find..."  │      │  "dark..."  │      │   on arXiv..."      │   │ │
│  │   └─────────────┘      └─────────────┘      └──────────┬──────────┘   │ │
│  │          ▲                                              │              │ │
│  │          │                                              │              │ │
│  │          └──────────────────────────────────────────────┘              │ │
│  │                         (Loop until complete)                          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │ Session Memory  │  │ Error Handler   │  │ Topic Prompt Enhancement    │ │
│  │ (InMemorySaver) │  │ (errors.py)     │  │ (cosmology_templates.py)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                              TOOL LAYER                                     │
│                                                                             │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌───────────┐ │
│  │  Web Search    │  │ Code Executor  │  │ Knowledge Base │  │  Plotter  │ │
│  │                │  │                │  │                │  │           │ │
│  │  - Tavily API  │  │  - NumPy       │  │  - Wikipedia   │  │ Matplotlib│ │
│  │  - arXiv       │  │  - SymPy       │  │    API         │  │           │ │
│  │  - NASA data   │  │  - SciPy       │  │  - Quick facts │  │ - Orbits  │ │
│  │                │  │  - Physics     │  │  - Definitions │  │ - Charts  │ │
│  │                │  │    constants   │  │                │  │ - Data    │ │
│  └────────────────┘  └────────────────┘  └────────────────┘  └───────────┘ │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES                                  │
│                                                                             │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────────────┐│
│  │  OpenAI API    │  │  Tavily API    │  │  Wikipedia API                 ││
│  │  (GPT-4o-mini) │  │  (Web Search)  │  │  (Knowledge Retrieval)         ││
│  └────────────────┘  └────────────────┘  └────────────────────────────────┘│
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interface Layer

The UI layer provides multiple ways to interact with Kosmo:

| Component | File | Description |
|-----------|------|-------------|
| CLI Interface | `cli.py` | Interactive terminal with single-query and conversational modes |
| Python API | `agent.py` | `KosmoAgent` class for programmatic access |
| Streamlit | (optional) | Web-based chat interface |

### 2. Agent Core Layer

The core layer implements the ReAct (Reason-Act) pattern using LangGraph:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ReAct Loop Execution                          │
│                                                                  │
│   Iteration 1:                                                   │
│   ┌──────────┐    ┌─────────────────┐    ┌──────────────────┐   │
│   │ Thought: │ -> │ Action:         │ -> │ Observation:     │   │
│   │ Need to  │    │ web_search(     │    │ Found paper on   │   │
│   │ research │    │   "Hohmann...")  │    │ orbital mech.    │   │
│   └──────────┘    └─────────────────┘    └──────────────────┘   │
│                                                   │              │
│                                                   ▼              │
│   Iteration 2:                                                   │
│   ┌──────────┐    ┌─────────────────┐    ┌──────────────────┐   │
│   │ Thought: │ -> │ Action:         │ -> │ Observation:     │   │
│   │ Now calc │    │ code_executor(  │    │ delta_v = 3.6    │   │
│   │ delta-v  │    │   "import np.." │    │ km/s             │   │
│   └──────────┘    └─────────────────┘    └──────────────────┘   │
│                                                   │              │
│                                                   ▼              │
│   Iteration 3:                                                   │
│   ┌──────────┐    ┌─────────────────┐    ┌──────────────────┐   │
│   │ Thought: │ -> │ Action:         │ -> │ Observation:     │   │
│   │ Visualize│    │ plotter(        │    │ Plot saved to    │   │
│   │ orbit    │    │   "plt.plot.."  │    │ output/orbit.png │   │
│   └──────────┘    └─────────────────┘    └──────────────────┘   │
│                                                   │              │
│                                                   ▼              │
│                          ┌──────────────────────────┐            │
│                          │   FINAL ANSWER           │            │
│                          │   Synthesized response   │            │
│                          │   with all findings      │            │
│                          └──────────────────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**

- **Session Memory**: Uses LangGraph's `InMemorySaver` for multi-turn conversations
- **Error Handling**: Graceful degradation when tools fail, with retry logic
- **Topic Detection**: Automatically enhances prompts for dark matter, exoplanet, and CMB queries

### 3. Tool Layer

Each tool is a standalone module with clear responsibilities:

#### Web Search Tool
```python
# Uses Tavily API for scientific search
web_search(query: str, max_results: int = 5) -> str
```
- Searches arXiv, NASA, and scientific databases
- Returns formatted results with titles, URLs, and snippets

#### Code Executor Tool
```python
# Sandboxed Python REPL with physics libraries
code_executor(code: str) -> str
```
- **Allowed modules**: math, numpy, sympy, scipy.constants
- **Physics constants**: G, c, M_sun, M_earth, AU, parsec, h, k_B
- **Security**: Restricted imports, no file I/O, execution timeout

#### Knowledge Base Tool
```python
# Wikipedia API integration
knowledge_base(topic: str, sentences: int = 5) -> str
```
- Quick fact retrieval for scientific definitions
- Automatic disambiguation handling

#### Plotter Tool
```python
# Matplotlib visualization
plotter(code: str, output_path: str = "output/plot.png") -> str
```
- Generates orbital plots, trajectories, and data charts
- Saves images to specified output directory

## Data Flow

```
User Query: "Simulate trajectory from Earth to Mars"
                    │
                    ▼
            ┌───────────────┐
            │  Parse Query  │
            └───────┬───────┘
                    │
                    ▼
            ┌───────────────┐
            │ Topic Detect  │──── Enhances prompt with orbital mechanics context
            └───────┬───────┘
                    │
                    ▼
         ┌──────────────────────┐
         │   ReAct Loop Start   │
         └──────────┬───────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
┌─────────┐   ┌──────────┐   ┌──────────┐
│ Search  │   │ Calculate│   │ Visualize│
│ Papers  │   │ Transfer │   │ Orbit    │
└────┬────┘   └────┬─────┘   └────┬─────┘
     │             │              │
     └─────────────┼──────────────┘
                   │
                   ▼
           ┌───────────────┐
           │   Synthesize  │
           │    Answer     │
           └───────┬───────┘
                   │
                   ▼
           ┌───────────────┐
           │ Final Output  │
           │ + Plot Image  │
           └───────────────┘
```

## Error Handling & Graceful Degradation

```
┌─────────────────────────────────────────────────────────────┐
│                   Error Handling Flow                        │
│                                                              │
│   Tool Call ──► Exception Caught ──► Error Classification   │
│                                              │               │
│                          ┌───────────────────┼───────────┐   │
│                          ▼                   ▼           ▼   │
│                   ┌──────────┐        ┌──────────┐ ┌───────┐ │
│                   │ Transient│        │ Critical │ │ Other │ │
│                   │ (retry)  │        │ (stop)   │ │(degrade│ │
│                   └────┬─────┘        └────┬─────┘ └───┬───┘ │
│                        │                   │           │     │
│                        ▼                   ▼           ▼     │
│                   ┌──────────┐        ┌──────────┐ ┌───────┐ │
│                   │ Retry    │        │ Return   │ │ Mark  │ │
│                   │ with     │        │ Error    │ │ Tool  │ │
│                   │ backoff  │        │ Message  │ │Failed │ │
│                   └──────────┘        └──────────┘ └───────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Error Categories:**
- `TRANSIENT`: Rate limits, timeouts, connection errors (retry with backoff)
- `CRITICAL`: Authentication failures (stop immediately)
- `RECOVERABLE`: Tool-specific errors (mark tool as failed, continue with others)

## Session Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Session Management                        │
│                                                              │
│   ┌────────────────────────────────────────────────────┐    │
│   │                  InMemorySaver                      │    │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │    │
│   │  │ Thread: A   │  │ Thread: B   │  │ Thread: C   │ │    │
│   │  │ Messages:   │  │ Messages:   │  │ Messages:   │ │    │
│   │  │ [Q1, A1,    │  │ [Q1, A1]    │  │ [Q1, A1,    │ │    │
│   │  │  Q2, A2]    │  │             │  │  Q2, A2,    │ │    │
│   │  │             │  │             │  │  Q3, A3]    │ │    │
│   │  └─────────────┘  └─────────────┘  └─────────────┘ │    │
│   └────────────────────────────────────────────────────┘    │
│                                                              │
│   Methods:                                                   │
│   - new_session()      → Creates new thread ID               │
│   - set_thread_id()    → Resume previous session             │
│   - get_session_info() → Query count, timestamps             │
│   - list_sessions()    → All active sessions                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Module Dependencies

```
kosmo/
├── __init__.py          ─── Exports: KosmoAgent, cli_main, errors
├── __main__.py          ─── Entry point: python -m kosmo
├── agent.py             ─┬─ KosmoAgent class
│                         ├─ Imports: tools/, prompts/, errors.py
│                         └─ Uses: langgraph, langchain_openai
├── cli.py               ─── CLI interface, imports agent.py
├── errors.py            ─── Error classes, no internal dependencies
├── prompts/
│   ├── __init__.py      ─── Exports prompt functions
│   ├── system_prompt.py ─── Base ReAct prompt
│   └── cosmology_templates.py ─── Topic-specific contexts
└── tools/
    ├── __init__.py      ─── Exports: create_tools()
    ├── web_search.py    ─── Tavily API integration
    ├── code_executor.py ─── Sandboxed Python REPL
    ├── knowledge_base.py─── Wikipedia API
    └── plotter.py       ─── Matplotlib visualization
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Agent Framework | LangGraph | ReAct pattern, state management |
| LLM | OpenAI GPT-4o-mini | Reasoning and response generation |
| Web Search | Tavily API | Scientific literature search |
| Math/Physics | NumPy, SymPy, SciPy | Numerical computation |
| Visualization | Matplotlib | Plot generation |
| Memory | LangGraph InMemorySaver | Session persistence |

## Extension Points

Kosmo is designed for extensibility:

1. **New Tools**: Add to `tools/` directory, register in `create_tools()`
2. **New Topics**: Add templates to `prompts/cosmology_templates.py`
3. **New UI**: Import `KosmoAgent` and build custom interface
4. **Custom LLM**: Swap `ChatOpenAI` for other LangChain-compatible models
