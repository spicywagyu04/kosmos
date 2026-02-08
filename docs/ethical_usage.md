# Ethical Usage Guidelines and Simulation Disclaimers

This document outlines important considerations for the ethical use of Kosmo and provides critical disclaimers regarding the accuracy and reliability of its outputs.

## Table of Contents

1. [Purpose and Scope](#purpose-and-scope)
2. [Simulation Disclaimers](#simulation-disclaimers)
3. [Ethical Usage Guidelines](#ethical-usage-guidelines)
4. [Data Sources and Citations](#data-sources-and-citations)
5. [Limitations](#limitations)
6. [Best Practices](#best-practices)

---

## Purpose and Scope

Kosmo is an **educational and research exploration tool** designed to:

- Help students and enthusiasts learn about cosmology and astrophysics concepts
- Assist researchers with preliminary calculations and literature exploration
- Demonstrate AI-powered scientific reasoning and tool orchestration
- Provide a starting point for further investigation using authoritative sources

Kosmo is **NOT** intended for:

- Mission-critical spacecraft navigation or trajectory planning
- Peer-reviewed scientific publications without independent verification
- Safety-critical engineering decisions
- Real-time astronomical observations or predictions

---

## Simulation Disclaimers

### Accuracy of Calculations

While Kosmo uses established physics equations and constants, users should be aware of the following:

1. **Simplified Models**: Many calculations use idealized models that may not account for:
   - Gravitational perturbations from multiple bodies
   - Relativistic effects in high-gravity or high-velocity scenarios
   - Atmospheric drag and solar radiation pressure
   - Real-world mission constraints and uncertainties

2. **Physical Constants**: The physical constants used (G, c, solar masses, etc.) are approximate values suitable for educational purposes. For precision work, consult authoritative sources such as:
   - CODATA recommended values (NIST)
   - IAU nominal values for solar and planetary parameters
   - NASA JPL ephemeris data

3. **Orbital Mechanics Limitations**: The Hohmann transfer and Kepler orbit calculations assume:
   - Two-body problems (central body + orbiting object)
   - Circular or elliptical orbits in the same plane
   - Instantaneous impulsive maneuvers
   - No fuel constraints or spacecraft mass changes

4. **No Warranty**: All calculations are provided "as-is" without warranty of any kind. The developers are not responsible for any consequences arising from the use of Kosmo's outputs.

### Verification Recommendations

For any calculation that will be used beyond educational exploration:

- **Cross-reference** results with established tools (e.g., NASA GMAT, STK, SPICE)
- **Consult** peer-reviewed literature and textbooks
- **Validate** against known benchmark values
- **Seek expert review** for mission-critical applications

---

## Ethical Usage Guidelines

### Responsible AI Use

1. **Transparency**: When presenting Kosmo-generated content in academic or professional contexts, clearly indicate that the content was generated with AI assistance.

2. **Critical Evaluation**: Do not accept AI-generated answers uncritically. Always:
   - Verify claims against authoritative sources
   - Check mathematical calculations independently
   - Question unusual or unexpected results

3. **Academic Integrity**: If using Kosmo for educational assignments:
   - Follow your institution's AI usage policies
   - Cite AI assistance appropriately
   - Use it as a learning tool, not a replacement for understanding

### Data Privacy

1. **Query Content**: Queries you submit may be processed by third-party LLM providers (e.g., OpenAI). Avoid including:
   - Personal identifiable information
   - Confidential research data
   - Proprietary or sensitive information

2. **API Keys**: Keep your API keys secure and never share them publicly.

### Environmental Considerations

AI systems require computational resources. To minimize environmental impact:

- Use Kosmo efficiently by formulating clear, specific queries
- Avoid unnecessary repeated queries for the same information
- Consider the carbon footprint of AI-powered tools in your research practices

---

## Data Sources and Citations

### Information Sources

Kosmo retrieves information from various sources:

1. **Web Search (Tavily)**: Searches the public web, including:
   - arXiv preprints (not peer-reviewed)
   - NASA and ESA public data
   - Educational institution websites
   - News articles and press releases

2. **Wikipedia**: Provides general scientific knowledge. While Wikipedia strives for accuracy, it:
   - May contain errors or outdated information
   - Should not be cited as a primary source
   - Is best used as a starting point for further research

3. **LLM Knowledge**: The underlying language model has a knowledge cutoff date and may:
   - Lack information about recent discoveries
   - Occasionally generate incorrect or hallucinated information
   - Reflect biases present in training data

### Citation Requirements

When using information from Kosmo:

- **Always verify** key facts and figures against primary sources
- **Cite original sources** rather than Kosmo itself
- **Acknowledge AI assistance** in your methodology when appropriate
- **Do not cite** Kosmo outputs as authoritative scientific references

---

## Limitations

### Technical Limitations

1. **Code Execution Sandbox**: The Python execution environment has limited libraries and cannot:
   - Access the internet
   - Read or write files
   - Install additional packages
   - Run long-duration computations

2. **LLM Constraints**: The AI agent may:
   - Misunderstand complex or ambiguous queries
   - Make errors in multi-step reasoning
   - Fail to use the optimal tool for a given task
   - Generate plausible-sounding but incorrect information

3. **Tool Availability**: External tools (web search, Wikipedia) depend on:
   - Internet connectivity
   - Third-party API availability and rate limits
   - Data freshness and completeness

### Domain Limitations

Kosmo is optimized for cosmology and astrophysics topics. It may provide less reliable results for:

- Quantum mechanics and particle physics details
- Cutting-edge theoretical physics
- Specific spacecraft engineering problems
- Interdisciplinary topics outside physics

---

## Best Practices

### For Students

1. Use Kosmo to **explore concepts** and build intuition
2. **Work through calculations** yourself after seeing the approach
3. Ask **follow-up questions** to deepen understanding
4. Compare results with **textbook examples**
5. Discuss interesting findings with **instructors**

### For Researchers

1. Use Kosmo for **preliminary exploration** and literature discovery
2. **Validate all calculations** independently before publication
3. **Cite primary sources** discovered through Kosmo searches
4. Consider Kosmo as a **research assistant**, not an authority
5. Report any **systematic errors** you discover to help improve the tool

### For Educators

1. Use Kosmo to **generate practice problems** and examples
2. Demonstrate **AI-assisted learning** while teaching critical evaluation
3. Discuss **AI limitations** as part of scientific literacy education
4. Encourage students to **verify and question** AI-generated content
5. Establish clear **policies** for AI use in your courses

---

## Contact and Feedback

If you discover errors, have concerns about ethical implications, or want to suggest improvements:

- Open an issue on the project's GitHub repository
- Include specific examples and expected correct values when reporting errors
- Provide constructive feedback to help improve the tool for everyone

---

*Last updated: February 2026*

*Kosmo - Cosmology Research Agent*
