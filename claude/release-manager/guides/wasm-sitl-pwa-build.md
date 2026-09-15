# WASM SITL + Browser/PWA Build (Not Yet in Standard Release Flow)

**Read this guide when:** You need to build/package the browser-based PWA Configurator build, which bundles an in-browser WASM build of SITL. This is separate from and in addition to the native per-platform SITL binaries copied into `inav-configurator/resources/public/sitl/{linux,macos,windows}/` for desktop packaging — that existing step is unaffected.

**Status as of 2026-09-01:** Feature not yet merged. Firmware: `inav` branch `feature/wasm-sitl-firmware` (not in master/maintenance-10.x). Configurator: PR #2729, branch `merge-2693-2722-best-of`. Verify current branch/merge status before using this guide.

**Open blocker:** GitHub Pages COOP/COEP hosting gap — see Manager task `claude/manager/email/inbox/2026-08-31-2339-task-request-github-pages-coop-coep-wasm-sitl.md`. Don't assume this is resolved; check status first.

---

## 1. Build WASM SITL firmware

Requires Emscripten SDK (`EMSDK` env var set, or `~/emsdk` present).

```bash
cd inav
git checkout feature/wasm-sitl-firmware   # verify current location first — may have merged elsewhere
mkdir -p build_wasm && cd build_wasm
source ~/emsdk/emsdk_env.sh
cmake .. -DTOOLCHAIN=wasm
make SITL
```

Produces `inav_<FIRMWARE_VERSION>_SITL.js` / `.wasm` in `build_wasm/`.

## 2. Copy into Configurator — rename required

`inav-configurator/js/web/SITL-Webassembly.js` has a **hardcoded static import** expecting `_WASM.js`/`.wasm`, but the build output is named `_SITL.js`/`.wasm`. You must **rename**, not just copy, to:

```
inav-configurator/js/web/WASM/inav_<FIRMWARE_VERSION>_WASM.js
inav-configurator/js/web/WASM/inav_<FIRMWARE_VERSION>_WASM.wasm
```

**Version-bump trap:** the import path is a static string. On any firmware version bump, this breaks at build time — you must edit `SITL-Webassembly.js` to match the new filename, not just rename the copied files. Not yet fixed to be version-agnostic.

## 3. pthreads / COOP-COEP — verify before trusting either path

- The binary **currently checked into the Configurator repo** (from PR #2722) was built **with pthreads** (uses `SharedArrayBuffer`), which requires `Cross-Origin-Opener-Policy: same-origin` + `Cross-Origin-Embedder-Policy: require-corp` on every response. GitHub Pages can't set these headers — hence the open Manager blocker above.
- `feature/wasm-sitl-firmware`'s current `cmake/sitl.cmake` has pthreads **disabled** ("Phase 5 MVP" comment) — a fresh build from that branch would not need SharedArrayBuffer or COOP/COEP at all, which would make the GitHub Pages gap moot **if it works**.
- **Not yet verified**: whether a fresh no-pthread build actually works with `js/web/SITL-Webassembly.js` / `js/connection/connectionExt.js`. Only the pthread prebuilt has been tested. Before treating no-pthread as the production answer: build fresh (§1), swap in (§2), smoke-test (§4). Report the result back — it can close or reprioritize the Manager's GitHub Pages task either way.

## 4. Build and test the PWA

```bash
cd inav-configurator
yarn install       # if needed
yarn web:build      # vite build --config vite.web.config.js
```

Output: `inav-configurator/dist-web/` (fully wiped and regenerated each run — safe to re-run). **No packaging/zip step exists yet** — don't assume a format if one is needed for release.

Local verification:

```bash
yarn web:build
yarn web:preview --port 4173
```

Open `http://localhost:4173` in a real browser (not Electron) → SITL tab → start WASM SITL → connect via port picker's "SITL" entry.

**Testing gotchas:**
- Service worker (`registerType: "prompt"`) caches aggressively and won't auto-update on reload. Use an Incognito window, or hard-reload + manually unregister the service worker, when re-testing after a rebuild.
- `SharedArrayBuffer`/`crossOriginIsolated` errors mean you're on the pthread-enabled binary and need COOP/COEP headers. `vite.web.config.js`'s dev/preview server blocks already set these for local testing — that does not cover production hosting (§3).

## Reference

- Project history: `claude/projects/active/compare-browser-configurator-implementations/todo.md`, Phase 5 section
- Open blocker: `claude/manager/email/inbox/2026-08-31-2339-task-request-github-pages-coop-coep-wasm-sitl.md`
- PR: inav-configurator #2729, branch `merge-2693-2722-best-of`
- Source: Developer email, 2026-09-01
