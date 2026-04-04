/**
 * MEPCalc Core — Shared state, project bar, navigation, constants
 * Include this in every tool page: <script src="mepcalc-core.js"></script>
 * No dependencies. No build step. ~200 lines.
 */
const MEPCalc = (function() {
  const STORAGE_KEY = 'mepcalc_project';

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

  const LOCATIONS = [
    {value: '1.00', label: 'National Average'},
    {value: '1.07', label: 'Delaware / Wilmington'},
    {value: '1.12', label: 'New Jersey / Northern'},
    {value: '1.10', label: 'Pennsylvania / Philadelphia'},
    {value: '1.05', label: 'Connecticut'},
    {value: '1.18', label: 'New York City Metro'},
    {value: '1.15', label: 'Boston Metro'},
    {value: '1.08', label: 'Washington DC Metro'},
    {value: '0.92', label: 'Southeast'},
    {value: '0.97', label: 'Midwest'},
    {value: '1.13', label: 'West Coast'},
  ];

  // --- Project State ---
  function getProject() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
    catch(e) { return {}; }
  }

  function saveProject(data) {
    const current = getProject();
    const merged = Object.assign(current, data);
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(merged)); }
    catch(e) {}
    return merged;
  }

  function clearProject() {
    try { localStorage.removeItem(STORAGE_KEY); } catch(e) {}
  }

  function hasProject() {
    const p = getProject();
    return !!(p.name || p.sqft || p.buildingType);
  }

  // --- Project Bar ---
  function renderProjectBar() {
    if (!hasProject()) return;
    const p = getProject();
    const existing = document.getElementById('mepcalc-project-bar');
    if (existing) existing.remove();

    const bar = document.createElement('div');
    bar.id = 'mepcalc-project-bar';
    bar.style.cssText = 'background:#f5f5f5;border-bottom:1px solid #ddd;padding:8px 0;font-size:13px;color:#555;';

    const inner = document.createElement('div');
    inner.style.cssText = 'max-width:1100px;margin:0 auto;padding:0 16px;display:flex;align-items:center;flex-wrap:wrap;gap:8px;';

    const parts = [];
    if (p.name) parts.push('<a href="index.html" style="color:#1a1a1a;font-weight:600;text-decoration:none">' + esc(p.name) + '</a>');
    if (p.sqft) parts.push(fmtNum(p.sqft) + ' SF');
    if (p.buildingType && BUILDING_TYPES[p.buildingType]) parts.push(BUILDING_TYPES[p.buildingType].label);
    if (p.locationLabel) parts.push(esc(p.locationLabel));
    if (p.mepCost) parts.push('MEP: $' + fmtDollar(p.mepCost));

    inner.innerHTML = '<span>' + parts.join(' &nbsp;|&nbsp; ') + '</span>'
      + '<span style="flex:1"></span>'
      + '<a href="#" onclick="MEPCalc.clearProject();MEPCalc.renderProjectBar();location.reload();return false" style="color:#999;font-size:12px;text-decoration:none" title="Clear project">Clear</a>';

    bar.appendChild(inner);
    const header = document.querySelector('header');
    if (header && header.nextSibling) {
      header.parentNode.insertBefore(bar, header.nextSibling);
    } else {
      document.body.prepend(bar);
    }
  }

  // --- Navigation ---
  function continueTo(tool, extraParams) {
    return tool + '.html';
  }

  function renderContinueButtons(container, buttons) {
    if (!container) return;
    const div = document.createElement('div');
    div.style.cssText = 'display:flex;gap:8px;flex-wrap:wrap;margin-top:16px;padding-top:16px;border-top:1px solid #eee;';
    buttons.forEach(function(b) {
      const a = document.createElement('a');
      a.href = b.tool + '.html';
      a.textContent = b.label + ' \u2192';
      a.style.cssText = 'padding:8px 16px;background:#1a1a1a;color:#fff;border-radius:4px;text-decoration:none;font-size:13px;font-weight:600;';
      div.appendChild(a);
    });
    container.appendChild(div);
  }

  // --- Format Helpers ---
  function fmtDollar(n) {
    if (n == null) return '0';
    if (n >= 1000000) return (n / 1000000).toFixed(2) + 'M';
    return Math.round(n).toLocaleString();
  }

  // Alias: MEPCalc.fmt() — spec-named dollar formatter
  function fmt(n) { return fmtDollar(n); }

  function fmtNum(n) {
    if (n == null) return '0';
    return Math.round(n).toLocaleString();
  }

  // MEPCalc.fmtSF() — format with commas + " SF" suffix
  function fmtSF(n) {
    if (n == null) return '0 SF';
    return Math.round(n).toLocaleString() + ' SF';
  }

  function fmtPct(decimal) {
    if (decimal == null) return '0%';
    return (decimal * 100).toFixed(1) + '%';
  }

  function esc(s) {
    const d = document.createElement('div');
    d.textContent = s || '';
    return d.innerHTML;
  }

  // --- Populate Dropdowns ---
  function populateBuildingTypes(selectEl, selected) {
    if (!selectEl) return;
    selectEl.innerHTML = '';
    Object.keys(BUILDING_TYPES).forEach(function(key) {
      const opt = document.createElement('option');
      opt.value = key;
      opt.textContent = BUILDING_TYPES[key].label;
      if (key === selected) opt.selected = true;
      selectEl.appendChild(opt);
    });
  }

  function populateLocations(selectEl, selected) {
    if (!selectEl) return;
    selectEl.innerHTML = '';
    LOCATIONS.forEach(function(loc) {
      const opt = document.createElement('option');
      opt.value = loc.value;
      opt.textContent = loc.label + ' (' + loc.value + ')';
      if (loc.value === selected) opt.selected = true;
      selectEl.appendChild(opt);
    });
  }

  function getLocationLabel(value) {
    const loc = LOCATIONS.find(function(l) { return l.value === value; });
    return loc ? loc.label : '';
  }

  // --- Pre-fill from project state ---
  function prefillFromProject(fieldMap) {
    const p = getProject();
    Object.keys(fieldMap).forEach(function(projectKey) {
      const el = document.getElementById(fieldMap[projectKey]);
      if (el && p[projectKey] != null && p[projectKey] !== '') {
        el.value = p[projectKey];
      }
    });
  }

  // --- Auto-init on DOM ready ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPage);
  } else {
    initPage();
  }

  // --- Liability Disclaimer (renders on every tool page) ---
  function renderDisclaimer() {
    const footer = document.querySelector('footer');
    if (!footer) return;
    const existing = document.getElementById('mepcalc-disclaimer');
    if (existing) return;
    const disc = document.createElement('div');
    disc.id = 'mepcalc-disclaimer';
    disc.style.cssText = 'max-width:900px;margin:0 auto;padding:16px;font-size:11px;color:#999;line-height:1.6;text-align:left;border-top:1px solid #eee;margin-top:8px;';
    disc.innerHTML = '<strong style="color:#777">Important Notice:</strong> MEPCalc tools are for preliminary estimating, feasibility studies, and preconstruction planning only. '
      + 'They are <strong>not a substitute for licensed professional engineering design, code analysis, or legal advice.</strong> '
      + 'All outputs are estimates based on published industry benchmarks and rules of thumb — not project-specific engineering calculations. '
      + 'Building codes (NEC, NFPA, ASHRAE, IMC, IBC) are updated on 3-year cycles and adopted at different times by state and local jurisdictions. '
      + 'Code values shown reflect the editions current at time of publication and <strong>may not match the edition adopted by your Authority Having Jurisdiction (AHJ).</strong> '
      + 'Always verify requirements with the AHJ, confirm all values with a licensed professional engineer, and consult current locally-adopted code editions before making design, construction, or procurement decisions. '
      + 'The creators of MEPCalc assume no liability for decisions made using these tools. '
      + '<br><span style="color:#bbb">Code references as of April 2026. Verify current local adoption.</span>';
    footer.parentNode.insertBefore(disc, footer.nextSibling);
  }

  // --- Auto-init: render project bar + disclaimer on DOM ready ---
  function initPage() {
    renderProjectBar();
    renderDisclaimer();
  }

  // --- Print hide for project bar ---
  const style = document.createElement('style');
  style.textContent = '@media print { #mepcalc-project-bar { display: none !important; } }';
  document.head.appendChild(style);

  // Public API
  return {
    getProject: getProject,
    saveProject: saveProject,
    clearProject: clearProject,
    hasProject: hasProject,
    renderProjectBar: renderProjectBar,
    continueTo: continueTo,
    renderContinueButtons: renderContinueButtons,
    fmt: fmt,
    fmtDollar: fmtDollar,
    fmtNum: fmtNum,
    fmtSF: fmtSF,
    fmtPct: fmtPct,
    populateBuildingTypes: populateBuildingTypes,
    populateLocations: populateLocations,
    getLocationLabel: getLocationLabel,
    prefillFromProject: prefillFromProject,
    BUILDING_TYPES: BUILDING_TYPES,
    LOCATIONS: LOCATIONS,
  };
})();
