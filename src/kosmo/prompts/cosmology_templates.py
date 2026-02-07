"""Cosmology-specific prompt templates for specialized topics."""

from typing import Optional

# Topic-specific context that can be appended to queries for deeper domain expertise

DARK_MATTER_CONTEXT = """
## Dark Matter Expertise Context
When addressing dark matter questions, consider:

### Key Concepts
- Cold Dark Matter (CDM) vs Warm Dark Matter (WDM) vs Hot Dark Matter
- WIMP (Weakly Interacting Massive Particles) candidates
- Axions and other theoretical particles
- Modified Newtonian Dynamics (MOND) as alternative theory
- Dark matter halos and galactic rotation curves

### Important Equations
- Rotation curve: v(r) = sqrt(G * M(r) / r)
- Virial theorem for galaxy clusters: 2K + U = 0
- NFW density profile: ρ(r) = ρ_s / ((r/r_s)(1 + r/r_s)²)
- Dark matter density: Ω_DM ≈ 0.27 (fraction of critical density)

### Current Research Areas
- Direct detection experiments (LUX-ZEPLIN, XENONnT, PandaX)
- Indirect detection (gamma rays, neutrinos from annihilation)
- Collider searches at CERN
- Gravitational lensing surveys
- Bullet Cluster as key evidence

### Key Values
- Local dark matter density: ~0.3 GeV/cm³
- Dark matter to baryon ratio: ~5:1
- Typical WIMP mass range: 10-1000 GeV/c²
"""

EXOPLANET_CONTEXT = """
## Exoplanet Expertise Context
When addressing exoplanet questions, consider:

### Detection Methods
- Transit photometry: ΔF/F = (R_p/R_*)²
- Radial velocity: K = (2πG/P)^(1/3) * (M_p sin i) / (M_* + M_p)^(2/3)
- Direct imaging
- Gravitational microlensing
- Astrometry

### Key Concepts
- Habitable zone boundaries (inner and outer)
- Planetary equilibrium temperature: T_eq = T_* * sqrt(R_*/(2a)) * (1-A)^(1/4)
- Atmospheric characterization via transmission spectroscopy
- Hot Jupiters, super-Earths, mini-Neptunes classifications
- Tidal locking and orbital resonances

### Important Equations
- Kepler's Third Law: P² = (4π²/GM) * a³
- Hill sphere radius: r_H = a * (M_p/(3M_*))^(1/3)
- Roche limit: d = R_M * (2 * ρ_M/ρ_m)^(1/3)
- Surface gravity: g = GM/R²

### Current Missions and Data Sources
- Kepler/K2 mission archive
- TESS (Transiting Exoplanet Survey Satellite)
- James Webb Space Telescope (JWST) for atmospheric studies
- CHEOPS mission
- Nancy Grace Roman Space Telescope (upcoming)

### Key Statistics
- Over 5,500 confirmed exoplanets (as of 2024)
- Most common: mini-Neptunes and super-Earths
- Nearest known exoplanet: Proxima Centauri b (4.24 ly)
"""

CMB_CONTEXT = """
## Cosmic Microwave Background Expertise Context
When addressing CMB questions, consider:

### Key Concepts
- Blackbody radiation at T = 2.725 K
- Recombination epoch at z ≈ 1100 (379,000 years after Big Bang)
- Temperature anisotropies: ΔT/T ~ 10⁻⁵
- Acoustic oscillations in primordial plasma
- Silk damping at small scales
- Polarization: E-modes and B-modes

### Power Spectrum Analysis
- Angular power spectrum: C_l
- Multipole expansion: l = 180°/θ
- First acoustic peak at l ≈ 220 (θ ≈ 1°)
- Baryon acoustic oscillations (BAO)

### Important Equations
- Wien's law: λ_max = b/T (b = 2.898 × 10⁻³ m·K)
- Stefan-Boltzmann: P = σT⁴
- CMB photon number density: n_γ ≈ 411 photons/cm³
- Photon-to-baryon ratio: η ≈ 6 × 10⁻¹⁰

### Cosmological Parameters from CMB
- Hubble constant: H₀ ≈ 67.4 km/s/Mpc (Planck 2018)
- Age of universe: 13.8 billion years
- Baryon density: Ω_b h² ≈ 0.0224
- Dark matter density: Ω_c h² ≈ 0.120
- Dark energy density: Ω_Λ ≈ 0.685
- Curvature: Ω_k ≈ 0 (flat universe)
- Spectral index: n_s ≈ 0.965

### Key Experiments
- COBE (first detection of anisotropies, 1992)
- WMAP (precision measurements, 2001-2010)
- Planck satellite (highest resolution, 2009-2013)
- Ground-based: ACT, SPT, BICEP/Keck
- Future: CMB-S4, LiteBIRD
"""

# Keywords for topic detection
DARK_MATTER_KEYWORDS = [
    "dark matter", "dark-matter", "wimp", "axion", "cdm", "cold dark",
    "warm dark", "hot dark", "mond", "modified newtonian", "rotation curve",
    "galactic halo", "dark halo", "nfw profile", "lux-zeplin", "xenon",
    "dark sector", "missing mass", "bullet cluster"
]

EXOPLANET_KEYWORDS = [
    "exoplanet", "extrasolar planet", "transit", "radial velocity",
    "habitable zone", "goldilocks", "hot jupiter", "super-earth",
    "super earth", "mini-neptune", "mini neptune", "kepler mission",
    "tess", "habitability", "biosignature", "transit spectroscopy",
    "planet detection", "alien planet", "proxima b", "trappist"
]

CMB_KEYWORDS = [
    "cmb", "cosmic microwave background", "microwave background",
    "planck satellite", "wmap", "cobe", "recombination", "last scattering",
    "acoustic peak", "power spectrum", "anisotropy", "anisotropies",
    "b-mode", "e-mode", "polarization", "primordial", "2.725",
    "blackbody radiation", "bao", "baryon acoustic"
]


def detect_topic(query: str) -> Optional[str]:
    """Detect the cosmology topic from a query.

    Args:
        query: The user's query string

    Returns:
        Topic name ('dark_matter', 'exoplanet', 'cmb') or None if no specific topic
    """
    query_lower = query.lower()

    # Count keyword matches for each topic
    dark_matter_matches = sum(1 for kw in DARK_MATTER_KEYWORDS if kw in query_lower)
    exoplanet_matches = sum(1 for kw in EXOPLANET_KEYWORDS if kw in query_lower)
    cmb_matches = sum(1 for kw in CMB_KEYWORDS if kw in query_lower)

    # Return the topic with most matches, if any
    max_matches = max(dark_matter_matches, exoplanet_matches, cmb_matches)

    if max_matches == 0:
        return None

    if dark_matter_matches == max_matches:
        return "dark_matter"
    elif exoplanet_matches == max_matches:
        return "exoplanet"
    else:
        return "cmb"


def get_topic_context(topic: str) -> str:
    """Get the specialized context for a given topic.

    Args:
        topic: Topic name ('dark_matter', 'exoplanet', 'cmb')

    Returns:
        The topic-specific context string
    """
    contexts = {
        "dark_matter": DARK_MATTER_CONTEXT,
        "exoplanet": EXOPLANET_CONTEXT,
        "cmb": CMB_CONTEXT,
    }
    return contexts.get(topic, "")


def enhance_prompt_for_topic(base_prompt: str, query: str) -> str:
    """Enhance a prompt with topic-specific context if applicable.

    Args:
        base_prompt: The base system prompt
        query: The user's query to analyze

    Returns:
        Enhanced prompt with topic context appended if a topic is detected
    """
    topic = detect_topic(query)

    if topic is None:
        return base_prompt

    context = get_topic_context(topic)
    return f"{base_prompt}\n{context}"
