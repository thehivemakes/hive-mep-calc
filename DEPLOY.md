# MEPCalc — Deploy in 60 Seconds

## Option 1: Netlify Drag & Drop (Fastest)

1. Go to [app.netlify.com](https://app.netlify.com)
2. Drag the entire `/MEPCalc/` folder onto the deploy area
3. Done. All 7 tools live instantly.
4. Optional: set custom domain in Netlify settings

## Option 2: GitHub Pages

1. Create a new repo called `mepcalc` on GitHub
2. Push the contents of `/MEPCalc/` (not the spec files — just the .html, .js, and serve.py)
3. Settings → Pages → Source: main branch, root folder
4. Site will be live at `https://yourusername.github.io/mepcalc`

## Option 3: Any Static Host

Upload these files to any web server:
```
index.html
mepcalc-core.js
rom-estimator.html
general-conditions.html
scope-gap-matrix.html
electrical-room.html
plenum-space.html
healthcare-adder.html
system-sizing.html
```

No build step. No dependencies. No server-side code needed. These are static HTML files that work anywhere.

## Files NOT Needed for Deployment

- `serve.py` — local dev server only
- `DEPLOY.md` — this file
- `BUILD_SPEC_MEPCALC_V2.md` — build spec for the Hive
- `SPEC_V2_UNIFIED_MEPCALC.md` — earlier spec draft

## After Deploy

- Verify all 7 tool links work from the landing page
- Test "Start a Project" flow: enter project info → ROM → General Conditions
- Test Bid Leveling Mode on Scope Gap Matrix
- Check mobile layout on your phone
- Share the URL
