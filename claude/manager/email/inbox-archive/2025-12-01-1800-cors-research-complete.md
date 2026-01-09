# INAV Configurator PWA: CORS Issue Research Report

**Date:** 2025-12-01
**Researched By:** Developer
**Project:** configurator-web-cors-research
**Status:** Research Complete

---

## Executive Summary

The INAV Configurator PWA cannot download firmware hex files from GitHub releases due to Cross-Origin Resource Sharing (CORS) restrictions. GitHub does not send appropriate CORS headers, causing browsers to block requests from the PWA.

**Current Solution:** Cloudflare Worker proxy at `https://proxy.inav.workers.dev/`

**Recommendation:** Adopt **Solution 2 (GitHub Pages/Actions Artifacts)** or **Solution 7 (Cloudflare R2)** for long-term reliability.

---

## Problem Details

### Root Cause

When the INAV Configurator runs as a Progressive Web App (PWA) in a web browser:

1. **Browser enforces same-origin policy** - Requests to different origins require CORS headers
2. **GitHub doesn't send CORS headers** - Their servers don't include `Access-Control-Allow-Origin` headers
3. **Browser blocks the request** - No way for JavaScript to bypass this restriction

### Affected Resources

| Resource Type | Example URL | Used In |
|---------------|-------------|---------|
| **GitHub Releases API** | `https://api.github.com/repos/iNavFlight/inav/releases` | `firmware_flasher.js:318` |
| **Nightly Builds API** | `https://api.github.com/repos/iNavFlight/inav-nightly/releases` | `firmware_flasher.js:305` |
| **Hex File Downloads** | `https://github.com/iNavFlight/inav/releases/download/9.0.0/inav_9.0.0_MATEKF405.hex` | `firmware_flasher.js:509` |
| **Documentation** | `https://github.com/iNavFlight/inav/raw/master/docs/Settings.md` | `globalUpdates.js:24` |

### Technical Background

**What is CORS?**

Cross-Origin Resource Sharing (CORS) is a security mechanism that allows servers to specify who can access their resources from different origins.

**Required Headers** (GitHub doesn't send these):
```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

**Why Electron Works:**

Electron apps don't run in a browser sandbox and can make HTTP requests without CORS restrictions.

---

## Current Solution Analysis

### Implemented: Cloudflare Worker Proxy

**Code Location:** `js/bridge.js:41-48`

```javascript
proxy: function(url) {
    if (this.isElectron) {
        return url;
    } else {
        // Use a cloudflare worker as a proxy to bypass CORS policy
        return `https://proxy.inav.workers.dev/?url=${url}`
    }
}
```

**How It Works:**

1. PWA makes request to `https://proxy.inav.workers.dev/?url=<encoded-github-url>`
2. Cloudflare Worker fetches content from GitHub
3. Worker adds CORS headers to response
4. Browser allows the request (same-origin with proxy)

**Pros:**
- ✅ Already implemented and working
- ✅ Relatively simple
- ✅ Free (Cloudflare Workers free tier: 100k requests/day)
- ✅ Low latency (Cloudflare global network)

**Cons:**
- ❌ External dependency (not under INAV control)
- ❌ Single point of failure
- ❌ Privacy concerns (all downloads go through third-party)
- ❌ Potential rate limiting
- ❌ Who maintains `proxy.inav.workers.dev`?
- ❌ What if it goes down or gets rate-limited?

**Risk Assessment:** **MEDIUM-HIGH**

The proxy owner could:
- Stop maintaining it
- Hit Cloudflare rate limits
- Introduce malicious code (MitM attack)
- Track user downloads

---

## Alternative Solutions

### Solution 1: Maintain Current Cloudflare Worker (Improved)

**Improvement: Document and formalize ownership**

**Actions:**
- Document proxy infrastructure in repository
- Add monitoring/alerting for proxy availability
- Publish Worker source code
- Set up backup proxy URLs

**Implementation Effort:** Low (1-2 hours)

**Pros:**
- ✅ No code changes needed
- ✅ Leverages existing infrastructure
- ✅ Quick to implement

**Cons:**
- ❌ Still has all the risks of current solution
- ❌ Doesn't address fundamental dependency issue

**Cost:** Free (Cloudflare Workers)

**Recommendation:** ⭐⭐ - OK as temporary measure, not ideal long-term

---

### Solution 2: GitHub Pages with CORS Headers

**Approach: Host firmware releases on GitHub Pages with proper CORS**

**Implementation:**

1. **CI/CD Change:** Publish firmware hex files to GitHub Pages on release
2. **Add `_headers` file** (for some hosts) or configure CORS in GitHub Pages settings
3. **Update firmware URLs** to point to GitHub Pages instead of releases

**Example URL Structure:**
```
Before: https://github.com/iNavFlight/inav/releases/download/9.0.0/inav_9.0.0_TARGET.hex
After:  https://inavflight.github.io/firmware/9.0.0/inav_9.0.0_TARGET.hex
```

**GitHub Pages `_headers` file:**
```
/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, OPTIONS
  Access-Control-Allow-Headers: Content-Type
```

**Note:** GitHub Pages might not support custom headers directly. Alternative: Use GitHub Actions to build/deploy to Pages with headers.

**Implementation Effort:** Medium (8-12 hours)

**Pros:**
- ✅ No external dependencies
- ✅ Under INAV organization control
- ✅ Free (GitHub Pages)
- ✅ Reliable (GitHub infrastructure)
- ✅ Proper CORS configuration
- ✅ Can serve both Electron and PWA

**Cons:**
- ❌ Requires CI/CD pipeline changes
- ❌ Need to upload firmware to two places (releases + pages)
- ❌ GitHub Pages may have bandwidth limits for large files
- ❌ GitHub Pages might not support custom CORS headers

**Cost:** Free

**Recommendation:** ⭐⭐⭐⭐ - Good long-term solution if GitHub Pages supports CORS headers

---

### Solution 3: GitHub Actions Artifacts with Public Access

**Approach: Use GitHub Actions artifacts with public URLs**

GitHub Actions now supports **public artifact URLs** that could potentially have CORS enabled.

**Implementation:**

1. Modify CI/CD to publish artifacts as "public"
2. Get public artifact URLs
3. Check if they have CORS headers
4. Update firmware URLs if CORS is supported

**Example:**
```
https://github.com/iNavFlight/inav/actions/runs/123456/artifacts/78910
```

**Implementation Effort:** Low-Medium (4-6 hours)

**Pros:**
- ✅ No external dependencies
- ✅ Integrated with existing CI/CD
- ✅ Free

**Cons:**
- ❌ Unknown if GitHub Actions artifacts support CORS
- ❌ Artifact URLs may be complex/non-permanent
- ❌ May require authentication for access

**Cost:** Free

**Recommendation:** ⭐⭐ - Worth investigating, but uncertain if viable

---

### Solution 4: Public CORS Proxy Services

**Approach: Use public CORS proxy services**

**Examples:**
- `https://cors-anywhere.herokuapp.com/`
- `https://api.allorigins.win/`
- `https://corsproxy.io/`

**Implementation:** Similar to current Cloudflare Worker

**Pros:**
- ✅ Easy to implement
- ✅ No infrastructure to maintain

**Cons:**
- ❌ Unreliable (services go down, rate limits)
- ❌ Privacy/security concerns
- ❌ Not suitable for production
- ❌ Often have strict rate limits

**Cost:** Free (but unreliable)

**Recommendation:** ⭐ - NOT recommended for production use

---

### Solution 5: Self-Hosted Backend API Server

**Approach: Create INAV API server that proxies GitHub requests**

**Architecture:**
```
PWA → https://api.inav.org/firmware/releases → GitHub → API → PWA
```

**Implementation:**

1. Deploy simple Node.js/Python server (e.g., on Vercel, Netlify, Railway)
2. Server fetches from GitHub and adds CORS headers
3. Optionally add caching, analytics, CDN

**Code Example (Node.js):**
```javascript
app.get('/firmware/releases', async (req, res) => {
    const data = await fetch('https://api.github.com/repos/iNavFlight/inav/releases');
    const json = await data.json();

    res.setHeader('Access-Control-Allow-Origin', '*');
    res.json(json);
});
```

**Implementation Effort:** Medium-High (12-16 hours + deployment)

**Pros:**
- ✅ Full control over infrastructure
- ✅ Can add features (caching, analytics, rate limiting)
- ✅ Can optimize response times
- ✅ Professional solution

**Cons:**
- ❌ Requires hosting/infrastructure
- ❌ Ongoing maintenance
- ❌ May have costs depending on traffic
- ❌ Single point of failure (needs monitoring)

**Cost:** $0-50/month depending on hosting provider

**Platforms:**
- **Vercel** (Serverless): Free tier, $20/month after
- **Railway**: ~$5/month
- **Fly.io**: Free tier, ~$3-10/month
- **Cloudflare Workers**: Free tier (100k req/day)

**Recommendation:** ⭐⭐⭐ - Good option if features like caching are valuable

---

### Solution 6: GitHub API with Authentication Tokens

**Approach: Use authenticated GitHub API requests**

**Note:** This doesn't actually solve the CORS problem for raw asset downloads, but worth mentioning.

**Implementation:**

1. Users provide GitHub personal access token
2. Use token for API requests
3. Potentially get higher rate limits

**Pros:**
- ✅ Official GitHub API
- ✅ Higher rate limits

**Cons:**
- ❌ Doesn't solve CORS for hex file downloads (assets)
- ❌ Requires users to create GitHub tokens
- ❌ Complex UX
- ❌ Security risk (storing tokens)

**Recommendation:** ⭐ - Doesn't solve the core problem

---

### Solution 7: Object Storage (Cloudflare R2 / AWS S3 / etc.)

**Approach: Host firmware files on object storage with CORS enabled**

**Implementation:**

1. **CI/CD uploads firmware to object storage** on release
2. **Configure CORS** on bucket/container
3. **Update URLs** in configurator

**Example with Cloudflare R2:**

**CORS Configuration:**
```json
{
  "AllowedOrigins": ["*"],
  "AllowedMethods": ["GET", "HEAD"],
  "AllowedHeaders": ["*"],
  "MaxAgeSeconds": 3600
}
```

**URL Structure:**
```
https://firmware.inav.org/9.0.0/inav_9.0.0_MATEKF405.hex
```

**Implementation Effort:** Medium (6-10 hours + CI/CD setup)

**Pros:**
- ✅ Purpose-built for file hosting
- ✅ Proper CORS support (native)
- ✅ High reliability and performance
- ✅ Global CDN distribution
- ✅ Under INAV control
- ✅ Can serve both Electron and PWA

**Cons:**
- ❌ Ongoing costs (storage + bandwidth)
- ❌ Requires CI/CD pipeline changes
- ❌ Need to manage infrastructure

**Cost Comparison:**

| Provider | Storage (100GB) | Bandwidth (1TB/mo) | Total/Month |
|----------|----------------|--------------------|-------------|
| **Cloudflare R2** | $0.015/GB = $1.50 | FREE egress | **~$1.50** |
| **AWS S3** | $2.30 | $90 | **~$92** |
| **DigitalOcean Spaces** | Included | Included | **$5** (flat) |
| **Backblaze B2** | $0.005/GB = $0.50 | $0.01/GB = $10 | **~$10.50** |

**Recommendation:** ⭐⭐⭐⭐⭐ - **BEST long-term solution** (especially Cloudflare R2 for cost)

---

### Solution 8: Hybrid Approach (GitHub + Fallback Proxy)

**Approach: Try direct GitHub first, fall back to proxy if CORS fails**

**Implementation:**

```javascript
async function fetchWithFallback(url) {
    try {
        // Try direct fetch (works in Electron, fails in PWA)
        const response = await fetch(url);
        return response;
    } catch (corsError) {
        // Fall back to proxy
        const proxyUrl = `https://proxy.inav.workers.dev/?url=${encodeURIComponent(url)}`;
        return await fetch(proxyUrl);
    }
}
```

**Pros:**
- ✅ Best of both worlds
- ✅ No proxy needed for Electron
- ✅ Proxy as backup for PWA

**Cons:**
- ❌ Still relies on external proxy
- ❌ Slightly more complex code
- ❌ Doesn't address fundamental issue

**Recommendation:** ⭐⭐⭐ - Good intermediate solution

---

## Solution Comparison Matrix

| Solution | Reliability | Cost | Control | Effort | Security | Recommended |
|----------|-------------|------|---------|--------|----------|-------------|
| **1. Current Proxy (Improved)** | ⭐⭐ | Free | ❌ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **2. GitHub Pages** | ⭐⭐⭐⭐ | Free | ✅ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **3. GitHub Actions Artifacts** | ⭐⭐⭐ | Free | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **4. Public CORS Proxies** | ⭐ | Free | ❌ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ |
| **5. Self-Hosted API** | ⭐⭐⭐⭐ | $5-20 | ✅ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **6. GitHub API + Auth** | ⭐⭐⭐ | Free | ✅ | ⭐⭐ | ⭐⭐ | ⭐ |
| **7. Object Storage (R2)** | ⭐⭐⭐⭐⭐ | ~$2 | ✅ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **8. Hybrid Fallback** | ⭐⭐⭐ | Free* | ⚠️ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

*Relies on proxy for PWA

---

## Recommendations

### Short-Term (Immediate - 0-2 weeks)

**Recommendation: Solution 1 (Document Current Proxy)**

**Actions:**
1. Document current Cloudflare Worker infrastructure
2. Verify who owns `proxy.inav.workers.dev`
3. Request source code for the Worker
4. Add monitoring for proxy availability
5. Document backup plan if proxy fails

**Effort:** 1-2 hours
**Risk Mitigation:** Low, but addresses immediate concerns

---

### Medium-Term (1-3 months)

**Primary Recommendation: Solution 7 (Cloudflare R2)**

**Why:**
- ✅ Most reliable and scalable
- ✅ Proper CORS support built-in
- ✅ Very low cost (~$1.50/month)
- ✅ Global CDN (fast downloads worldwide)
- ✅ Under INAV organization control
- ✅ Professional infrastructure

**Actions:**
1. Create Cloudflare R2 bucket for firmware hosting
2. Configure CORS policy
3. Modify CI/CD to upload releases to R2
4. Update configurator to fetch from R2
5. Test thoroughly
6. Roll out gradually

**Effort:** 6-10 hours
**Cost:** ~$1.50/month

**Alternative Recommendation: Solution 2 (GitHub Pages)**

If GitHub Pages supports custom CORS headers:

**Actions:**
1. Test if GitHub Pages allows CORS configuration
2. If yes, modify CI/CD to publish to Pages
3. Update configurator URLs

**Effort:** 8-12 hours
**Cost:** Free

**Why Consider This:**
- ✅ Free
- ✅ No external services
- ✅ Integrated with GitHub

**Why It's Alternative, Not Primary:**
- ❌ Unclear if GitHub Pages supports CORS headers
- ❌ May have bandwidth limits
- ❌ Less control than R2

---

### Long-Term (6+ months)

**Recommendation: Solution 5 (Self-Hosted API)**

Consider building a proper INAV API service that:

- Proxies GitHub with CORS
- Caches firmware files (reduces GitHub load)
- Provides analytics (download counts, popular targets)
- Adds features (firmware change notifications, etc.)
- Serves as foundation for future web services

**Tech Stack:**
- Cloudflare Workers (serverless, scales to zero)
- KV Storage (for caching)
- R2 (for firmware hosting)

**Effort:** 12-20 hours initial + ongoing maintenance
**Cost:** $5-10/month

---

## Risk Analysis

### Risks of Current Solution

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Proxy goes offline | Medium | High | Monitor + backup proxy |
| Rate limiting | Medium | Medium | Move to proper hosting |
| Malicious tampering | Low | Critical | Verify Worker source code |
| Performance degradation | Low | Medium | Move to CDN solution |

### Risks of Recommended Solutions

**Cloudflare R2:**
- ✅ Very low risk
- ✅ Enterprise-grade reliability
- ✅ Can migrate if needed

**GitHub Pages:**
- ⚠️ May not support CORS (needs testing)
- ⚠️ Bandwidth limits possible
- ✅ Can fall back to other solutions

---

## Implementation Roadmap

### Phase 1: Immediate (Week 1)

- [ ] Document current proxy infrastructure
- [ ] Verify proxy ownership and access
- [ ] Add proxy monitoring
- [ ] Test proxy failure scenarios
- [ ] Document backup procedures

### Phase 2: Migration Preparation (Week 2-3)

**Option A: Cloudflare R2**
- [ ] Create Cloudflare account/R2 bucket
- [ ] Configure CORS on R2
- [ ] Test file upload/download
- [ ] Test CORS headers from PWA

**Option B: GitHub Pages**
- [ ] Test GitHub Pages CORS capabilities
- [ ] If successful, proceed with implementation
- [ ] If failed, fall back to R2

### Phase 3: CI/CD Integration (Week 4)

- [ ] Modify release workflow to upload to chosen solution
- [ ] Test end-to-end release process
- [ ] Verify firmware files accessible
- [ ] Test CORS from configurator

### Phase 4: Configurator Updates (Week 5)

- [ ] Update firmware URLs in code
- [ ] Implement hybrid fallback (direct + proxy)
- [ ] Test Electron version (ensure still works)
- [ ] Test PWA version

### Phase 5: Testing & Rollout (Week 6)

- [ ] Beta test with community
- [ ] Monitor for issues
- [ ] Gradual rollout
- [ ] Documentation updates

### Phase 6: Cleanup (Week 7)

- [ ] Remove old proxy dependency (if fully migrated)
- [ ] Update documentation
- [ ] Monitor usage and performance
- [ ] Celebrate! 🎉

---

## Technical Specifications

### Required CORS Headers

**Minimum Required:**
```http
Access-Control-Allow-Origin: *
```

**Recommended:**
```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, HEAD, OPTIONS
Access-Control-Allow-Headers: Content-Type, Range
Access-Control-Expose-Headers: Content-Length, Content-Range
Access-Control-Max-Age: 86400
```

### Cloudflare R2 CORS Configuration

```json
{
  "AllowedOrigins": ["*"],
  "AllowedMethods": ["GET", "HEAD", "OPTIONS"],
  "AllowedHeaders": ["*"],
  "ExposeHeaders": ["Content-Length", "Content-Range", "ETag"],
  "MaxAgeSeconds": 86400
}
```

### CI/CD Pseudocode for R2 Upload

```yaml
name: Release Firmware
on:
  release:
    types: [published]

jobs:
  upload-firmware:
    runs-on: ubuntu-latest
    steps:
      - name: Upload to GitHub Releases
        # existing step

      - name: Upload to Cloudflare R2
        env:
          R2_ACCESS_KEY: ${{ secrets.R2_ACCESS_KEY }}
          R2_SECRET_KEY: ${{ secrets.R2_SECRET_KEY }}
          R2_BUCKET: inav-firmware
        run: |
          for hex in *.hex; do
            aws s3 cp "$hex" \
              "s3://$R2_BUCKET/${{ github.ref_name }}/$hex" \
              --endpoint-url https://<account-id>.r2.cloudflarestorage.com
          done
```

---

## Conclusion

The CORS issue is well-understood and has multiple viable solutions. The current Cloudflare Worker proxy is functional but creates external dependencies.

**Recommended Path Forward:**

1. **Immediate:** Document and monitor current proxy
2. **Short-term (1-3 months):** Migrate to **Cloudflare R2** or **GitHub Pages**
3. **Long-term:** Consider self-hosted API for added features

**Primary Recommendation: Cloudflare R2**
- Most reliable
- Very low cost (~$1.50/month)
- Professional infrastructure
- Full control
- Easy to implement

This provides a sustainable, long-term solution for the PWA while maintaining compatibility with the Electron version.

---

**Report Status:** Research Complete
**Next Steps:** Present to team for decision on implementation approach
