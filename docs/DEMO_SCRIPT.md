# Demo Recording Script

This document provides a script for recording the Kosmo Cosmology Research Agent demo screencast/GIF.

## Recording Setup

### Prerequisites
- Terminal with dark theme (recommended for visibility)
- API keys configured in `.env` file
- Virtual environment activated
- Screen recording software (e.g., asciinema, OBS, or macOS screen recording)

### Recommended Settings
- Terminal size: 120x30 characters
- Font size: 14-16pt for readability
- Clear terminal before starting: `clear`

## Demo Script

### 1. Introduction (5 seconds)
```bash
# Show the project directory
ls -la
```

### 2. Installation Demo (10 seconds)
```bash
# Show that kosmo is installed
pip show kosmo
```

### 3. Help Command (5 seconds)
```bash
# Display available options
kosmo --help
```

Expected output:
```
usage: kosmo [-h] [-q QUERY] [-v] [--no-memory]

Kosmo - Cosmology Research Agent

options:
  -h, --help            show this help message and exit
  -q QUERY, --query QUERY
                        Run a single query and exit
  -v, --verbose         Show detailed agent reasoning steps
  --no-memory           Disable session memory
```

### 4. Single Query Demo - Calculation (15 seconds)
```bash
# Calculate escape velocity
kosmo -q "Calculate the escape velocity from Earth"
```

Expected response highlights:
- Agent uses code executor tool
- Shows calculation: v = sqrt(2GM/R)
- Returns ~11.2 km/s

### 5. Single Query Demo - Orbital Mechanics (20 seconds)
```bash
# Hohmann transfer calculation
kosmo -q "Calculate the Hohmann transfer orbit from Earth to Mars" -v
```

Expected response highlights:
- Verbose mode shows Thought-Action-Observation cycle
- Uses code executor for calculations
- Shows delta-v requirements
- May generate orbital plot

### 6. Interactive Mode Demo (30 seconds)
```bash
# Start interactive mode
kosmo
```

Then type these queries:
```
> What is the Schwarzschild radius of a 10 solar mass black hole?
```

Wait for response, then:
```
> Can you also calculate for 100 solar masses?
```

Shows session memory maintaining context.

### 7. Exit Demo (5 seconds)
```
> exit
```

Or press `Ctrl+C`

## Recording Tips

1. **Pace**: Type slowly enough for viewers to read
2. **Pauses**: Wait for responses to complete before typing next command
3. **Errors**: If an error occurs, it's okay - the agent handles errors gracefully
4. **API Latency**: Real API calls may take a few seconds; this is normal

## Post-Processing

### For GIF Creation
- Use tools like `gifsicle` or `ffmpeg` to convert video to GIF
- Recommended: 10-15 fps for terminal recordings
- Consider speed-up for longer operations (1.5x-2x)

### For Asciinema
```bash
# Record with asciinema
asciinema rec demo.cast

# Convert to GIF using agg
agg demo.cast demo.gif
```

## Sample Terminal Session

Below is a sample of what the demo should look like:

```
$ kosmo -q "Calculate escape velocity from Earth" -v

🔭 Kosmo - Cosmology Research Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Query: Calculate escape velocity from Earth

Thought: I need to calculate the escape velocity from Earth using the formula
v = sqrt(2GM/R). I'll use the code executor with the physics constants.

Action: code_executor
import numpy as np

# Physical constants
G = 6.67430e-11  # gravitational constant (m³/kg/s²)
M_earth = 5.972e24  # Earth mass (kg)
R_earth = 6.371e6  # Earth radius (m)

# Escape velocity formula: v = sqrt(2GM/R)
v_escape = np.sqrt(2 * G * M_earth / R_earth)
v_escape_km_s = v_escape / 1000

print(f"Escape velocity from Earth: {v_escape_km_s:.2f} km/s")

Observation: Escape velocity from Earth: 11.19 km/s

Final Answer: The escape velocity from Earth is approximately 11.2 km/s.

This is calculated using the formula v = √(2GM/R), where:
- G = 6.674 × 10⁻¹¹ m³/(kg·s²) (gravitational constant)
- M = 5.972 × 10²⁴ kg (Earth's mass)
- R = 6.371 × 10⁶ m (Earth's radius)

This means any object must reach at least 11.2 km/s (about 40,320 km/h or
25,000 mph) to escape Earth's gravitational pull without further propulsion.
```

## File Locations

After recording, place the demo files in:
- `docs/demo.gif` - Animated GIF for README
- `docs/demo.mp4` - Full video (optional)
- Link in README.md under a "Demo" section
