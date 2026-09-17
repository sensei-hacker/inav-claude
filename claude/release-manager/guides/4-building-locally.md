# Phase 4: Building Locally (Optional)

**Read this guide when:** You need to build firmware, SITL, or configurator locally instead of using CI artifacts

**Note:** For most releases, use pre-built artifacts from CI (Phase 2). Only build locally when necessary.

**Related guides:**
- [Phase 2: Downloading Artifacts](2-downloading-artifacts.md)
- [Phase 3: Verifying Artifacts](3-verifying-artifacts.md)

---

## Overview

This guide covers building INAV firmware, SITL binaries, and configurator locally. The **inav-builder** agent handles all build complexities automatically.

---

## Building Firmware

### Using Nightly Builds (Preferred)

Pre-built firmware binaries are available from the nightly build system:

**Nightly Releases:** https://github.com/iNavFlight/inav-nightly/releases

To verify the nightly matches your release commit:

```bash
# Get latest commit on master
cd inav
git log -1 --format="%h %s" HEAD

# Compare with the nightly release description
# Nightly tags follow format: v9.0.0-YYYYMMDD.BUILD_NUMBER
```

The nightly builds include all targets and can be used directly for RC releases instead of building locally.

### Building Locally

Use the **inav-builder** agent for all firmware builds:

```
Task tool with subagent_type="inav-builder"
Prompt: "Build MATEKF405" or "Build all targets"
```

The agent handles cmake configuration, parallel compilation, and error diagnosis automatically.

**⚠️ Important for Releases:** Always use Release mode:
```
"Build MATEKF405 with -DCMAKE_BUILD_TYPE=Release"
```

See `.claude/agents/inav-builder.md` for detailed build commands and troubleshooting.

### Output Location

Firmware hex files are output to: `inav/build/inav_<version>_<TARGET>.hex`

---

## Building SITL Binaries

SITL binaries must be updated in the configurator before tagging.

### When to Build SITL Locally

**Build locally:**
- **Linux x64** - To ensure glibc ≤ 2.35 compatibility

**Use CI artifacts:**
- **Windows** - Needs cygwin1.dll from CI build
- **macOS** - Must be built on macOS
- **Linux arm64** - Unless you have arm64 hardware

### Building SITL Locally

Use the **inav-builder** agent:

```
Task tool with subagent_type="inav-builder"
Prompt: "Build SITL"
```

This ensures:
- Linux binaries meet glibc compatibility requirements (≤ 2.35 for Ubuntu 22.04 LTS)
- Binaries match the exact firmware commit being released

**Build on Ubuntu 22.04 LTS (glibc 2.35) for maximum compatibility.**

### Linux SITL glibc Compatibility Requirement

**CRITICAL:** Linux SITL binaries must be compiled on a system with glibc old enough to support all non-EOL Ubuntu LTS releases.

| Period | Oldest Supported Ubuntu LTS | glibc Version |
|--------|----------------------------|---------------|
| 2025-2027 | Ubuntu 22.04.3 LTS | glibc 2.35 |

**Why this matters:**
- glibc is forward-compatible but NOT backward-compatible
- A binary compiled on Ubuntu 24.04 (glibc 2.39) will fail on Ubuntu 22.04 with errors like:
  ```
  /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.38' not found
  ```
- Users on older (but still supported) Ubuntu LTS releases would be unable to use SITL

**How to verify:**
```bash
# Check glibc version requirements of a binary
objdump -T inav_SITL | grep GLIBC | sed 's/.*GLIBC_//;s/ .*//' | sort -V | tail -1

# Check system glibc version
ldd --version | head -1
```

**Build recommendations:**
- Build on Ubuntu 22.04 LTS or equivalent (glibc 2.35) for maximum compatibility
- Alternatively, use a Docker container with an older base image
- The inav-nightly CI should be configured to build on an appropriate base image

---

## Updating SITL Binaries in Configurator

SITL binaries must be updated before tagging the configurator. They are stored in:

```
inav-configurator/resources/public/sitl/
├── linux/
│   ├── inav_SITL
│   └── arm64/
│       └── inav_SITL
├── macos/
│   └── inav_SITL
└── windows/
    ├── inav_SITL.exe
    └── cygwin1.dll
```

### Download from Nightly

```bash
# Find matching nightly release
gh release list --repo iNavFlight/inav-nightly --limit 5

# Download SITL resources
curl -L -o /tmp/sitl-resources.zip \
  "https://github.com/iNavFlight/inav-nightly/releases/download/<tag>/sitl-resources.zip"
unzip /tmp/sitl-resources.zip -d /tmp/sitl-extract

# Copy to configurator
cd inav-configurator
cp /tmp/sitl-extract/resources/sitl/linux/inav_SITL resources/public/sitl/linux/
cp /tmp/sitl-extract/resources/sitl/linux/arm64/inav_SITL resources/public/sitl/linux/arm64/
cp /tmp/sitl-extract/resources/sitl/macos/inav_SITL resources/public/sitl/macos/
cp /tmp/sitl-extract/resources/sitl/windows/inav_SITL.exe resources/public/sitl/windows/

# Commit
git add resources/public/sitl/
git commit -m "Update SITL binaries for <version>"
```

### Replace Linux x64 with Locally-Built Binary

If you built Linux x64 SITL locally for glibc compatibility:

```bash
cd inav-configurator
cp ../inav/build/inav_SITL resources/public/sitl/linux/
git add resources/public/sitl/linux/inav_SITL
git commit -m "Update Linux x64 SITL binary for glibc 2.35 compatibility"
```

### Create PR and Wait for CI

```bash
# Create branch
git checkout -b update-sitl-9.0.0-RC3

# Push to GitHub
git push origin update-sitl-9.0.0-RC3

# Create PR
gh pr create --title "Update SITL binaries for 9.0.0-RC3" \
  --body "Updates SITL binaries from firmware commit abc123"

# Wait for CI to pass, then merge
```

**After the SITL PR is merged**, the configurator CI will build packages with the updated SITL binaries. Download those artifacts for the release (see Phase 2).

⚠️ **macOS signing:** the release-ready macOS build is code-signed + notarized by `release.yml`, which triggers on a **tag push**. Push the tag only **after** the SITL (and WASM SITL) is merged, and never modify the signed artifacts afterward. See Phase 1's [macOS Signing Sequencing](1-workflow-and-preparation.md#️-macos-signing-sequencing-critical).

### Important Notes

- The `cygwin1.dll` in the Windows folder is a runtime dependency; only update if the build toolchain changes
- SITL binaries are platform-specific and cannot be cross-used
- Linux arm64 binary added in 9.0.0 for ARM-based Linux systems (e.g., Raspberry Pi)
- Linux binaries must support glibc 2.35+ (see glibc compatibility section above)
- Ensure the SITL version matches the firmware version being released
- Test the SITL binaries work before committing (run configurator and try SITL mode)
- The SITL PR triggers CI builds - use those artifacts for the configurator release

---

## Building the WASM SITL + PWA (10.x+)

The browser-based PWA Configurator build bundles an in-browser WASM build of SITL. This is **in addition to** the native per-platform SITL binaries above, not a replacement.

Follow the [WASM SITL + Browser/PWA Build](wasm-sitl-pwa-build.md) guide for the exact commands. In brief:

1. Build the WASM SITL firmware from `feature/wasm-sitl-firmware` (`cmake .. -DTOOLCHAIN=wasm; make SITL`).
2. **Rename** the output (`inav_<ver>_SITL.js`/`.wasm`) to `inav_<ver>_WASM.js`/`.wasm`, copy into `inav-configurator/js/web/WASM/`, and update the hardcoded import in `js/web/SITL-Webassembly.js` for the new firmware version.
3. Commit these alongside the native SITL binaries in the same version-bump PR (Phase 1 step 4) so both are in place before CI.
4. Build the PWA: `yarn web:build` → `dist-web/`.

⚠️ **Same sequencing rule as macOS signing:** the WASM SITL must be in the repo **before** any release CI run that packages or signs the configurator. Do not rebuild or modify the packaged output after the fact.

**Note:** the WASM guide's §3 (pthreads vs. no-pthread, COOP/COEP hosting) is still open — verify before treating the prebuilt binary as production-ready.

---

## Building Configurator

### Using GitHub Actions CI (Preferred)

Pull requests to the configurator repo automatically trigger CI builds for all platforms. **Use these artifacts for releases** instead of building locally.

1. Create/merge a PR (e.g., SITL update PR)
2. Wait for the CI workflow to complete
3. Go to the PR or commit's "Checks" tab
4. Download artifacts from the workflow run:
   - `INAV-Configurator_linux_x64`
   - `INAV-Configurator_macOS`
   - `INAV-Configurator_win_x64`

```bash
# Or use gh CLI to download artifacts from a workflow run
gh run download <run-id> --repo iNavFlight/inav-configurator

# Organize by platform (see Phase 2: Downloading Artifacts)
mkdir -p downloads/configurator-9.0.0-RC3/{linux,macos,windows}
mv INAV-Configurator_linux_x64/* downloads/configurator-9.0.0-RC3/linux/
mv INAV-Configurator_macOS/* downloads/configurator-9.0.0-RC3/macos/
mv INAV-Configurator_win_x64/* downloads/configurator-9.0.0-RC3/windows/
```

**⚠️ NEVER flatten directories** containing multiple platforms together - this can cause cross-platform contamination.

### Building Locally (Fallback)

Only build locally if CI is unavailable.

Use the **inav-builder** agent for all configurator builds:

```
Task tool with subagent_type="inav-builder"
Prompt: "Build configurator" or "Build configurator for Linux"
```

The agent handles npm installation, build configuration, and error diagnosis automatically.

See `.claude/agents/inav-builder.md` for detailed build commands and troubleshooting.

### Output Location

Configurator packages are output to: `inav-configurator/out/make/`

---

## Next Steps

After building locally:

**→ Proceed to [Phase 3: Verifying Artifacts](3-verifying-artifacts.md)** to verify your builds

OR

**→ Return to [Phase 2: Downloading Artifacts](2-downloading-artifacts.md)** if you built SITL and need to update configurator
