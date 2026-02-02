# wyscout-entropy

**Entropy-based striker scouting from Wyscout event data**

`wyscout-entropy` is a Python package for scouting attacking players—especially strikers—using
**shot entropy, spatial entropy, and unscaled xG-adjusted metrics** derived from Wyscout JSON event data.

The goal is not to replace xG, but to **add context and repeatability**:
- *How* is a player generating xG?
- Is their production driven by **repeatable patterns** or **high-variance shot profiles**?
- How portable is their scoring output across teams and systems?

---

## Core ideas (plain English)

- **Shot entropy** → variety of chances
- **Spatial entropy** → variety of shot locations
- **Type entropy** → variety of shot types
- **Stability (unscaled)** → share of xG coming from low-entropy, repeatable patterns
- **xG adjusted (unscaled)** → xG weighted by stability
- **xG adjusted %** → literal share of xG from trusted patterns (no rescaling)

> ⚠️ This package uses **unscaled** metrics by design.  
> Percentages are *literal proportions*, not indices.

---

## What this package is for

✅ Scouting strikers  
✅ Identifying fox-in-the-box profiles  
✅ Flagging volatile, high-entropy seasons  
✅ Comparing players across leagues or teams  
✅ Buy-low / regression-risk analysis  

❌ Measuring finishing technique directly  
❌ Predicting goals on its own  
❌ Tactical evaluation of team buildup  

---

## Installation

### Local development install
```bash
pip install -e .
