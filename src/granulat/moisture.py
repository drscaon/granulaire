"""Per-grain moisture model.

Four discrete states, exported as an OpenUSD *variant set* "moisture" on
every grain prototype. Each grain in the scene selects its own state: dry and
wet grains can be mixed in one heap, and the state of one grain (or all of
them) can be switched in usdview / Omniverse without regenerating.

What a state changes:

1. Mass - grain water = absorbed water + surface film:
     m_water = absorption * saturation(state) * m_dry
             + rho_water * area * film_thickness(state)
   The film scales with surface area, so it weighs a lot on sand (high
   surface-to-volume ratio) and little on gravel. For a 0.35 mm sand grain a
   20 um film is ~13 % of the dry mass, the order of magnitude of the water
   content of wet sand; for an 8 mm gravel grain, under 1 %.
   This is a per-grain share of the water in a heap, not a measurement.
   The film is capped by the water the pores of a heap can hold
   (porosity n ~ 0.38): w_max = n/(1-n) * rho_water/rho_grain, ~23 % for
   quartz, times the fill ratio of the state. Without that cap, very fine
   sand would hold more water than a saturated heap.
2. Appearance - a wet grain is darker and glossier: lower, slightly more
   saturated albedo, lower roughness, rising clearcoat. One UsdPreviewSurface
   material per prototype and per state.
3. Contact - friction and restitution through one UsdPhysics material per
   state. Capillary cohesion (liquid bridges between grains) has no standard
   UsdPhysics schema: it is written to the custom attribute
   granulat:capillaryCohesion (Pa), for a solver or script that can read it.
   It peaks in the damp state, is zero when dry or saturated, and decreases
   with grain size.

Contact and cohesion coefficients are indicative values to be calibrated:
they are exactly what a "sand on the ramp" test should measure.
"""

import numpy as np

RHO_WATER = 1000.0  # kg/m3
POROSITY = 0.38  # typical heap porosity, used to cap the film

# order: driest to wettest
STATES = ["dry", "damp", "wet", "saturated"]
LABELS = {"dry": "Dry", "damp": "Damp", "wet": "Wet", "saturated": "Saturated"}

STATE_PARAMS = {
    # film: thickness (m); sat: fraction of the grain's own pores filled;
    # fill: fraction of the heap's pore water (film cap); albedo, rough, coat:
    # appearance; mu, e: friction and restitution multipliers;
    # cohesion: capillary cohesion (Pa) for a 0.35 mm grain
    "dry": dict(
        film=0.0, sat=0.0, fill=0.0, albedo=1.00, rough=0.85, coat=0.0, mu=1.00, e=1.00, cohesion=0.0
    ),
    "damp": dict(
        film=5e-6, sat=0.3, fill=0.2, albedo=0.80, rough=0.60, coat=0.2, mu=1.10, e=0.60, cohesion=2000.0
    ),
    "wet": dict(
        film=20e-6, sat=0.8, fill=0.7, albedo=0.60, rough=0.30, coat=0.6, mu=1.00, e=0.40, cohesion=1000.0
    ),
    "saturated": dict(
        film=35e-6, sat=1.0, fill=1.0, albedo=0.50, rough=0.15, coat=1.0, mu=0.80, e=0.30, cohesion=0.0
    ),
}
COHESION_REF_D = 0.35e-3  # m: reference diameter of the cohesion values above

DEFAULT_WEIGHTS = "40,30,20,10"


def water_mass(state, dry_mass, area, absorption, density):
    p = STATE_PARAMS[state]
    absorbed = absorption * p["sat"] * dry_mass
    film = RHO_WATER * area * p["film"]
    w_max = POROSITY / (1 - POROSITY) * RHO_WATER / density
    return absorbed + min(film, p["fill"] * w_max * dry_mass)


def wet_color(color, state):
    """Darken and slightly saturate the dry colour."""
    p = STATE_PARAMS[state]
    c = np.asarray(color, dtype=float) * p["albedo"]
    grey = c.mean()
    sat_boost = 1.0 + 0.3 * (1.0 - p["albedo"])
    return tuple(np.clip(grey + (c - grey) * sat_boost, 0.0, 1.0))


def cohesion(state, diameter_m):
    return STATE_PARAMS[state]["cohesion"] * COHESION_REF_D / diameter_m


def parse_weights(text):
    """ "40,30,20,10" -> normalised weight per state (dry, damp, wet, saturated)."""
    vals = [float(v) for v in text.split(",")]
    if len(vals) != len(STATES) or sum(vals) <= 0 or min(vals) < 0:
        raise ValueError("expected 4 non-negative weights: dry,damp,wet,saturated")
    total = sum(vals)
    return {s: v / total for s, v in zip(STATES, vals, strict=True)}
