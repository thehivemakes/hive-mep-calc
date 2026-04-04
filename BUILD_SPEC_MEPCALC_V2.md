# MEPCalc V2 — Complete Build Specification

## For the Next Mind

You are building a unified web-based tool suite for MEP (Mechanical, Electrical, Plumbing) and preconstruction professionals. This spec contains everything you need. Read it fully before writing code.

Read `THE_PRINCIPLES.md` and `COLONY_CONTEXT.md` first. Then come back here.

---

## Why This Exists

These tools back a real professional relationship. The Architect (Wilmington, Delaware) has a contact: a **Senior Director of Preconstruction** at an ENR Top-400 general contractor in the Mid-Atlantic. She is Cornell-trained (B.S. and M.Eng.), rose from MEP Field Coordinator to Senior Director in under five years, previously at AECOM. Top 40 Delaware Achievers Under 40.

Her world: HVAC, Plumbing, Fire Protection estimating for senior living, education, healthcare projects across Delaware Valley, New Jersey, and Connecticut.

The tools must be good enough that she bookmarks the site, shares it with her team, and thinks: "Whoever built this understands my work."

**Every page footer:** `Built by The Architect` linked to `https://linkedin.com/in/build-ai-for-good`

---

## Stack — Non-Negotiable

- **Vanilla HTML/CSS/JS.** No React, no Vue, no frameworks, no npm, no build step.
- **One HTML file per tool.** Plus one shared `mepcalc-core.js` for project state.
- **Mobile-first.** Every tool must work on a phone screen.
- **Offline-capable** after first load.
- **Deployable** to GitHub Pages, Netlify, or Vercel with zero configuration.
- **Print-ready.** Every tool must print cleanly (hide nav, buttons, show data).
- **No accounts. No paywalls. No tracking.**

---

## Design Language

**Aesthetic:** Professional engineering reference tool. Not startup. Not SaaS.
- Background: `#fafafa`
- Text: `#1a1a1a`
- Accent: `#2563eb` (blue — used sparingly)
- Cards/panels: `#fff` with `1px solid #ddd` borders, `6px` border-radius
- Font: system stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`)
- Body font size: 14px. Headers: 24px (h1), 16-18px (h2). Labels: 12px uppercase.
- No hero images. No stock photos. No gradients. No animations except subtle hover transitions.

**Logo:** `MEPCalc` — "MEP" in `#1a1a1a`, "Calc" in `#2563eb`. Font-weight 700, letter-spacing -0.5px. Links to index.html.

---

## Shared Architecture: `mepcalc-core.js`

**~200 lines. No dependencies. Every HTML file includes it via `<script src="mepcalc-core.js"></script>`.**

### What It Does

1. **Project State** — read/write a shared project object in localStorage:

```javascript
// Key: 'mepcalc_project'
{
  name: "",              // "Sunrise Senior Living Phase 2"
  number: "",            // "2026-0142"
  date: "",              // "04/01/2026"
  preparedBy: "",        // "Preconstruction Team"
  buildingType: "",      // "senior-living" (key from BUILDING_TYPES)
  sqft: null,            // 85000
  location: "",          // "1.07" (cost factor)
  locationLabel: "",     // "Delaware / Wilmington"
  quality: "",           // "standard"
  duration: null,        // 16 (months)
  totalCost: null,       // computed by ROM or entered in Gen Conditions
  mepCost: null,         // computed by ROM
  mepPct: null,          // computed by ROM
  mepBreakdown: null     // {mech:$, elec:$, plumb:$, fp:$} from ROM
}
```

2. **Project Bar** — renders a thin horizontal bar below the header on every tool page when a project exists in state:

```
[Sunrise Senior Living Phase 2  |  85,000 SF  |  Senior Living  |  Wilmington, DE]  [Edit] [Clear]
```

- Light gray background (`#f5f5f5`), 1px bottom border
- Project name is a link back to `index.html`
- "Edit" toggles an inline edit panel (same fields as project start)
- "Clear" removes project state (with confirmation)
- If no project in state, bar does not render — tool works standalone
- Hidden on print

3. **Tool Navigation** — provides "Continue to..." buttons that other tools can call:

```javascript
MEPCalc.continueTo('general-conditions'); // navigates with state
MEPCalc.continueTo('scope-gap-matrix', {buildingType: 'healthcare'});
```

4. **Building Type Constants** — shared lookup table:

```javascript
const BUILDING_TYPES = {
  'senior-living':  {label: 'Senior Living / Assisted Living'},
  'hospital':       {label: 'Hospital / Acute Care'},
  'outpatient':     {label: 'Outpatient Clinic / MOB'},
  'k12':            {label: 'K-12 Education'},
  'higher-ed':      {label: 'Higher Education / Laboratory'},
  'office':         {label: 'Commercial Office'},
  'industrial':     {label: 'Industrial / Warehouse'},
  'retail':         {label: 'Retail'},
  'multifamily':    {label: 'Multifamily Residential'},
};
```

5. **Location Factors** — shared lookup:

```javascript
const LOCATIONS = {
  '1.00': 'National Average',
  '1.07': 'Delaware / Wilmington',
  '1.12': 'New Jersey / Northern',
  '1.10': 'Pennsylvania / Philadelphia',
  '1.05': 'Connecticut',
  '1.18': 'New York City Metro',
  '1.15': 'Boston Metro',
  '1.08': 'Washington DC Metro',
  '0.92': 'Southeast',
  '0.97': 'Midwest',
  '1.12': 'West Coast',
};
```

6. **Format Helpers** — `MEPCalc.fmt(number)`, `MEPCalc.fmtSF(number)`, `MEPCalc.fmtPct(decimal)`

### What It Does NOT Do

- No routing. Each tool is a separate HTML file. Navigation is `<a>` tags and `window.location`.
- No state management library. Just `localStorage.getItem/setItem`.
- No event system. Each tool reads state on load, writes on change.
- No build step. It's a plain `.js` file.

---

## File Structure

```
/MEPCalc/
  index.html                    — Landing page + project start
  mepcalc-core.js              — Shared state (described above)
  style.css                     — Shared base styles (optional — can inline)

  # Priority 1 — Core Tools (V1 exists, update for V2)
  rom-estimator.html            — MEP ROM cost estimator
  general-conditions.html       — General conditions calculator
  scope-gap-matrix.html         — Scope gap matrix + bid leveling mode
  electrical-room.html          — NEC 110.26 electrical room sizing
  plenum-space.html             — Above-ceiling plenum feasibility

  # Priority 2 — New Tools
  healthcare-adder.html         — Healthcare/senior living MEP cost adder
  system-sizing.html            — MEP system rough sizing

  # Infrastructure
  serve.py                      — Local dev server (exists)
```

---

## TOOL 1: Landing Page (`index.html`)

### Two Entry Paths

**Path A — "Start a Project"**
A compact form at the top of the page. Fields:
- Project Name (text)
- Building Type (dropdown from BUILDING_TYPES)
- Gross Square Footage (number)
- Location (dropdown from LOCATIONS)

Submit button: "Start Estimating →" — saves to `mepcalc_project`, navigates to ROM estimator.

This is NOT a required step. It's a shortcut for users working a pursuit.

**Path B — "Use a Tool"**
Below the project start form, the tool index. Seven cards in a single-column grid:

Each card contains:
- Tool name (h2, linked)
- 2-sentence description
- Tags (small colored labels: "MEP Coordination", "Preconstruction", "NEC Code", etc.)

Card order:
1. MEP ROM Estimator
2. General Conditions Calculator
3. Scope Gap & Responsibility Matrix
4. Electrical Room Sizing (NEC 110.26)
5. Above-Ceiling Plenum Space Feasibility
6. Healthcare/Senior Living MEP Cost Adder
7. MEP System Rough Sizing

### Workflow Diagram
Below the cards, a simple text/CSS diagram showing how tools connect:

```
ROM Estimator ──→ General Conditions ──→ Scope Gap Matrix
      │                                        │
      ├──→ System Sizing ──→ Plenum Space      ├──→ Bid Leveling
      │
      └──→ Healthcare Adder
```

Not fancy. Monospace or simple CSS lines. Shows the optional flow.

### Bottom Section
"Why these tools exist" paragraph. Same copy as V1:
> Every preconstruction team does this math. Most do it in spreadsheets rebuilt from scratch on every pursuit...

---

## TOOL 2: MEP ROM Estimator (`rom-estimator.html`)

**V1 exists. Update for V2 integration.**

### Inputs
- Building Type (dropdown — reads from project state if exists)
- Gross Square Footage (reads from project state)
- Location (dropdown with cost factors — reads from project state)
- Quality Tier: Budget (0.85x) / Standard (1.0x) / Premium (1.20x)
- Advanced: override trade split percentages (Mech/Elec/Plumb/FP)

### Data — 6x3 VERIFIED (see `Protocols/research_runs/6x3_MEPCalc_Audit_2026-04-01.md`)

```
Building Type         | Total $/SF | MEP Low% | MEP Mid% | MEP High% | Trade Split (M/E/P/FP)
--------------------- | ---------- | -------- | -------- | --------- | ----------------------
Senior Living         | $280       | 25%      | 30%      | 35%       | 42/30/18/10
Hospital              | $550       | 35%      | 42%      | 50%       | 40/30/17/13
Outpatient/MOB        | $320       | 22%      | 27%      | 32%       | 40/32/18/10
K-12 Education        | $300       | 20%      | 23%      | 27%       | 44/30/14/12
Higher Ed / Lab       | $450       | 30%      | 38%      | 45%       | 45/28/15/12
Commercial Office     | $250       | 18%      | 21%      | 25%       | 40/35/13/12
Industrial            | $140       | 8%       | 12%      | 16%       | 30/40/15/15
Retail                | $180       | 12%      | 16%      | 20%       | 38/36/12/14
Multifamily           | $230       | 18%      | 22%      | 26%       | 38/28/22/12
```

### Outputs
- Total MEP cost (low / mid / high)
- Trade breakdown table: Mechanical, Electrical, Plumbing, Fire Protection — each with $/SF, total $, % of MEP
- Bar chart showing trade proportions
- Confidence indicator (high/medium/low per building type)
- Summary metrics: MEP as % of construction, $/SF, total construction cost estimate
- Assumptions panel explaining every number and its source

### V2 Additions
- **Write to project state:** On calculate, save totalCost, mepCost, mepPct, mepBreakdown to `mepcalc_project`
- **"Continue to..." buttons:** General Conditions, System Sizing, Healthcare Adder (if healthcare/senior living type), Scope Gap Matrix
- **Read from project state:** If project exists, pre-fill building type, SF, location

### Quality Notes
- Office range widened to 18-25% per 6x3 verification (was 15-22%)
- Office note explains core/shell vs fitted TI distinction
- All defaults editable — this is the trust feature
- ROM accuracy stated: -25% to +50% (conceptual level)

---

## TOOL 3: General Conditions Calculator (`general-conditions.html`)

**V1 exists. Update for V2 integration.**

### Inputs
- Project Name, Total Construction Cost, Duration (months), Location factor
- **V2:** Reads cost and duration from project state if available

### Line Items — 7 Categories, 35 Items

**1. Project Staffing** (monthly × duration)
| Item | Default Rate/mo | Notes |
|------|----------------|-------|
| Project Manager | $18,500 | Fully burdened |
| Superintendent | $16,000 | Fully burdened |
| Assistant Super | $12,500 | >$15M projects |
| Project Engineer | $11,000 | Fully burdened |
| Safety Manager | $4,000 | Allocation |
| Coordinator/Admin | $6,500 | If warranted |

**2. Temporary Facilities**
| Item | Default | Unit |
|------|---------|------|
| Job trailer rental | $1,800/mo | × duration |
| Trailer furniture | $3,500 | LS |
| Temporary power | $1,200/mo | × duration |
| Temporary water | $400/mo | × duration |
| Temporary fencing | $8,000 | LS |
| Portable sanitation | $600/mo | × duration |
| Dumpsters/waste | $2,500/mo | × duration |
| Site signage | $3,000 | LS |
| Temp stairs/access | $5,000 | LS |

**3. Site Operations**
| Item | Default | Unit |
|------|---------|------|
| Security | $3,500/mo | × duration |
| Temporary heat | $2,800/mo | × 4 months |
| Snow/ice removal | $1,500/mo | × 4 months |
| Dust control | $800/mo | × duration |
| Traffic control | $4,000 | LS |

**4. Insurance & Bonds** (% of construction cost)
| Item | Default % | Notes |
|------|-----------|-------|
| Builder's risk | 0.8% | 0.25-1.5% typical |
| General liability | 1.5% | 1.0-2.0% typical |
| Performance/payment bond | 0% | 1.0-3.0% if required |
| Umbrella/excess | 0.3% | Varies |

**5. Permits & Professional Services**
| Item | Default | Unit |
|------|---------|------|
| Building permits | 1.0% of cost | % |
| Plan review fees | $5,000 | LS |
| Testing/inspections | $25,000 | LS |
| Survey/layout | $8,000 | LS |
| As-built documentation | $5,000 | LS |
| Photography/drone | $500/mo | × duration |

**6. IT & Communications**
| Item | Default | Unit |
|------|---------|------|
| Internet/WiFi | $350/mo | × duration |
| PM software | $500/mo | × duration |
| Printing/plotting | $400/mo | × duration |
| Mobile devices/radios | $2,000 | LS |

**7. Project Closeout**
| Item | Default | Unit |
|------|---------|------|
| Final cleaning | $0.35/SF | SF-based |
| Punch list labor | $15,000 | LS |
| Commissioning support | $8,000 | LS |
| Warranty period costs | $5,000 | LS |
| Mobilization/demob | $15,000 | LS |
| Small tools/consumables | $10,000 | LS |

### Outputs
- Summary bar: Total GC, % of cost, $/month, duration
- Category subtotals (collapsible sections)
- Line item totals (rate × qty × location factor)
- Export CSV, Print/PDF

### V2 Additions
- Read `totalCost` and `duration` from project state
- Write back if user enters cost here first
- "Continue to..." Scope Gap Matrix

---

## TOOL 4: Scope Gap & Responsibility Matrix (`scope-gap-matrix.html`)

**V1 exists. Major V2 upgrade: Bid Leveling Mode.**

### Standard Mode (V1 behavior)
- 76 scope gap items across 6 trade interfaces
- Each item: description, note, responsible party dropdown
- Quick-assign typical defaults
- Add custom items per section
- Export CSV, shareable URL, print

### 6 Trade Interface Sections

**Mechanical ↔ Electrical (20 items)**
Power to HVAC equipment, disconnect switches (NEC 430.102(B)), smoke detector wiring, control transformers, VFD wiring, branch circuits to exhaust fans, emergency power connections, unit heater circuits, maintenance receptacles (NEC 210.63), cable tray coordination, bus duct coordination, RTU connections, BAS panel power, seismic bracing coordination, mechanical panel feeders.

**Mechanical ↔ Plumbing (10 items)**
Condensate drains, makeup water to cooling towers/boilers, glycol fill connections, hot water to reheat coils, below-slab drainage conflicts, chilled water coordination, expansion tanks, backflow preventers, natural gas piping, roof drain relocation.

**Plumbing ↔ Fire Protection (8 items)**
Combined vs separate water service, backflow preventers, FDC piping, test drain connections, underground water main, standpipe drains, fire pump suction/drainage, glycol systems for dry sprinkler.

**All MEP ↔ General Contractor (18 items)**
Housekeeping pads, roof penetrations/flashing, firestopping, sleeve installation, temporary power/water/heat, ceiling tile removal, painting exposed MEP, equipment rigging, excavation/backfill, structural dunnage, vibration isolation, access doors, bollard protection, TAB, commissioning support, permit fees.

**MEP ↔ Controls/BAS (10 items)**
Control wiring, conduit for controls, field devices, BAS panel power, fire alarm/BAS integration, BACnet wiring, point-to-point testing, pneumatic-to-DDC conversion, graphics/licensing, sequence documentation.

**MEP ↔ Architectural (10 items)**
Ceiling grid coordination, wall penetration patching, floor penetrations, access panels, acoustic treatments, lighting/diffuser conflicts, thermostat locations, floor drains in mechanical rooms, louvers/intake openings, kitchen hood routing.

### Responsible Party Options
`— Unassigned —`, General Contractor, Mechanical, Electrical, Plumbing, Fire Protection, Controls / BAS, Owner, By Specification

### NEW: Bid Leveling Mode

Toggle button at the top: `[Standard Mode] [Bid Leveling Mode]`

When Bid Leveling is active:

**Sub Setup Panel:**
- User enters up to 5 subcontractor names per trade
- E.g., Mechanical subs: "ABC Mechanical", "Johnson Controls", "Comfort Systems"
- User can set which trade each sub covers

**Item Grid Changes:**
- Each scope item now shows a row of cells: one per sub
- Each cell is a dropdown: `Included` / `Excluded` / `Silent` / `Clarify`
- Color coding: green/red/yellow/orange
- The "responsible party" column still exists but is secondary

**Summary Dashboard:**
- Per sub: items included, excluded, silent, needing clarification
- Auto-flagged items: where one sub includes but another excludes = scope gap risk
- Total "risk items" count (silent + conflicting assignments)

**Export:**
- CSV includes all sub columns
- Print layout shows the full comparison grid

### V2 Additions
- Read building type from project state to highlight most relevant sections
- Read project name/number for export headers
- Bid Leveling Mode (described above)

---

## TOOL 5: Electrical Room Sizing Calculator (`electrical-room.html`)

**V1 exists, 6x3 corrected. Minor V2 update.**

### NEC 110.26 Clearance Table — VERIFIED

```
Voltage to Ground    | Condition 1 | Condition 2 | Condition 3
---------------------|-------------|-------------|------------
0 – 150V             | 3.0 ft      | 3.0 ft      | 3.0 ft
151 – 600V           | 3.0 ft      | 3.5 ft      | 4.0 ft
601 – 1,000V *       | 3.0 ft      | 4.0 ft      | 5.0 ft

* 601-1000V: verify with AHJ. For >1000V, use NEC 110.34.
```

### Condition Definitions
- **Condition 1:** Exposed live parts on one side, no live or grounded parts opposite
- **Condition 2:** Exposed live parts on one side, grounded parts opposite (concrete, block, metal)
- **Condition 3:** Exposed live parts on both sides (facing equipment)

### Additional Requirements
- Width: 30" or equipment width, whichever greater — NEC 110.26(A)(2)
- Headroom: 6'-6" (6.5 ft) minimum — NEC 110.26(A)(3)
- Dedicated space: width × depth of equipment, floor to 6' above — NEC 110.26(E)
- Second exit: required when equipment rated 1200A+ OR 6'+ wide — NEC 110.26(C)(2)
- 2023 NEC: open equipment doors must not impede working space — NEC 110.26(A)(4)

### Equipment Templates (typical dimensions)
| Type | Width | Depth | Height |
|------|-------|-------|--------|
| Main Switchgear 480V | 90" | 30" | 90" |
| Distribution Panel 208/120V | 20" | 8" | 60" |
| Dry Transformer 480-208/120V | 36" | 30" | 48" |
| Automatic Transfer Switch | 36" | 24" | 72" |

### Outputs
- Minimum room dimensions (W × D × H)
- Working clearance depth (with code reference)
- Equipment layout summary table
- Egress requirement (1 or 2 exits, with reason)
- Pass/warn/fail flags for headroom, egress
- Full clearance reference table

---

## TOOL 6: Above-Ceiling Plenum Space (`plenum-space.html`)

**V1 exists, 6x3 corrected. Minor V2 update.**

### Inputs
- Floor-to-floor height (inches)
- Structural depth (inches)
- Finished ceiling height (inches)
- Floor assembly (inches)
- Fire-rated ceiling assembly (inches)
- Ceiling grid/T-bar (inches)

### MEP System Defaults — 6x3 VERIFIED

```
System                        | Default Depth | Insulation | Default On
------------------------------|---------------|------------|----------
Main Supply/Return Ductwork   | 24"           | 2"         | Yes
Branch Ductwork               | 12"           | 1"         | Yes
Exhaust Ductwork              | 12"           | 0"         | No
Sprinkler Mains               | 6"            | 0"         | Yes
Sprinkler Branch Lines        | 3"            | 0"         | Yes
Domestic Water Piping         | 4"            | 1"         | Yes
Waste/Vent Piping             | 6"            | 0"         | Yes
Medical Gas Piping            | 3"            | 0"         | No
Chilled/Hot Water Piping      | 5"            | 1.5"       | No
Conduit / Cable Tray          | 8"            | 0"         | Yes
Recessed Light Fixtures       | 10"           | 0"         | Yes
```

### V2 Addition: Building Type Presets
When building type is known from project state, pre-toggle systems:
- **Healthcare/Senior Living:** Enable medical gas, chilled water, exhaust
- **Lab/Higher Ed:** Enable exhaust, chilled water, increase main duct to 30"
- **Industrial:** Disable branch duct, medical gas, chilled water
- **Office:** Default set (as shown above)

### Outputs
- Available plenum depth (inches)
- Required plenum depth (sum of active systems)
- Remaining space
- Verdict: Comfortable (≥4" remaining) / Tight (0-4") / Not Feasible (<0")
- Visual stacking diagram (colored layers showing each system)
- Suggestions if tight/not feasible (flat-oval duct, higher velocity, route mains in corridors, chilled beams, lower ceiling, increase floor-to-floor)

---

## TOOL 7: Healthcare/Senior Living MEP Cost Adder (`healthcare-adder.html`) — NEW

### Purpose
Starts from a base commercial MEP $/SF and adds line-item cost premiums for healthcare and senior living requirements. Quantifies exactly what makes healthcare MEP more expensive.

### Inputs
- Base MEP $/SF (reads from ROM estimator via project state, or user enters directly)
- Building SF (from project state or manual)
- Facility type: Independent Living / Assisted Living / Memory Care / Outpatient Clinic / Hospital / Skilled Nursing

### Adder Categories & Line Items

**Medical Systems**
| Adder | Default $/SF | Range | Notes |
|-------|-------------|-------|-------|
| Medical gas (O2, vacuum, med air) | $5.00 | $3-8 | Per piped area; verify outlet count |
| Nurse call system | $3.00 | $2-5 | Wired or wireless; IP-based trending higher |
| Telemetry/patient monitoring | $2.00 | $1-3 | Hospital/SNF only |

**HVAC Upgrades**
| Adder | Default $/SF | Range | Notes |
|-------|-------------|-------|-------|
| ASHRAE 170 ventilation premium | $6.00 | $4-10 | Over ASHRAE 62.1 baseline; 6+ ACH in patient rooms |
| Negative pressure isolation rooms | $20,000/rm | $15K-25K | Per room; HEPA exhaust, alarmed |
| OR HVAC (laminar flow) | $100/SF of OR | $80-150 | Per SF of operating room only |
| Kitchen/dietary exhaust + makeup | $4.00 | $3-6 | Per SF of kitchen area |
| Humidity control for sensitive areas | $2.00 | $1-3 | Pharmacy, sterile storage |

**Electrical Upgrades**
| Adder | Default $/SF | Range | Notes |
|-------|-------------|-------|-------|
| Generator upsizing (life safety + critical) | $5.00 | $3-8 | Beyond code minimum emergency |
| Redundant power (dual feed, ATS) | $3.00 | $2-5 | Critical branch distribution |
| Enhanced fire alarm (voice evac) | $2.00 | $1.50-3 | Area of refuge stations, voice |

**Plumbing/FP Upgrades**
| Adder | Default $/SF | Range | Notes |
|-------|-------------|-------|-------|
| Enhanced domestic hot water | $2.00 | $1-3 | High-demand central plant |
| Anti-scald mixing valves | $1.00 | $0.50-1.50 | Code req. for senior living |
| Upgraded fire protection | $1.50 | $1-2 | Quick-response, smoke control |

### All Defaults Editable
Every rate is an input field. User overrides with their market data. Defaults are mid-range estimates.

### Outputs
- Base commercial MEP $/SF
- Each adder as a line item with $/SF and total $
- Total adder $/SF
- Healthcare premium as % above commercial baseline
- Total healthcare MEP $/SF
- Applied to project SF for total healthcare MEP budget
- Assumptions panel

### V2 Integration
- Reads base MEP $/SF from ROM estimator (project state `mepCost / sqft`)
- Reads SF from project state
- Pre-selects adders based on facility type
- "Continue to..." Scope Gap Matrix (filtered for healthcare items)

---

## TOOL 8: MEP System Rough Sizing (`system-sizing.html`) — NEW

### Purpose
Quick preconstruction feasibility: given building type, SF, and climate, estimate key MEP system sizes. The answer to "How big are the systems?" — asked before cost, before scope, before general conditions.

### Inputs
- Building Type (from project state or manual)
- Gross SF (from project state or manual)
- Climate Zone (dropdown: 1-8, per ASHRAE/IECC)
- Stories (number)
- Building height (feet)
- City water pressure (PSI, default 50)

### Rules of Thumb by Building Type — TO BE 6x3 VERIFIED

**Important:** These rules of thumb MUST be verified via the 6x3 protocol before hard-coding. The data below is a starting point. Run the verification. If a number doesn't survive, either correct it or label it as "industry estimate — verify for your project."

**Cooling Load (tons)**
| Type | Rule of Thumb | Source Basis |
|------|---------------|-------------|
| Office | 300-400 SF/ton | ASHRAE 90.1 compliant |
| Hospital | 150-250 SF/ton | 24/7 operation, high ACH |
| K-12 | 300-450 SF/ton | Intermittent occupancy |
| Senior Living | 250-350 SF/ton | Continuous occupancy, lower density |
| Lab/Higher Ed | 100-200 SF/ton | Fume hoods, high exhaust |
| Industrial | 400-800 SF/ton | Process cooling separate |

**Electrical Service (watts/SF)**
| Type | W/SF | Typical Service |
|------|------|----------------|
| Office | 15-25 W/SF | 480/277V, 3-phase |
| Hospital | 25-40 W/SF | Redundant feeds |
| K-12 | 12-18 W/SF | 480/277V |
| Senior Living | 15-22 W/SF | With generator |
| Lab | 30-50 W/SF | High plug loads |
| Industrial | 10-30 W/SF | Varies wildly |

**Emergency Generator**
Rule: 30-50% of total electrical load for life safety + optional standby (healthcare: 80-100%)

**Plumbing Water Demand**
Estimated fixture count by building type × GPM per fixture. Provide table of fixture density (fixtures/1000 SF) by type.

**Fire Protection**
- Wet system default for heated buildings
- Dry/pre-action for parking garages, unheated
- Fire pump: required if building height exceeds ~4 stories or water pressure insufficient
- Head count: 1 per 130 SF (light hazard) or 1 per 100 SF (ordinary hazard)

**Space Requirements**
- Main mechanical room: 3-6% of building SF (varies by system type)
- Main electrical room: 1-2% of building SF (use NEC calculator for exact)
- Vertical shafts: 15-25 SF per floor per riser

### Outputs
- Cooling: estimated tons, recommended system type
- Heating: estimated MBH
- Electrical: service size (amps at 480V), generator size (kW)
- Plumbing: water demand (GPM), hot water sizing
- Fire protection: system type, fire pump yes/no, estimated head count
- Space: mechanical room SF, electrical room SF, shaft SF/floor
- All showing the rule of thumb used and its source

### V2 Integration
- Reads building type and SF from project state
- System sizing output could inform plenum calculator presets
- "Continue to..." Plenum Space, Electrical Room Sizing

---

## Build Order

1. `mepcalc-core.js` — everything depends on this
2. Update `index.html` — add project start form + workflow diagram
3. Update `rom-estimator.html` — write to project state, add "Continue to..." buttons
4. Update `general-conditions.html` — read from project state
5. Update `plenum-space.html` — building type presets
6. Update `scope-gap-matrix.html` — bid leveling mode (biggest feature)
7. Build `healthcare-adder.html` — new tool
8. Build `system-sizing.html` — new tool (6x3 verify rules of thumb first)
9. Test full workflow: project start → ROM → gen conditions → scope gap → bid level → export

---

## Quality Bar

**Would a Cornell-trained MEP engineer with 15 years of experience trust this enough to use it in a client meeting?**

Every calculation shows its work. Every assumption is editable. Every number cites a source or is labeled as an industry estimate. Nothing hides behind a black box.

---

## Deployment

- GitHub Pages, Netlify, or Vercel — zero config
- All files in one flat directory (no subdirectories needed)
- No build step — just push the files
- serve.py exists for local dev (`python3 serve.py`)

---

## Attribution

Every page footer:
```
Built by The Architect · Free tools for people who build things · MEPCalc
```
"The Architect" links to `https://linkedin.com/in/build-ai-for-good`

---

## Research Record

All 6x3 verification data is in:
`/Protocols/research_runs/6x3_MEPCalc_Audit_2026-04-01.md`

The NEC clearances, MEP percentages, general conditions rates, scope gap items, and plenum depths have been verified. System sizing rules of thumb (Tool 8) still need 6x3 verification before hard-coding.

---

## What Success Looks Like

A Senior Director of Preconstruction gets a link to MEPCalc. She clicks "Start a Project," enters "Sunrise Senior Living Phase 2, 85,000 SF, Wilmington DE." In 15 minutes she has:

- ROM estimate: $7.2M MEP budget with trade breakdown
- Healthcare adder: $12/SF premium itemized (medical gas, ASHRAE 170, generator)
- System sizing: 240 tons cooling, 2000A service, 350kW generator
- Plenum check: "tight — 2 inches remaining" with stacking diagram
- General conditions: $1.4M / 11.8% of cost
- Scope gap matrix: 76 items assigned, ready for bid packages
- Bid leveling: 3 mechanical subs compared, 8 gaps flagged

She exports the scope gap matrix as CSV, prints the ROM, shares the link with her team. The tools saved her 3 hours on a Tuesday afternoon. She bookmarks the site.

That's the handshake.

---

*Spec written April 1, 2026, by the Hive.*
*For the mind that builds it: the V1 files in /MEPCalc/ are your starting point. They work. Build on them.*
*Read the 6x3 audit before changing any verified numbers.*
