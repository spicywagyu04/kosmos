# Sample Query Outputs

This document shows example outputs from the Kosmo Cosmology Research Agent for various types of queries. These examples demonstrate the agent's capabilities across different categories of cosmology questions.

## Table of Contents

1. [Basic Calculations](#basic-calculations)
2. [Orbital Mechanics](#orbital-mechanics)
3. [Research Questions](#research-questions)
4. [Cosmology Topics](#cosmology-topics)

---

## Basic Calculations

### Query: Escape Velocity from Earth

**Query:** "Calculate the escape velocity from Earth"

**Agent Response:**

```
To calculate the escape velocity from Earth, I'll use the formula:

v_escape = sqrt(2 * G * M / R)

Where:
- G = 6.674 × 10^-11 m³/(kg·s²) (gravitational constant)
- M = 5.972 × 10^24 kg (Earth's mass)
- R = 6.371 × 10^6 m (Earth's radius)

Calculation:
v_escape = sqrt(2 × 6.674×10^-11 × 5.972×10^24 / 6.371×10^6)
v_escape = sqrt(1.25 × 10^8)
v_escape ≈ 11,186 m/s ≈ 11.2 km/s

The escape velocity from Earth's surface is approximately 11.2 km/s (about 40,320 km/h or 25,000 mph). This is the minimum velocity an object needs to escape Earth's gravitational pull without further propulsion.
```

**Tools Used:** code_executor

---

### Query: Schwarzschild Radius

**Query:** "What is the Schwarzschild radius of a 10 solar mass black hole?"

**Agent Response:**

```
The Schwarzschild radius is the radius of the event horizon for a non-rotating black hole, calculated using:

Rs = 2GM/c²

Where:
- G = 6.674 × 10^-11 m³/(kg·s²)
- M = 10 × M_sun = 10 × 1.989 × 10^30 kg = 1.989 × 10^31 kg
- c = 2.998 × 10^8 m/s

Calculation:
Rs = 2 × 6.674×10^-11 × 1.989×10^31 / (2.998×10^8)²
Rs = 2.654×10^21 / 8.988×10^16
Rs ≈ 29,540 meters ≈ 29.5 km

A 10 solar mass black hole has a Schwarzschild radius of approximately 29.5 km. This means the event horizon—the boundary beyond which nothing can escape—forms a sphere about 59 km in diameter.

For reference, this scales linearly with mass: a stellar black hole with 1 solar mass would have Rs ≈ 3 km, while Sagittarius A* (4 million solar masses) has Rs ≈ 12 million km.
```

**Tools Used:** code_executor

---

### Query: Orbital Period of Mars

**Query:** "Calculate the orbital period of Mars around the Sun"

**Agent Response:**

```
Using Kepler's Third Law, the orbital period can be calculated as:

T = 2π × sqrt(a³ / (G × M))

Where:
- a = 2.279 × 10^11 m (Mars' semi-major axis, ~1.524 AU)
- G = 6.674 × 10^-11 m³/(kg·s²)
- M = 1.989 × 10^30 kg (Sun's mass)

Calculation:
T = 2π × sqrt((2.279×10^11)³ / (6.674×10^-11 × 1.989×10^30))
T = 2π × sqrt(1.184×10^34 / 1.327×10^20)
T = 2π × sqrt(8.92×10^13)
T ≈ 5.936 × 10^7 seconds

Converting to Earth years:
T = 5.936×10^7 / (365.25 × 24 × 3600)
T ≈ 1.88 Earth years ≈ 687 Earth days

Mars takes approximately 687 Earth days (1.88 Earth years) to complete one orbit around the Sun. This is longer than Earth's year due to Mars being farther from the Sun.
```

**Tools Used:** code_executor

---

## Orbital Mechanics

### Query: Hohmann Transfer to Mars

**Query:** "Simulate the trajectory of a spacecraft from Earth to Mars using a Hohmann transfer orbit"

**Agent Response:**

```
A Hohmann transfer orbit is the most fuel-efficient trajectory between two circular orbits. For Earth to Mars:

ORBITAL PARAMETERS:
- Earth orbit radius: 1.496 × 10^11 m (1.0 AU)
- Mars orbit radius: 2.279 × 10^11 m (1.524 AU)
- Transfer orbit semi-major axis: 1.888 × 10^11 m (1.262 AU)
- Transfer orbit eccentricity: 0.208

VELOCITY CALCULATIONS:
- Earth orbital velocity: 29.78 km/s
- Mars orbital velocity: 24.13 km/s
- Spacecraft velocity at Earth departure: 32.73 km/s
- Spacecraft velocity at Mars arrival: 21.48 km/s

DELTA-V REQUIREMENTS:
- Departure burn (Earth): Δv₁ = 2.95 km/s
- Arrival burn (Mars): Δv₂ = 2.65 km/s
- Total delta-v: 5.60 km/s

TRANSFER TIME:
- Transfer time: 258.8 days (~8.5 months)

This represents half of the transfer ellipse period. Launch windows occur approximately every 26 months when Earth and Mars are in the correct alignment.

[A plot showing the transfer orbit would be generated here]
```

**Tools Used:** code_executor, plotter

---

### Query: Low Earth Orbit Velocity

**Query:** "What is the orbital velocity of a satellite in low Earth orbit at 400 km altitude?"

**Agent Response:**

```
For a circular orbit, the orbital velocity is:

v = sqrt(G × M / r)

Where:
- G = 6.674 × 10^-11 m³/(kg·s²)
- M = 5.972 × 10^24 kg (Earth's mass)
- r = R_Earth + altitude = 6.371×10^6 + 400×10^3 = 6.771×10^6 m

Calculation:
v = sqrt(6.674×10^-11 × 5.972×10^24 / 6.771×10^6)
v = sqrt(5.886×10^7)
v ≈ 7,672 m/s ≈ 7.67 km/s

The orbital velocity at 400 km altitude is approximately 7.67 km/s (about 27,600 km/h).

Additional orbital parameters:
- Orbital period: T = 2π × r / v ≈ 5,544 seconds ≈ 92.4 minutes
- Orbits per day: ~15.6

This is the approximate altitude of the International Space Station (ISS), which orbits Earth about 16 times per day.
```

**Tools Used:** code_executor

---

## Research Questions

### Query: Dark Matter Evidence

**Query:** "What is dark matter and what evidence do we have for its existence?"

**Agent Response:**

```
Dark matter is a hypothetical form of matter that does not emit, absorb, or reflect electromagnetic radiation, making it invisible to telescopes. It is estimated to comprise about 27% of the universe's total mass-energy content.

EVIDENCE FOR DARK MATTER:

1. Galaxy Rotation Curves
   The most compelling evidence comes from observations of galaxy rotation. Stars at the edges of spiral galaxies orbit much faster than predicted by visible matter alone. This suggests the presence of a massive, invisible halo of dark matter surrounding galaxies.

2. Gravitational Lensing
   Light from distant galaxies is bent by massive galaxy clusters more than can be explained by visible matter. The additional gravitational lensing effect indicates unseen mass—dark matter.

3. Cosmic Microwave Background (CMB)
   Fluctuations in the CMB reveal the distribution of matter in the early universe. The pattern matches models that include cold dark matter (CDM), supporting the ΛCDM cosmological model.

4. Large-Scale Structure
   The "cosmic web" of galaxies and galaxy clusters formed under gravitational influence that requires more mass than visible matter provides.

5. Bullet Cluster
   Observations of colliding galaxy clusters show gravitational effects separated from the hot gas (visible via X-rays), directly demonstrating the presence of dark matter.

DARK MATTER CANDIDATES:
- WIMPs (Weakly Interacting Massive Particles)
- Axions
- Sterile neutrinos
- Primordial black holes

Current experiments like LUX-ZEPLIN, XENONnT, and CERN searches continue to look for direct detection of dark matter particles.
```

**Tools Used:** wikipedia, web_search

---

### Query: Gravitational Wave Detection

**Query:** "How do LIGO and Virgo detect gravitational waves?"

**Agent Response:**

```
LIGO (Laser Interferometer Gravitational-Wave Observatory) and Virgo are ground-based interferometers designed to detect ripples in spacetime caused by massive accelerating objects.

DETECTION PRINCIPLE:

Gravitational waves stretch and compress space as they pass through. LIGO uses laser interferometry to measure these tiny distortions:

1. A laser beam is split into two perpendicular arms (4 km long in LIGO, 3 km in Virgo)
2. The beams reflect off mirrors at the ends of each arm
3. The beams recombine at the detector
4. When arms are equal length, the beams destructively interfere (no signal)
5. A passing gravitational wave changes the relative arm lengths
6. This causes partial constructive interference, producing a measurable signal

SENSITIVITY:

LIGO can detect length changes of about 10^-19 meters—one ten-thousandth the diameter of a proton. This incredible sensitivity requires:

- Ultra-high vacuum in the beam tubes
- Seismic isolation systems
- Highly reflective mirrors suspended as pendulums
- Precise laser stabilization
- Multiple detectors for signal confirmation

NOTABLE DETECTIONS:

- GW150914 (2015): First direct detection, two merging black holes
- GW170817 (2017): First neutron star merger with electromagnetic counterpart
- Multiple black hole and neutron star mergers since then

The network now includes LIGO (Louisiana & Washington), Virgo (Italy), and KAGRA (Japan), enabling better source localization through triangulation.
```

**Tools Used:** wikipedia, web_search

---

## Cosmology Topics

### Query: CMB Temperature

**Query:** "What is the temperature of the cosmic microwave background and why is it significant?"

**Agent Response:**

```
The cosmic microwave background (CMB) has a temperature of approximately 2.725 K (-270.425°C or -454.765°F).

ORIGIN AND SIGNIFICANCE:

The CMB is the thermal radiation left over from the early universe, released about 380,000 years after the Big Bang during the epoch of recombination. At this time, the universe cooled enough for electrons and protons to combine into neutral hydrogen, allowing photons to travel freely through space.

KEY PROPERTIES:

1. Nearly Perfect Blackbody
   The CMB follows a perfect blackbody spectrum to remarkable precision, confirming it originated from thermal equilibrium in the early universe.

2. Temperature Anisotropies
   Tiny variations (~10^-5 K) in the CMB temperature reveal density fluctuations in the early universe that seeded galaxy formation.

3. Cosmological Parameters
   Analysis of CMB anisotropies (by COBE, WMAP, and Planck satellites) has determined:
   - Age of the universe: 13.8 billion years
   - Hubble constant: ~67.4 km/s/Mpc
   - Matter content: ~5% ordinary, ~27% dark matter, ~68% dark energy
   - Spatial curvature: nearly flat

4. Original Temperature
   When released, the CMB had a temperature of ~3000 K. The expansion of the universe has stretched (redshifted) these photons by a factor of ~1100, cooling them to their current microwave wavelengths.

The CMB is often called the "afterglow of the Big Bang" and provides our deepest observable window into the early universe.
```

**Tools Used:** wikipedia

---

### Query: Hubble Tension

**Query:** "What is the Hubble constant and why is there tension in its measurements?"

**Agent Response:**

```
The Hubble constant (H₀) describes the rate at which the universe is expanding. It relates the recession velocity of galaxies to their distance: v = H₀ × d.

CURRENT VALUES:

The "Hubble tension" refers to a significant discrepancy between two measurement methods:

1. Early Universe Measurements (CMB-based)
   Using Planck satellite observations of the cosmic microwave background and the ΛCDM model:
   H₀ = 67.4 ± 0.5 km/s/Mpc

2. Local Universe Measurements (Distance Ladder)
   Using Cepheid variables and Type Ia supernovae:
   H₀ = 73.0 ± 1.0 km/s/Mpc (SH0ES collaboration)

THE TENSION:

The ~9% difference (about 5σ statistical significance) is too large to attribute to measurement errors alone. This suggests either:

1. Systematic Errors
   Unidentified issues with one or both measurement methods

2. New Physics
   The standard ΛCDM cosmological model may be incomplete. Proposed modifications include:
   - Early dark energy
   - Modified gravity theories
   - Additional relativistic species
   - Interacting dark matter/dark energy

RECENT DEVELOPMENTS:

- James Webb Space Telescope observations have confirmed the Cepheid distance measurements
- Alternative distance indicators (tip of the red giant branch) give intermediate values
- The tension persists and remains one of cosmology's most pressing puzzles

Resolution of the Hubble tension could reveal fundamental new physics beyond our current understanding of the universe.
```

**Tools Used:** wikipedia, web_search

---

### Query: Age of the Universe

**Query:** "Calculate the age of the universe given a Hubble constant of 70 km/s/Mpc"

**Agent Response:**

```
The simplest estimate for the age of the universe is the Hubble time, calculated as:

t_H = 1 / H₀

UNIT CONVERSION:
First, convert H₀ to SI units:
- H₀ = 70 km/s/Mpc
- 1 Mpc = 3.086 × 10^19 km

H₀ = 70 / (3.086 × 10^19) = 2.268 × 10^-18 s^-1

HUBBLE TIME:
t_H = 1 / H₀ = 1 / (2.268 × 10^-18)
t_H = 4.41 × 10^17 seconds

CONVERTING TO YEARS:
t_H = 4.41 × 10^17 / (3.156 × 10^7 s/yr)
t_H ≈ 13.97 billion years

IMPORTANT CAVEATS:

The Hubble time is only an approximation. The actual age depends on the universe's expansion history:

1. In a matter-dominated universe: t = (2/3) × t_H
2. In our dark-energy-dominated universe: t ≈ 0.96 × t_H

Using the current ΛCDM model with H₀ = 70 km/s/Mpc:
- Actual age ≈ 13.4 billion years

The Planck satellite's best estimate (using H₀ = 67.4 km/s/Mpc) gives:
- Age = 13.8 ± 0.02 billion years

The universe's age is approximately 13.8 billion years, though the exact value depends on the measured Hubble constant.
```

**Tools Used:** code_executor

---

## Running These Examples

To run these sample queries yourself:

```python
from examples.sample_queries import run_query, get_query_by_name

# Run a specific query
query = get_query_by_name("escape_velocity")
response = run_query(query)
print(response)

# Or run with a custom query
from kosmo import KosmoAgent
agent = KosmoAgent(verbose=True)
response = agent.query("What is the mass of the Sun?")
```

See [sample_queries.py](sample_queries.py) for the full catalog of example queries.
