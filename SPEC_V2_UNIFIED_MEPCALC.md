# MEPCalc V2 — Unified Preconstruction Platform Spec

## What Changes from V1

V1: Five standalone HTML files. Each works independently. No shared state. Five separate experiences that happen to share a logo.

V2: One site, one project context, five tools that work alone OR together. A preconstruction director working a pursuit enters project info once and flows between tools. A random Google searcher lands on one tool and uses it without knowing the others exist.

**Nothing breaks.** Every tool still loads independently, works offline, prints clean, exports CSV. The change is additive — shared state layered on top of standalone tools.

---

## Architecture

### Shared Project State

A single JavaScript object stored in localStorage:

```
mepcalc_project = {
  name: "Sunrise Senior Living Phase 2",
  number: "2026-0142",
  date: "04/01/2026",
  preparedBy: "Preconstruction Team",
  buildingType: "senior-living",
  sqft: 85000,
  location: "1.07",          // location cost factor
  locationLabel: "Delaware / Wilmington",
  quality: "standard",
  duration: 16,              // months
  totalCost: null,           // populated by ROM estimator output
  mepCost: null,             // populated by ROM estimator output
  mepPct: null               // populated by ROM estimator output
}
```

### How It Flows

Each tool reads from `mepcalc_project` on load. If the object exists, it pre-fills inputs. If it doesn't exist, the tool works exactly as V1 — empty inputs, user fills them in.

Each tool writes back to `mepcalc_project` when the user changes relevant fields. Changes propagate when you navigate to the next tool.

**No framework. No build step. No API. Just localStorage and a shared 200-line `mepcalc-core.js` file that every tool includes.**

### Core.js Responsibilities

1. Read/write `mepcalc_project` from localStorage
2. Render the shared project bar (appears at top of every tool when a project exists)
3. Provide the "Continue to..." navigation between tools
4. Handle URL parameter import (for share links — overrides localStorage)
5. Nothing else. No router, no state management library, no abstractions.

---

## The Project Bar

When a project exists in state, every tool shows a thin bar below the header:

```
[Project: Sunrise Senior Living Phase 2  |  85,000 SF  |  Senior Living  |  Wilmington, DE  |  Edit]
```

- Always visible, never intrusive
- "Edit" opens the project info panel (same fields, updates state)
- Clicking the project name links back to the landing page
- If no project exists, the bar doesn't render — tool works standalone

---

## Tool-to-Tool Flow

### ROM Estimator → General Conditions
ROM output: total construction cost estimate, MEP cost, duration estimate.
General Conditions reads: project cost (pre-fills the cost field), duration (pre-fills months).
**User action:** "Continue to General Conditions →" button appears below ROM results.

### ROM Estimator → Plenum Space
ROM knows the building type. Plenum calculator uses building type to pre-select typical MEP systems:
- Senior living: enable medical gas, chilled water piping
- Healthcare: enable medical gas, chilled water, exhaust ductwork
- Industrial: disable branch duct, medical gas, chilled water
- Office: default set (as V1)
**User action:** "Check Plenum Feasibility →" button.

### ROM Estimator → Scope Gap Matrix
Building type pre-filters the scope gap items to show the most relevant ones first.
- Healthcare projects: surface medical gas piping scope gaps, nurse call, isolation room items
- Education: surface lab exhaust, kitchen hood items
**User action:** "Build Scope Gap Matrix →" button.

### General Conditions → ROM Estimator
If user enters a total cost in Gen Conditions first (before using ROM), that cost feeds back to ROM as an override.

### Any Tool → Any Tool
The project bar includes quick links to all five tools. Clicking any link carries the current project state.

---

## New Feature: Bid Leveling Mode (Scope Gap Matrix)

### The Problem
The current matrix assigns one responsible party per item. In practice, a preconstruction director has 3-5 sub bids per trade. Each sub includes/excludes different items. The actual work is comparing what's in vs out across bidders.

### The Solution
Add a "Bid Leveling" toggle to the Scope Gap Matrix. When enabled:

- Each scope item shows columns for up to 5 subcontractors (user-named)
- Per sub, per item: Included / Excluded / Silent / Clarify
- Color coding: green (included), red (excluded), yellow (silent — the dangerous one)
- Summary row per sub: "Sub A includes 62 of 76 items, excludes 4, silent on 10"
- Auto-flag: items where one sub includes but another excludes = scope gap risk
- Export includes the full bid leveling comparison

### Data Model
Same scope items. The `responsible party` dropdown becomes a secondary field. The primary view is the bid comparison grid.

### Why This Matters
This is the tool that goes from "useful reference" to "I use this every bid day." Bid leveling is the single most time-consuming preconstruction task for MEP coordination. No free tool does it.

---

## New Tool: Healthcare/Senior Living MEP Cost Adder (Tool 7)

### What It Does
Starts from a base commercial MEP $/SF (pulled from ROM estimator if project exists), then adds line-item cost premiums for healthcare/senior living requirements.

### Adder Line Items (each editable, with default $/SF):

**Medical Systems**
- Medical gas systems (O2, vacuum, medical air): $3-8/SF
- Nurse call system: $2-5/SF
- Telemetry/patient monitoring infrastructure: $1-3/SF

**HVAC Upgrades**
- ASHRAE 170 ventilation rates (vs standard ASHRAE 62.1): $4-10/SF
- Negative pressure isolation rooms (per room): $15,000-25,000 each
- Operating room HVAC (laminar flow, redundancy): $80-150/SF of OR
- Kitchen/dietary exhaust and makeup air: $3-6/SF of kitchen area

**Electrical Upgrades**
- Emergency generator upsizing (life safety + critical): $3-8/SF
- Redundant power distribution (dual utility feeds, ATS): $2-5/SF
- Enhanced fire alarm (voice evacuation, area of refuge): $1.50-3/SF

**Plumbing/Fire Protection Upgrades**
- Enhanced domestic hot water (high-demand senior living): $1-3/SF
- Anti-scald mixing valves (code requirement): $0.50-1.50/SF
- Upgraded fire protection (quick-response heads, smoke control): $1-2/SF

### Output
- Base commercial MEP $/SF (from ROM or user input)
- Total adder $/SF
- Healthcare premium as % above commercial baseline
- Total healthcare MEP $/SF
- Applied to project SF for total healthcare MEP budget

### Why This Targets the Contact
She does senior living, education, healthcare. This tool speaks her language — it quantifies exactly what makes healthcare MEP more expensive than commercial, line by line. Every preconstruction team debates these adders on every healthcare pursuit. No free tool itemizes them.

---

## New Tool: MEP System Rough Sizing (Tool 6)

### What It Does
Quick preconstruction feasibility: given building type, SF, and climate zone, estimate key MEP system sizes using published rules of thumb.

### Outputs (all showing the rule of thumb used):

**Mechanical**
- Cooling load: tons (rule: tons/SF by building type, adjusted for climate)
- Heating load: MBH (rule: BTU/SF by building type and climate zone)
- Recommended system type(s) for building type and size

**Electrical**
- Electrical service size: amps at 480V (rule: watts/SF by building type)
- Emergency generator size: kW (rule: % of total load for life safety + optional standby)
- Number of panels/distribution boards (rule: circuits per SF)

**Plumbing**
- Domestic water demand: GPM (rule: GPM/fixture unit, estimated fixture count by building type)
- Hot water generation: gallons and recovery rate

**Fire Protection**
- System type recommendation (wet/dry/pre-action based on building use and climate)
- Fire pump: required or not (based on building height and water pressure assumptions)
- Rough head count (rule: 1 head per 130-200 SF depending on hazard)

**Space Requirements**
- Main mechanical room: SF (rule: % of building SF by system type)
- Main electrical room: SF (links to NEC calculator for detailed sizing)
- Vertical shaft space: SF per floor for risers

### Why This Exists
This is the first tool a preconstruction team reaches for on a new pursuit. Before cost — before scope gaps — before general conditions — they need to know: "How big are the systems? What are we dealing with?" The answer determines everything downstream.

---

## Landing Page V2

The landing page becomes a starting point, not just an index.

### Two Entry Paths

**Path 1: "Start a Project"**
- Quick form: project name, building type, SF, location
- Saves to `mepcalc_project`
- Routes to ROM estimator (or whichever tool the user picks)
- Subsequent tools pre-fill from project state

**Path 2: "Use a Tool"**
- Same tool cards as V1
- Each card links directly to the standalone tool
- No project required, no friction, no signup

### Visual Change
Add a workflow diagram showing how tools connect:
```
ROM Estimator → General Conditions → Scope Gap Matrix
     ↓                                      ↓
System Sizing → Plenum Feasibility    Bid Leveling
     ↓
Healthcare Adder
```

Not fancy. A simple SVG or CSS diagram. Shows the preconstruction workflow without requiring anyone to follow it.

---

## What Stays the Same

- Vanilla HTML/CSS/JS. No frameworks. No build step.
- Each tool is one HTML file. Deployable anywhere.
- Works offline after first load
- Mobile-first, prints clean
- "Built by The Architect" footer on every page
- No accounts, no paywalls, no tracking
- Every calculation shows its work
- Every assumption is editable

## File Structure

```
/MEPCalc/
  index.html                    — Landing page with project start + tool index
  mepcalc-core.js              — Shared state, project bar, navigation (new)
  scope-gap-matrix.html         — V1 + bid leveling mode
  general-conditions.html       — V1 + reads project state
  electrical-room.html          — V1 (corrected per 6x3)
  plenum-space.html             — V1 (corrected per 6x3) + building type presets
  rom-estimator.html            — V1 (corrected per 6x3) + writes project state
  healthcare-adder.html         — New: healthcare/senior living cost adders
  system-sizing.html            — New: MEP system rough sizing
  serve.py                      — Local dev server
```

## Build Order

1. `mepcalc-core.js` — shared state engine (everything depends on this)
2. Update ROM estimator to write project state
3. Update General Conditions to read project state
4. Update Plenum to read building type presets
5. Update Scope Gap Matrix with bid leveling mode
6. Build Healthcare Adder (new)
7. Build System Sizing (new)
8. Update landing page with project start flow
9. Test full workflow: ROM → Gen Conditions → Scope Gap → Bid Level → Export

## What Success Looks Like

A Senior Director of Preconstruction at a Top-400 GC gets a link to mepcalc. She clicks "Start a Project," enters "Sunrise Senior Living Phase 2, 85,000 SF, Wilmington DE." In 15 minutes she has:

- A ROM estimate showing $7.2M MEP budget with trade breakdown
- A general conditions estimate showing $1.4M / 11.8% of cost
- A plenum feasibility check showing "tight — 2 inches remaining"
- A scope gap matrix with 76 items pre-assigned, ready to attach to bid packages
- A healthcare adder showing $12/SF premium over commercial baseline

She exports the scope gap matrix as CSV, prints the ROM estimate, and shares the link with her team. The tools saved her 3 hours on a Tuesday afternoon. She bookmarks the site.

That's the handshake.

---

*Spec written April 1, 2026. For the mind that builds it.*
