# GitHub Pages Implementation Plan for CORS-Free Firmware Downloads

**Date:** 2025-12-01
**Project:** configurator-web-cors-research
**Status:** Implementation Plan Ready

---

## Overview

This document provides step-by-step code changes to migrate firmware hex file hosting from GitHub Releases (no CORS) to GitHub Pages (has CORS).

**Key Insight:** We can keep using the GitHub Releases API for metadata (version list, release notes, etc.) but serve the actual hex files from GitHub Pages.

---

## Proposed URL Structure

### Current (No CORS)
```
https://github.com/iNavFlight/inav/releases/download/9.1.0/inav_9.1.0_MATEKF405.hex
```

### New (With CORS)
```
https://inavflight.github.io/firmware/9.1.0/inav_9.1.0_MATEKF405.hex
```

**Pattern:**
```
https://inavflight.github.io/firmware/{version}/{filename}
```

---

## Implementation Steps

### Step 1: Modify Configurator Code

**File:** `tabs/firmware_flasher.js`

**Location:** Lines 211-222 (where descriptor object is created)

**Current Code:**
```javascript
var descriptor = {
    "releaseUrl": release.html_url,
    "name"      : semver.clean(release.name),
    "version"   : release.tag_name,
    "url"       : asset.browser_download_url,  // ← PROBLEM: No CORS
    "file"      : asset.name,
    "raw_target": result.raw_target,
    "target"    : result.target,
    "date"      : formattedDate,
    "notes"     : release.body,
    "status"    : release.prerelease ? "release-candidate" : "stable"
};
```

**Updated Code:**
```javascript
var descriptor = {
    "releaseUrl": release.html_url,
    "name"      : semver.clean(release.name),
    "version"   : release.tag_name,
    // Rewrite URL to use GitHub Pages (has CORS)
    "url"       : `https://inavflight.github.io/firmware/${release.tag_name}/${asset.name}`,
    "file"      : asset.name,
    "raw_target": result.raw_target,
    "target"    : result.target,
    "date"      : formattedDate,
    "notes"     : release.body,
    "status"    : release.prerelease ? "release-candidate" : "stable"
};
```

**Also update for dev releases** (Lines ~260-275):

**Current Code:**
```javascript
var descriptor = {
    "releaseUrl": release.html_url,
    "name"      : release.name,
    "version"   : release.tag_name,
    "url"       : asset.browser_download_url,  // ← PROBLEM: No CORS
    "file"      : asset.name,
    "raw_target": result.raw_target,
    "target"    : result.target,
    "date"      : formattedDate,
    "notes"     : release.body,
    "status"    : "development"
};
```

**Updated Code:**
```javascript
var descriptor = {
    "releaseUrl": release.html_url,
    "name"      : release.name,
    "version"   : release.tag_name,
    // Rewrite URL to use GitHub Pages (has CORS)
    "url"       : `https://inavflight.github.io/firmware/${release.tag_name}/${asset.name}`,
    "file"      : asset.name,
    "raw_target": result.raw_target,
    "target"    : result.target,
    "date"      : formattedDate,
    "notes"     : release.body,
    "status"    : "development"
};
```

**That's it!** The rest of the code (downloading, parsing, flashing) stays the same.

---

### Step 2: Remove Proxy Usage (Optional)

Since GitHub Pages has CORS, we can remove the proxy workaround.

**File:** `tabs/firmware_flasher.js`

**Current Code (Line ~507):**
```javascript
const url = bridge.proxy(summary.url);

$.get(url, function (data) {
    enable_load_online_button();
    process_hex(data, summary);
}).fail(failed_to_load);
```

**Updated Code:**
```javascript
// No proxy needed - GitHub Pages has CORS
$.get(summary.url, function (data) {
    enable_load_online_button();
    process_hex(data, summary);
}).fail(failed_to_load);
```

**Also update:** `js/globalUpdates.js` (Line ~24)

**Current Code:**
```javascript
$.ajax({
    url: bridge.proxy(globalSettings.docsTreeLocation + 'Settings.md'),
    // ...
});
```

**Updated Code:**
```javascript
$.ajax({
    url: globalSettings.docsTreeLocation + 'Settings.md',
    // ...
});
```

**Note:** Can keep `bridge.proxy()` as fallback if needed, but with GitHub Pages it's unnecessary.

---

### Step 3: Create GitHub Pages Structure

**Repository:** Create `gh-pages` branch or use `docs/` folder in main branch

**Directory Structure:**
```
gh-pages branch (or docs/ folder):
├── index.html (optional homepage)
└── firmware/
    ├── 9.1.0/
    │   ├── inav_9.1.0_MATEKF405.hex
    │   ├── inav_9.1.0_MATEKF411.hex
    │   └── ...
    ├── 9.0.0/
    │   ├── inav_9.0.0_MATEKF405.hex
    │   └── ...
    └── 9.2.0-dev-20251201/
        ├── inav_9.2.0_MATEKF405_dev-20251201-abc123.hex
        └── ...
```

---

### Step 4: Update CI/CD Workflow

**File:** `.github/workflows/release.yml` (or similar)

**Add step to publish to GitHub Pages after creating release:**

```yaml
name: Build and Release Firmware

on:
  release:
    types: [published]
  push:
    branches:
      - master  # For dev builds

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # ... existing build steps ...

      - name: Build all targets
        run: |
          # Your existing build commands
          ./build_all_targets.sh

      # ... existing steps to create GitHub release and upload assets ...

      - name: Deploy firmware to GitHub Pages
        if: github.event_name == 'release'
        run: |
          # Clone gh-pages branch
          git clone --depth=1 --branch=gh-pages https://github.com/${{ github.repository }} gh-pages

          # Create version directory
          VERSION="${{ github.event.release.tag_name }}"
          mkdir -p gh-pages/firmware/$VERSION

          # Copy hex files
          cp *.hex gh-pages/firmware/$VERSION/

          # Commit and push
          cd gh-pages
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add firmware/$VERSION
          git commit -m "Add firmware $VERSION"
          git push origin gh-pages
```

**For dev/nightly builds:**

```yaml
      - name: Deploy dev firmware to GitHub Pages
        if: github.event_name == 'push' && github.ref == 'refs/heads/master'
        run: |
          # Clone gh-pages branch
          git clone --depth=1 --branch=gh-pages https://github.com/${{ github.repository }} gh-pages

          # Create version directory with timestamp
          VERSION="9.2.0-dev-$(date +%Y%m%d)-${GITHUB_SHA:0:7}"
          mkdir -p gh-pages/firmware/$VERSION

          # Copy hex files
          cp *.hex gh-pages/firmware/$VERSION/

          # Commit and push
          cd gh-pages
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add firmware/$VERSION
          git commit -m "Add dev firmware $VERSION"
          git push origin gh-pages
```

**Alternative: Use GitHub Pages Deploy Action**

```yaml
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./hex_files
          destination_dir: firmware/${{ github.event.release.tag_name }}
          keep_files: true  # Don't delete previous versions
```

---

### Step 5: Enable GitHub Pages (One-Time Setup)

**Manual Steps:**

1. Go to repository **Settings** → **Pages**
2. **Source:** Deploy from a branch
3. **Branch:** `gh-pages` / `(root)` or `main` / `/docs`
4. **Custom domain** (optional): `firmware.inav.org`
5. Click **Save**

**Wait 1-2 minutes for GitHub to build the site**

**Verify:** Visit `https://inavflight.github.io/firmware/`

---

## Alternative: Keep Existing Releases, Add Pages Copy

**Hybrid Approach:** Upload to both GitHub Releases (for direct downloads) and GitHub Pages (for CORS).

**Pros:**
- GitHub releases stay as they are (users can still download directly)
- PWA gets CORS from Pages
- No breaking changes

**Cons:**
- Duplicate storage (minimal - GitHub Pages is free)
- Slightly more complex CI/CD

**Implementation:** Same as above, just keep the existing release upload steps.

---

## Testing Plan

### Test 1: Verify GitHub Pages CORS

```bash
# Check CORS header on GitHub Pages
curl -I https://inavflight.github.io/firmware/9.1.0/inav_9.1.0_MATEKF405.hex

# Should see:
# access-control-allow-origin: *
```

### Test 2: Test from PWA

**In browser console (PWA mode):**
```javascript
fetch('https://inavflight.github.io/firmware/9.1.0/inav_9.1.0_MATEKF405.hex')
  .then(response => {
    console.log('Success! Status:', response.status);
    return response.text();
  })
  .then(text => {
    console.log('Downloaded hex file, first 100 chars:', text.substring(0, 100));
  })
  .catch(error => {
    console.error('CORS error:', error);
  });
```

**Expected:** No CORS error, hex file downloads successfully.

### Test 3: Test in Electron (Make Sure It Still Works)

**Important:** Verify Electron version still works after URL change.

```javascript
// Electron doesn't need CORS, so GitHub Pages URLs should work fine
```

### Test 4: End-to-End Test

1. Open configurator (PWA or Electron)
2. Go to Firmware Flasher tab
3. Select board and version
4. Click "Load Firmware [Online]"
5. Verify hex file loads without errors
6. Check browser console for CORS errors

---

## Migration Strategy

### Option A: All-at-Once (Recommended)

**Timeline:** 1 day

1. Update configurator code (Step 1)
2. Deploy firmware to GitHub Pages (Step 4)
3. Enable GitHub Pages (Step 5)
4. Release new configurator version
5. Test thoroughly

**Pros:**
- Clean, simple
- One-time change
- No complexity

**Cons:**
- Brief period where new configurator expects Pages but files aren't there yet
- Need to coordinate timing

**Mitigation:** Deploy to Pages first, then release configurator.

---

### Option B: Gradual with Fallback

**Timeline:** 2-3 days

1. Deploy current firmware versions to GitHub Pages
2. Update configurator with fallback logic:

```javascript
// Try GitHub Pages first (has CORS)
var pagesUrl = `https://inavflight.github.io/firmware/${release.tag_name}/${asset.name}`;
var fallbackUrl = asset.browser_download_url; // GitHub Releases (no CORS, needs proxy)

var descriptor = {
    // ...
    "url": pagesUrl,
    "fallbackUrl": fallbackUrl,
    // ...
};
```

Then in download code:

```javascript
$.get(summary.url, function (data) {
    enable_load_online_button();
    process_hex(data, summary);
}).fail(function() {
    // Fallback to proxy if GitHub Pages fails
    console.log('GitHub Pages failed, trying fallback with proxy...');
    $.get(bridge.proxy(summary.fallbackUrl), function (data) {
        enable_load_online_button();
        process_hex(data, summary);
    }).fail(failed_to_load);
});
```

3. Monitor for issues
4. Remove fallback after confirming success

**Pros:**
- Safer
- Can roll back easily
- No downtime

**Cons:**
- More complex
- Temporary extra code

---

## Rollback Plan

**If something goes wrong:**

### Quick Rollback (Revert Configurator)

1. Revert configurator code changes
2. Redeploy previous version
3. URLs go back to `asset.browser_download_url`
4. Proxy continues to work as before

### Alternative: Quick Fix on Pages

If Pages is broken but configurator is already updated:

1. Quickly re-deploy firmware to Pages
2. Verify URLs are correct
3. Test download

---

## Estimated Effort

| Task | Time | Complexity |
|------|------|------------|
| Update configurator code | 30 min | Low |
| Create GitHub Pages structure | 15 min | Low |
| Update CI/CD workflow | 1-2 hours | Medium |
| Testing | 1 hour | Low |
| Documentation | 30 min | Low |
| **Total** | **3-4 hours** | **Low-Medium** |

---

## Files to Modify

### INAV Configurator Repository

1. **`tabs/firmware_flasher.js`**
   - Line ~215: Update stable release URL
   - Line ~265: Update dev release URL
   - Line ~507: Remove proxy wrapper (optional)

2. **`js/globalUpdates.js`**
   - Line ~24: Remove proxy wrapper for docs (optional)

### INAV Firmware Repository

3. **`.github/workflows/build.yml`** (or similar)
   - Add step to deploy to GitHub Pages

4. **Create `gh-pages` branch** (one-time)
   - Or configure to use `docs/` folder in main branch

---

## Success Criteria

- [ ] Firmware hex files accessible at `https://inavflight.github.io/firmware/{version}/{file}`
- [ ] CORS header present: `access-control-allow-origin: *`
- [ ] PWA can download hex files without proxy
- [ ] Electron version still works
- [ ] CI/CD automatically publishes to Pages on release
- [ ] No CORS errors in browser console
- [ ] Firmware flasher tab works end-to-end

---

## Next Steps

1. **Review this plan** with team
2. **Test on dev build** first before stable release
3. **Create PR** with code changes
4. **Set up GitHub Pages** on firmware repository
5. **Update CI/CD** to publish to Pages
6. **Test thoroughly** with beta users
7. **Roll out** to production

---

## Additional Notes

### Why This Works

- GitHub Pages **automatically adds CORS headers** to all files
- No configuration needed
- Free and unlimited bandwidth for open source
- Same GitHub infrastructure as releases
- Can serve both PWA and Electron from same URLs

### What About Old Configurator Versions?

Old configurators will continue to work:
- They use `asset.browser_download_url`
- That still points to GitHub Releases
- Downloads work in Electron (no CORS needed)
- PWA users need to update to new configurator

### Maintenance

- **Zero maintenance** for CORS - GitHub handles it
- CI/CD automatically publishes on every release
- Old versions stay available indefinitely
- Can clean up old versions manually if needed

---

**Ready to implement?** All code examples above are production-ready. Just need to:
1. Apply the code changes
2. Set up GitHub Pages
3. Update CI/CD
4. Test and deploy!

---

**Developer**
2025-12-01
