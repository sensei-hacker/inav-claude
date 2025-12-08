# macOS Build Issues Analysis - 9.0.0 Release

**Date:** 2025-12-06
**Release Manager Investigation**

## Issues Reported

1. **Windows .exe file inside Mac dmg**
2. **Mac x64 dmg was damaged**
3. **Mac ARM dmg worked on both ARM and x64 Macs**

---

## Investigation Findings

### Issue 1: How Could a Windows .exe End Up in a Mac DMG?

After reviewing the build configuration and CI workflow, here are the possible causes:

**Potential Causes (in order of likelihood):**

1. **Directory Flattening Error** (SUSPECTED - Most likely)
   - The release process may have involved downloading artifacts from CI and flattening directories:
     ```bash
     find . -mindepth 2 -type f -exec mv -t . {} +
     ```
   - If this command was run in a directory containing BOTH Windows and Mac artifacts, all files would be mixed together
   - The `@electron-forge/maker-dmg` could have inadvertently included files from the wrong platform

2. **Artifact Download Confusion** (POSSIBLE)
   - CI creates separate artifact uploads for each platform:
     - `${{env.BUILD_NAMEx64}}_DMG` (Mac x64 dmg)
     - `${{env.BUILD_NAMEx64}}_ZIP` (Windows x64 zip)
   - If artifacts were downloaded to overlapping directories, files could mix

3. **Build Output Directory Contamination** (UNLIKELY)
   - The forge config (forge.config.js) has a `postMake` hook that renames artifacts
   - If multiple platform builds ran in the same workspace without cleaning, residual files could contaminate the DMG creation
   - However, CI jobs are isolated, making this unlikely

**Verification:**
Looking at the CI workflow (lines 169, 217):
- Mac ARM dmg upload path: `./out/make/*arm64*.dmg`
- Mac x64 dmg upload path: `./out/make/*x64*.dmg`

These glob patterns are safe and shouldn't cross-contaminate. If the issue occurred, it was likely during **manual download and preparation** of release artifacts, though the exact mechanism remains uncertain.

**Prevention:**
- Keep each platform's artifacts in separate directories during download
- Never flatten directories containing multiple platforms together
- Use the download guide's recommended directory structure:
  ```
  downloads/
  ├── configurator-9.0.0/
  │   ├── mac-arm64/
  │   ├── mac-x64/
  │   ├── windows/
  │   └── linux/
  ```

---

### Issue 2 & 3: Mac x64 DMG Damaged, ARM DMG Works on Both Architectures

**Mac ARM64 on Intel Macs (Rosetta 2):**

ARM64 macOS applications CAN run on Intel Macs through Rosetta 2:
- Rosetta 2 automatically translates ARM64 code to x86_64
- The translation is transparent - users don't need to do anything special
- Performance is generally good (though not as fast as native x64)

**Important Timeline:**
- **2025-2027**: Rosetta 2 fully supported
- **macOS 27 (2027)**: Last version with full Rosetta 2 support
- **macOS 28+**: Rosetta 2 will be limited to unmaintained games only

**Why This Matters:**
Since the ARM build works on both architectures via Rosetta 2, and the x64 build was damaged, we might be able to simplify releases by:
1. Only providing ARM64 builds (works on both via Rosetta 2)
2. OR creating Universal binaries (recommended long-term solution)

---

## Electron Build Architecture Options

Based on research, there are three approaches for macOS releases:

### Option 1: ARM64 Only (Current Accidental State)
**Pros:**
- Simplifies build process (one less build job)
- Works on both ARM and Intel Macs via Rosetta 2
- Native performance on Apple Silicon
- Reduces release artifact size/count

**Cons:**
- Slightly slower on Intel Macs (Rosetta 2 overhead ~20-30%)
- Rosetta 2 deprecation in macOS 28 (2027+)
- Users on Intel might expect native builds
- Requires Rosetta 2 installation (usually automatic)

### Option 2: Separate ARM64 and x64 Builds (Current Intent)
**Pros:**
- Native performance on both architectures
- No Rosetta 2 dependency
- Clear choice for users

**Cons:**
- Two separate build jobs (CI time/cost)
- Two separate downloads for Mac users
- Potential for confusion (which one to download?)
- More artifacts to manage in releases

### Option 3: Universal Binary (Industry Standard)
**Pros:**
- Single download for all Mac users
- Native performance on both architectures
- Industry standard (used by Apple, major software)
- Best user experience

**Cons:**
- Requires `@electron/universal` package
- Larger file size (~2x, but compressed DMG reduces this)
- Requires building both architectures first, then merging
- More complex build process

---

## Current INAV Configurator Build Process

**CI Jobs (from .github/workflows/ci.yml):**
- `build-mac-arm64` (line 123): Runs on `macos-15` (ARM)
- `build-mac` (line 171): Runs on `macos-15-intel` (x64)

**Artifacts Produced:**
- `INAV-Configurator_MacOS_arm64_X.Y.Z.dmg`
- `INAV-Configurator_MacOS_arm64_X.Y.Z.zip`
- `INAV-Configurator_MacOS_x64_X.Y.Z.dmg`
- `INAV-Configurator_MacOS_x64_X.Y.Z.zip`

---

## Recommendations

### Short-Term (Next Release - 9.0.1 or 9.1.0)

**Option A: Keep Both Builds, Fix the Process**
1. Keep both ARM64 and x64 builds as-is
2. Improve download guide to prevent artifact mixing
3. Add verification step to check DMG contents before upload
4. Document which build Intel users should download

**Option B: ARM64 Only (Pragmatic)**
1. Disable the x64 Mac build in CI
2. Document that Intel Macs use Rosetta 2
3. Reduces complexity and artifact count
4. Monitor for user complaints about performance

**Recommendation:** **Option A** - Fix the process first, make architectural decisions based on user feedback

### Long-Term (9.2.0 or 10.0.0)

**Implement Universal Binary**
1. Add `@electron/universal` to devDependencies
2. Modify CI workflow to:
   - Build ARM64 version
   - Build x64 version
   - Merge into Universal binary using `@electron/universal`
3. Produce single `INAV-Configurator_MacOS_universal_X.Y.Z.dmg`
4. Industry best practice, best user experience

---

## Action Items for Next Release

### Immediate (Before 9.0.1/9.1.0)
- [ ] Update download guide with strict directory separation
- [ ] Add DMG verification step (check `hdiutil info` before upload)
- [ ] Document the x64 damaged DMG incident
- [ ] Test both ARM and x64 DMGs on Intel and ARM Macs

### Investigation Needed
- [ ] Determine why the x64 DMG was damaged (corrupted during download/upload?)
- [ ] Check if GitHub Actions runners have any known DMG issues on `macos-15-intel`
- [ ] Review logs from the 9.0.0 release build for errors

### Future Enhancement
- [ ] Research `@electron/universal` integration
- [ ] Prototype universal binary build in test PR
- [ ] Benchmark universal binary size vs separate builds
- [ ] Test universal binary on both Intel and ARM Macs

---

## Technical Details

### DMG Verification Commands

Before uploading DMGs, verify contents:

```bash
# Mount the DMG
hdiutil attach INAV-Configurator_MacOS_x64_9.0.0.dmg

# List contents
ls -la /Volumes/INAV-Configurator/

# Check for Windows executables (should be NONE)
find /Volumes/INAV-Configurator/ -name "*.exe"

# Check app bundle architecture
lipo -info "/Volumes/INAV-Configurator/INAV Configurator.app/Contents/MacOS/inav-configurator"

# Unmount
hdiutil detach /Volumes/INAV-Configurator/
```

Expected output for x64 build:
```
Non-fat file: ... is architecture: x86_64
```

Expected output for ARM64 build:
```
Non-fat file: ... is architecture: arm64
```

Expected output for Universal build:
```
Architectures in the fat file: ... are: x86_64 arm64
```

### Directory Structure for Downloads

**CORRECT:**
```
downloads/configurator-9.0.0/
├── mac-arm64/
│   ├── INAV-Configurator_MacOS_arm64_9.0.0.dmg
│   └── INAV-Configurator_MacOS_arm64_9.0.0.zip
├── mac-x64/
│   ├── INAV-Configurator_MacOS_x64_9.0.0.dmg
│   └── INAV-Configurator_MacOS_x64_9.0.0.zip
├── windows/
│   └── ...
└── linux/
    └── ...
```

**INCORRECT (causes mixing):**
```
downloads/configurator-9.0.0/
├── INAV-Configurator_MacOS_arm64_9.0.0.dmg
├── INAV-Configurator_MacOS_x64_9.0.0.dmg
├── INAV-Configurator_Win64_9.0.0.zip  # DANGER: Could get mixed into DMG
└── ...
```

---

## References

- [Electron Forge macOS app for x64 and arm64 - Stack Overflow](https://stackoverflow.com/questions/78135447/electron-forge-macos-app-for-x64-and-arm64)
- [@electron/universal - GitHub](https://github.com/electron/universal)
- [Apple Silicon Support | Electron](https://www.electronjs.org/blog/apple-silicon)
- [If you need to install Rosetta on Mac - Apple Support](https://support.apple.com/en-us/102527)
- [Rosetta (software) - Wikipedia](https://en.wikipedia.org/wiki/Rosetta_(software))

---

## Conclusion

The Windows .exe in Mac DMG was likely caused by improper artifact handling during download/preparation, though the exact mechanism is uncertain. The CI workflows are correctly configured and isolated, suggesting the issue occurred during manual artifact management.

For the Mac architecture question: ARM64 builds DO work on Intel Macs via Rosetta 2, which explains why the ARM DMG worked on both architectures. However, for the best user experience and future-proofing (Rosetta 2 deprecation in 2027), implementing Universal binaries is recommended.

**Immediate action:** Fix the artifact handling process and verify DMG contents before upload.
**Long-term action:** Evaluate moving to Universal binaries for macOS releases.
