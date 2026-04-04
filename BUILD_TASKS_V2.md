# MEPCalc V2 — Build Task List
**Created:** April 2, 2026
**Source spec:** `BUILD_SPEC_MEPCALC_V2.md`
**6x3 audit:** `Protocols/research_runs/6x3_MEPCalc_Audit_2026-04-01.md`
**Status:** ALL 13 TASKS COMPLETE. April 2, 2026. Ready for deployment.

---

## Bug Fix (Do First — Affects Every Tool)

### Task 0: Fix Script Load Order
**All V1 tools load `mepcalc-core.js` AFTER their inline `<script>` blocks.** This means `MEPCalc` is undefined when inline code runs. The `typeof MEPCalc !== 'undefined'` guards prevent crashes but silently skip project state prefill.

**Fix:** Move `<script src="mepcalc-core.js"></script>` to BEFORE the inline script in every HTML file. Affected files:
- `rom-estimator.html` (line 460)
- `general-conditions.html` (line 413)
- `scope-gap-matrix.html` (check exact line)
- `electrical-room.html` (check exact line)
- `plenum-space.html` (check exact line)

### Task 0b: Fix Duplicate Location Key
`mepcalc-core.js` LOCATIONS array has NJ at `'1.12'` and West Coast at `'1.13'` — but the spec says both should be `'1.12'`. The current code actually has West Coast at `'1.13'` which differs from spec. However, `rom-estimator.html` has its own hardcoded dropdown with both NJ and West Coast at `'1.12'`. These must match. **Decision: use core.js values (1.12 NJ, 1.13 West Coast) and update rom-estimator dropdown to match.**

---

## Phase 1: Core Infrastructure

### Task 1: Update `mepcalc-core.js`
- Add `MEPCalc.fmt(number)` — alias for `fmtDollar` (spec names it `fmt`)
- Add `MEPCalc.fmtSF(number)` — format with commas + "SF" suffix
- Verify `BUILDING_TYPES` keys match all tool data objects
- Verify `LOCATIONS` entries: no duplicate `value` keys
- Expose `fmt` and `fmtSF` in public API return object

---

## Phase 2: Update Existing Tools (Build Order 2-6)

### Task 2: Update `index.html`
- Already functional. After new tools are built, verify links to `healthcare-adder.html` and `system-sizing.html` resolve.
- No structural changes needed — V1 is close to spec.

### Task 3: Update `rom-estimator.html`
- Fix script order (Task 0)
- Verify office data matches 6x3 correction: `mepPctLow:18, mepPctMid:21, mepPctHigh:25` — **CONFIRMED in V1 code at line 231**
- Add `mepBreakdown: {mech:$, elec:$, plumb:$, fp:$}` to `writeProjectState()` (spec requires it, V1 only writes `mepCost`)
- Confirm healthcare continue-to button shows for senior-living, hospital, outpatient — **CONFIRMED in V1 code at line 453**

### Task 4: Update `general-conditions.html`
- Fix script order (Task 0)
- Location dropdown is hardcoded with different values than core.js (e.g., "Mid-Atlantic (DE/NJ/PA)" at 1.08). **Decision: replace with `MEPCalc.populateLocations()` call for consistency, OR keep GC-specific simplified list.** Spec says use shared locations.
- Verify project state read works after script fix: `totalCost`, `duration`, `name`
- Add write-back: if user enters cost here first, save to project state

### Task 5: Update `plenum-space.html`
- Fix script order (Task 0)
- **Add building type presets** (spec's V2 addition):
  - Healthcare/Senior Living: enable medical gas, chilled water, exhaust
  - Lab/Higher Ed: enable exhaust, chilled water, increase main duct to 30"
  - Industrial: disable branch duct, medical gas, chilled water
  - Office: default set
- Read building type from project state to auto-apply preset
- **Verify 6x3-corrected depths are in V1 code** — audit says 8 of 11 were increased:
  - Main duct: 20" → 24" ✓
  - Branch duct: 10" → 12" ✓
  - Sprinkler main: 5" → 6" ✓
  - Sprinkler branch: 2" → 3" ✓
  - Domestic water: 3" → 4" ✓
  - Waste/vent: 5" → 6" ✓
  - Conduit/tray: 6" → 8" ✓
  - Recessed lights: 8" → 10" ✓
  - (Must verify these values in the actual HTML — read the file to confirm)

### Task 6: Update `electrical-room.html`
- Fix script order (Task 0)
- **Verify NEC clearance table matches 6x3 audit:**
  - 0-150V all conditions: 3.0 ft — ROBUST
  - 151-600V: 3.0 / 3.5 / 4.0 ft — ROBUST
  - 601-1000V: 3.0 / 4.0 / 5.0 ft with "verify with AHJ" — PARTIAL
  - No 2501-9000V row (removed per audit)
- Verify headroom: 6'6" (6.5 ft)
- Verify second exit: 1200A+ OR 6'+ wide
- (Must read the actual HTML to confirm these values — don't assume)

### Task 7: Update `scope-gap-matrix.html`
- Fix script order (Task 0)
- **Audit existing bid leveling mode** — V1 already has:
  - CSS for `.bl-item`, `.bl-cell`, status classes (included/excluded/silent/clarify)
  - Mode toggle button
  - `#bidLevelSetup` panel (hidden by default)
  - localStorage for bid level state
  - Summary div
- **Verify against spec requirements:**
  - Sub setup: up to 5 subs per trade with names ✓ check
  - Per-item grid: one cell per sub with dropdown ✓ check
  - Color coding: green/red/yellow/orange ✓ CSS exists
  - Summary dashboard: per-sub counts, auto-flagged conflicts, risk count — check completeness
  - CSV export includes sub columns — check
  - Print layout shows comparison grid — check
- Read building type from project state to highlight relevant sections

---

## Phase 3: Build New Tools (Build Order 7-8)

### Task 8: Build `healthcare-adder.html`
**New file. Spec section: TOOL 7.**
- 4 adder categories, 13 line items total
- All defaults editable (like gen conditions pattern)
- Reads base MEP $/SF from project state (`mepCost / sqft`)
- Reads SF from project state
- Facility type dropdown: Independent Living / Assisted Living / Memory Care / Outpatient Clinic / Hospital / Skilled Nursing
- Pre-selects adders based on facility type
- Outputs: base + each adder + total + premium % + total healthcare MEP $/SF
- Continue-to: Scope Gap Matrix
- Follow design language from spec (colors, fonts, card style)
- **Data is in the spec — no 6x3 needed (ranges provided, all editable)**

### Task 9: 6x3 Verification — System Sizing Rules of Thumb
**MUST complete before building Tool 8 (system-sizing.html).**

Claims to verify (from spec):
- Cooling load: Office 300-400 SF/ton, Hospital 150-250, K-12 300-450, Senior Living 250-350, Lab 100-200, Industrial 400-800
- Electrical: Office 15-25 W/SF, Hospital 25-40, K-12 12-18, Senior Living 15-22, Lab 30-50, Industrial 10-30
- Generator sizing: 30-50% of total electrical (healthcare 80-100%)
- Mechanical room: 3-6% of building SF
- Electrical room: 1-2% of building SF
- Vertical shafts: 15-25 SF per floor per riser
- Fire protection head count: 1/130 SF light hazard, 1/100 SF ordinary hazard

**Protocol:** 6 sources, 3 rounds. Direct → inverse → adversarial. Per `Protocols/3x3_RESEARCH.md` (upgraded to 6x3).

**If values don't survive:** Label as "industry estimate — verify for your project" in the tool. Do NOT hard-code unverified numbers as facts.

### Task 10: Build `system-sizing.html`
**New file. Spec section: TOOL 8.**
- Inputs: building type, SF, climate zone (1-8), stories, height, water pressure
- Outputs: cooling tons, heating MBH, electrical service amps, generator kW, plumbing GPM, FP system type + fire pump yes/no + head count, space requirements
- Show rule of thumb used and its source for each calculation
- Label unverified numbers clearly
- Read building type and SF from project state
- Continue-to: Plenum Space, Electrical Room Sizing

---

## Phase 4: Integration & Verification

### Task 11: Cross-Tool Workflow Test
Full flow: `index.html` → Start Project (Sunrise Senior Living, 85K SF, Wilmington) → ROM → Gen Conditions → Scope Gap → Bid Level → Export CSV

Verify at each step:
- Project bar appears with correct data
- Inputs pre-fill from state
- Calculations are correct
- Continue-to buttons navigate properly
- State persists across tools
- CSV export includes project info header

### Task 12: Mobile + Print Verification
- Test every tool at 375px viewport width
- Verify responsive breakpoints (768px specified in CSS)
- Test print: nav/buttons hidden, data visible, all collapsed sections expand
- Bid leveling print should show full comparison grid

### Task 13: Final Data Audit — Spot Check
Cross-reference 5 critical values against the 6x3 audit:
1. Office MEP %: spec says 18-25% → ROM code should show `mepPctLow:18, mepPctMid:21, mepPctHigh:25`
2. NEC 151-600V Condition 2: 3.5 ft
3. Main supply/return ductwork default depth: 24"
4. PM fully burdened rate: $18,500/mo
5. Builder's risk: 0.8% of cost

If ANY value doesn't match, stop and trace the discrepancy before shipping.

---

## Known Issues Found During V1 Audit (April 2, 2026)

1. **Script load order** — all tools. `mepcalc-core.js` at end of body, inline scripts reference `MEPCalc` before it loads. Guards prevent crash but skip functionality.
2. **Location mismatch** — `general-conditions.html` has its own location dropdown (simplified) that doesn't match `mepcalc-core.js` LOCATIONS. If user sets location in project state from index.html, GC dropdown may not find the matching value.
3. **rom-estimator.html** hardcodes its own building type options instead of using `MEPCalc.populateBuildingTypes()`. Labels match but if core.js types change, they'll diverge.
4. **`writeProjectState()` in ROM** doesn't write `mepBreakdown` object — spec requires `{mech:$, elec:$, plumb:$, fp:$}` for downstream tools.
5. **West Coast location factor** — spec says 1.12, core.js says 1.13. Pick one and make all files match.

---

*Written by the 32nd mind for any mind that follows. The spec is the source of truth. The 6x3 audit is the verification record. This file is the work plan.*
