#!/usr/bin/env python3
"""
MEPCalc Code Edition Monitor
Checks for building code/standard updates that may affect MEPCalc tools.

Run manually:    python3 code_monitor.py
Run scheduled:   python3 code_monitor.py --cron
                 (Add to crontab: 0 9 1 * * cd /path/to/MEPCalc && python3 code_monitor.py --cron)

Checks NFPA, NEC, and ASHRAE publication pages for new editions.
Outputs alerts to stdout and optionally to a log file.
"""

import json
import os
import sys
import datetime
import urllib.request
import urllib.error
import re
from pathlib import Path

# --- Configuration ---

LOG_FILE = Path(__file__).parent / "code_monitor_log.json"

# Standards tracked by MEPCalc tools, with known edition info.
# "current_edition" = edition MEPCalc was built against (April 2026).
# "next_expected" = year the next edition is expected.
# "check_urls" = pages to scrape for new edition announcements.
STANDARDS = {
    "NEC (NFPA 70)": {
        "current_edition": "2023",
        "mepcalc_built_against": "2023",
        "next_expected": 2029,
        "cycle_years": 3,
        "tools_affected": ["electrical-room.html", "system-sizing.html", "healthcare-adder.html"],
        "check_urls": [
            "https://www.nfpa.org/codes-and-standards/nfpa-70-standard-development/70",
        ],
        "keywords": ["2029", "2026", "new edition", "next edition"],
        "notes": "NEC 2026 published late 2025. MEPCalc references 2023 edition values. DE/NJ/CT on 2020, PA on 2017.",
    },
    "NFPA 13 (Sprinklers)": {
        "current_edition": "2025",
        "mepcalc_built_against": "2022",
        "next_expected": 2028,
        "cycle_years": 3,
        "tools_affected": ["system-sizing.html"],
        "check_urls": [
            "https://www.nfpa.org/codes-and-standards/nfpa-13-standard-development/13",
        ],
        "keywords": ["2028", "new edition", "next edition", "revision"],
        "notes": "Head spacing values (130 SF ordinary hazard) from NFPA 13. Critical life-safety data.",
    },
    "NFPA 99 (Healthcare Facilities)": {
        "current_edition": "2024",
        "mepcalc_built_against": "2024",
        "next_expected": 2027,
        "cycle_years": 3,
        "tools_affected": ["healthcare-adder.html"],
        "check_urls": [
            "https://www.nfpa.org/codes-and-standards/nfpa-99-standard-development/99",
        ],
        "keywords": ["2027", "new edition", "next edition"],
        "notes": "CMS enforces 2012 edition. State adoption varies widely.",
    },
    "NFPA 110 (Emergency Power)": {
        "current_edition": "2025",
        "mepcalc_built_against": "2022",
        "next_expected": 2028,
        "cycle_years": 3,
        "tools_affected": ["healthcare-adder.html", "system-sizing.html"],
        "check_urls": [
            "https://www.nfpa.org/codes-and-standards/nfpa-110-standard-development/110",
        ],
        "keywords": ["2028", "new edition", "next edition"],
        "notes": "Generator sizing references. Many AHJs still on 2016 or 2019.",
    },
    "ASHRAE 90.1 (Energy)": {
        "current_edition": "2022",
        "mepcalc_built_against": "2022",
        "next_expected": 2025,
        "cycle_years": 3,
        "tools_affected": ["system-sizing.html"],
        "check_urls": [
            "https://www.ashrae.org/technical-resources/standards-and-guidelines/read-only-versions-of-ashrae-standards",
        ],
        "keywords": ["90.1-2025", "new edition", "published"],
        "notes": "DOE determination on 90.1-2022 triggers state adoption requirement by early 2026.",
    },
    "ASHRAE 170 (Healthcare Ventilation)": {
        "current_edition": "2025",
        "mepcalc_built_against": "2021",
        "next_expected": 2029,
        "cycle_years": 4,
        "tools_affected": ["healthcare-adder.html"],
        "check_urls": [
            "https://www.ashrae.org/technical-resources/standards-and-guidelines/read-only-versions-of-ashrae-standards",
        ],
        "keywords": ["170-2029", "170-2025", "new edition"],
        "notes": "4-year cycle aligned with FGI guidelines. ACH rates for patient rooms.",
    },
    "ASHRAE 62.1 (Ventilation)": {
        "current_edition": "2025",
        "mepcalc_built_against": "2022",
        "next_expected": 2028,
        "cycle_years": 3,
        "tools_affected": ["system-sizing.html", "plenum-space.html"],
        "check_urls": [
            "https://www.ashrae.org/technical-resources/standards-and-guidelines/read-only-versions-of-ashrae-standards",
        ],
        "keywords": ["62.1-2028", "new edition"],
        "notes": "Referenced by IMC. Baseline ventilation rates.",
    },
}

# Target jurisdictions for adoption tracking
JURISDICTIONS = {
    "Delaware": {"nec_adopted": "2020", "ashrae901_adopted": "2016"},
    "New Jersey": {"nec_adopted": "2020", "ashrae901_adopted": "2019"},
    "Connecticut": {"nec_adopted": "2020", "ashrae901_adopted": "2019"},
    "Pennsylvania": {"nec_adopted": "2017", "ashrae901_adopted": "2016"},
}


def load_log():
    """Load previous check results."""
    if LOG_FILE.exists():
        try:
            return json.loads(LOG_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            pass
    return {"checks": [], "alerts": []}


def save_log(log):
    """Save check results."""
    # Keep only last 24 months of entries
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=730)).isoformat()
    log["checks"] = [c for c in log["checks"] if c.get("timestamp", "") > cutoff]
    log["alerts"] = [a for a in log["alerts"] if a.get("timestamp", "") > cutoff]
    LOG_FILE.write_text(json.dumps(log, indent=2))


def fetch_page(url, timeout=15):
    """Fetch a URL and return text content. Returns None on failure."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "MEPCalc-CodeMonitor/1.0 (building-code-update-checker)"
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, TimeoutError) as e:
        return None


def check_standard(name, config):
    """Check a single standard for updates. Returns list of alert strings."""
    alerts = []
    now = datetime.datetime.now()

    # Time-based check: is the next edition expected soon or overdue?
    next_yr = config["next_expected"]
    if now.year >= next_yr:
        alerts.append(
            f"[TIME] {name}: Next edition was expected in {next_yr}. "
            f"MEPCalc was built against {config['mepcalc_built_against']} edition. "
            f"Check if a new edition has been published and review affected tools: "
            f"{', '.join(config['tools_affected'])}"
        )
    elif now.year == next_yr - 1:
        alerts.append(
            f"[UPCOMING] {name}: Next edition expected in {next_yr} "
            f"(current: {config['current_edition']}). Plan review of: "
            f"{', '.join(config['tools_affected'])}"
        )

    # Web check: scan publication pages for keywords
    for url in config.get("check_urls", []):
        page = fetch_page(url)
        if page is None:
            alerts.append(f"[FETCH FAILED] {name}: Could not reach {url}")
            continue

        page_lower = page.lower()
        for keyword in config.get("keywords", []):
            if keyword.lower() in page_lower:
                # Extract surrounding context (100 chars)
                idx = page_lower.find(keyword.lower())
                snippet = page[max(0, idx-50):idx+len(keyword)+50]
                snippet = re.sub(r'\s+', ' ', snippet).strip()
                alerts.append(
                    f"[KEYWORD] {name}: Found '{keyword}' on {url} — "
                    f'context: "...{snippet}..."'
                )
                break  # One match per URL is enough

    return alerts


def check_jurisdiction_adoption():
    """Flag if known adoption dates are getting stale (>3 years old)."""
    alerts = []
    now = datetime.datetime.now()
    for state, data in JURISDICTIONS.items():
        nec_yr = int(data["nec_adopted"])
        if now.year - nec_yr >= 6:
            alerts.append(
                f"[ADOPTION] {state}: Still recorded as NEC {nec_yr} "
                f"({now.year - nec_yr} years behind current). "
                f"Check if the state has adopted a newer edition."
            )
    return alerts


def generate_report(all_alerts):
    """Format alerts into a readable report."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"{'='*70}",
        f"  MEPCalc Code Edition Monitor — {now}",
        f"{'='*70}",
        "",
    ]

    if not all_alerts:
        lines.append("  No alerts. All standards appear current.")
        lines.append("  Next check recommended in 30 days.")
    else:
        lines.append(f"  {len(all_alerts)} alert(s) found:\n")
        for i, alert in enumerate(all_alerts, 1):
            lines.append(f"  {i}. {alert}")
            lines.append("")

    lines.extend([
        f"{'='*70}",
        "  Standards monitored: " + ", ".join(STANDARDS.keys()),
        "  Jurisdictions tracked: " + ", ".join(JURISDICTIONS.keys()),
        "  MEPCalc build date: April 2026",
        f"  Log file: {LOG_FILE}",
        f"{'='*70}",
    ])

    return "\n".join(lines)


def main():
    is_cron = "--cron" in sys.argv
    is_quiet = "--quiet" in sys.argv

    log = load_log()
    all_alerts = []

    if not is_quiet:
        print("MEPCalc Code Monitor — checking standards...\n")

    for name, config in STANDARDS.items():
        if not is_quiet:
            print(f"  Checking {name}...", end=" ", flush=True)
        alerts = check_standard(name, config)
        all_alerts.extend(alerts)
        if not is_quiet:
            print(f"{'(' + str(len(alerts)) + ' alerts)' if alerts else 'OK'}")

    if not is_quiet:
        print(f"  Checking jurisdiction adoption...", end=" ", flush=True)
    adoption_alerts = check_jurisdiction_adoption()
    all_alerts.extend(adoption_alerts)
    if not is_quiet:
        print(f"{'(' + str(len(adoption_alerts)) + ' alerts)' if adoption_alerts else 'OK'}")

    # Log this run
    log["checks"].append({
        "timestamp": datetime.datetime.now().isoformat(),
        "alert_count": len(all_alerts),
        "mode": "cron" if is_cron else "manual",
    })
    if all_alerts:
        log["alerts"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "alerts": all_alerts,
        })
    save_log(log)

    report = generate_report(all_alerts)
    print("\n" + report)

    # Non-zero exit if alerts found (useful for cron notification)
    if all_alerts:
        sys.exit(1)


if __name__ == "__main__":
    main()
