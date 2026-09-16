# Diagnostic Host Implementation Plan / DEV-003

Goal: build the accepted Windows 11 x64 diagnostic host, without a state reducer or character assets.

Architecture: Presentation owns package validation, time-based playback and physical-pixel geometry. Host owns WPF decoding, windows, mouse capture, DPI and shutdown. A local diagnostic controller explicitly selects clips; task state remains unknown/unconnected.

Tech stack: C# / WPF / .NET SDK 10.0.401. Specs: ADR 0002, windows-host-v1.md, animation-assets-v1.md. Plan is executed inline using writing-plans/executing-plans; no new tasks or agents.

## Constraints and verification boundary

- ART is the only package format: 96x104, RGBA PNG, anchor (48,94), six allowed action IDs; diagnostic package contains neutral, idle-soft and idle-smile only.
- once returns neutral and ends once; cancellation never raises a stale natural-end event.
- All dimensions are integer physical source-pixel multiples, converted to local DIP only at the host boundary.
- Native CUA APIs are explicitly disabled in this session. Do not use another automation path to bypass that restriction. Build/run and the application's own diagnostics remain available; real mouse, keyboard and visual acceptance require the user/QA on Windows.
- H3, character artwork, persistence, full multi-monitor support and H6 clean-machine acceptance are outside this increment.

## Increment 1: toolchain and launchable shell

- [x] Download official SDK ZIP, compare SHA512 with Microsoft release metadata, extract to the versioned user directory; run --info/list-sdks/list-runtimes.
- [x] Add global.json, solution/projects, ignored build outputs and scripts/build.ps1. Host uses net10.0-windows and an explicit PerMonitorV2 manifest.
- [x] Create a taskbar-visible diagnostic control window with named Exit/Alt+X and application-wide shutdown. Build Release, start the executable, record only process/own-window evidence; do not claim visual or keyboard acceptance.
- [x] Commit this independently launchable increment and report its hash.

## Increment 2: behavioral tests first, then presentation/loading

Files: src/Aemeath.Presentation/{Playback,Geometry,PackageLoader}.cs; src/Aemeath.Host/PngDecoder.cs; tests/Aemeath.Presentation.Tests/.

Interfaces: PackageLoader.Load(root, decode) -> validated package (clips, cached pixels, disabled actions/errors); decode accepts already read PNG bytes, returns fixed dimensions/RGBA. Playback.Play(action, now), Sample(now), Cancel(now) -> selected action/frame plus optional completed playback ID. Geometry converts source physical scale to DIP and clamps cursor-minus-captured-offset to a work area.

- [x] Write failing real-behavior tests for half-open frame boundaries, loop wrap, once return/one notification, cancel/replace, invalid times, 144 DPI geometry and nonzero/negative grab offsets.
- [x] Write failing loader tests using temporary real files: valid subset, duplicate/unknown metadata, invalid duration/path/limits, bad neutral rejection, shared nonneutral bad PNG disables entire referencing actions. Test real WPF PNG decoding separately rather than mock its validity.
- [x] Run tests and record expected failures, implement the smallest rules, rerun tests green. Keep generated diagnostic fixtures visibly synthetic; no character generation.
- [x] Commit tested player/loader/geometry and its test evidence.

Representative independent expectations: durations [100,200] select frame 0 at 99 and frame 1 at 100; once total 300 selects neutral at 300 and emits one completion, never again at 301. 96x104 at k=2/dpi144 gives 192x208 physical and 128x138.6667 DIP. Pointer (410,320) minus captured offset (10,20) gives window origin (400,300).

## Increment 3: transparent window and actual input paths

Files: src/Aemeath.Host/{PetWindow,DiagnosticWindow,NativeMethods,App}.cs; assets/diagnostic/manifest.json and frames; scripts/validate.ps1.

- [x] Bind preloaded pixels to nearest-neighbor WPF Image. Rendering uses Stopwatch milliseconds; do not load files on animation ticks.
- [x] Capture mouse on press, store global physical cursor minus window origin, update SetWindowPos on MouseMove, release/cancel idempotently on mouse-up/capture-loss/deactivation/exit. Keep manually selected idle-soft playing during drag.
- [x] Load/reload packages atomically: retain old valid package on rejection, visibly mark disabled actions, first-load failure leaves control window usable. No task completion mapping.
- [x] Add bounded opt-in application diagnostics for own HWND/DPI/render/drag/shutdown events. Run build/tests, publish local self-contained directory and launch; report actual evidence separately from pending real UI checks.
- [ ] Final scope/diff review, progress report, commit and push original branch. Leave Draft PR open for PM/QA.

## Actual execution evidence

Pending execution entries are completed below as commands run; unchecked items are not claimed passed.

Increment 1: official SHA512 verified (24b670ad...9430); SDK --info/list-sdks/list-runtimes passed (10.0.401, WindowsDesktop.App 10.0.12). scripts/build.ps1 restore/Release build passed: 0 warnings/0 errors. Initial process launch remained alive but immediate MainWindowHandle was zero; close request did not succeed, so the owned smoke process was terminated. Window readiness was not established by this early process probe. This is process lifecycle evidence, NOT native UI inspection/keyboard verification. SDK first-run automatically reported installing an ASP.NET development certificate; no trust command was run.

Increment 2: dotnet test tests/Aemeath.Presentation.Tests/Aemeath.Presentation.Tests.csproj -c Release --logger trx: initial player/geometry RED 8 failed; implementation GREEN 8. Loader/real WPF decoder RED 10 failed with the prior 8 green; final combined GREEN 20/20 (2026-09-16). Includes PNG CRC/alpha/format rejection, shared bad frames, case/path boundaries, exact mathematical integers, retained package on failure. Windows file handles use OPEN_REPARSE_POINT, verified final paths and directory locks. Restore/build succeeded. Corrected .gitignore to retain the preexisting repository patterns. Native UI gates remain pending.

Increment 3: code-based WPF control and transparent pixel window implemented. Native mouse capture/nonmodal movement, idempotent cancellation, static Rendering cleanup, anchor-preserving integer scales, own HWND physical positioning, primary-work-area clamp and display-change fallback are implemented but real input acceptance remains pending. Package reload uses the tested retained-session behavior. No reducer or task-to-animation mapping was added.

`./scripts/validate.ps1 -Publish`: locked restore, Release build (0 warnings/0 errors), 20/20 tests and self-contained win-x64 directory publish succeeded. `./scripts/smoke-host.ps1 -Clip idle-soft -Scale 2` and `-Clip idle-smile -Scale 1` launched that directory from the temporary working directory; both exited 0 via the app's opt-in timed smoke path. Own logs show Rendering callback, loop changes across five cycles and one natural end for the 500 ms once clip. Bad-neutral startup independently emitted control-rendered + package-rejected (no pet-loaded), then shutdown/exit 0. This does not test keyboard or accessibility.

Current display as read by this application: DPI 144. Actual own-window rectangles: k=1 96x104 px / 64x69.333333 DIP; k=2 192x208 px / 128x138.666667 DIP. Client origin minus window origin was (0,0) for both. No system display setting changed. Three local PNGs were opened individually for visual inspection: distinct blue/orange/green grid blocks with 1/2/3 white bars and pink anchor cross, transparent margins; diagnostic-only assets.

## Reproduce and handoff

- Build/test/publish: `./scripts/validate.ps1 -Publish` (SDK path is absolute inside the script; no system PATH dependency).
- Local runnable directory: `artifacts/host-win-x64/`; start `Aemeath.Host.exe` normally for manual checks. Default package resolves relative to the executable, not cwd.
- Optional own diagnostics: `--diagnostics <file> --clip idle-soft --scale 2 --exit-after-ms 3500`. Log parent must exist; logging is off by default and bounded to 2048 entries. CLI timed exit and clip selection are diagnostics, not native input tests. No desktop capture, chat content or real task events are collected.
- Manual checks: select idle-soft, drag visible pixels for two cycles, release outside/cancel, inspect transparent margin and rectangle-outside clicks; switch 1x/2x; use Tab/Enter, Alt+X, Alt+F4 and Narrator to verify exit. Load a rejected package then verify the old valid package persists. Log categories intentionally omit private paths and stack traces.
- QA independently reported baseline 372e38d: locked restore/build + 20 tests, 10 extra contract probes and two actual Windows junction rejections passed. Full window review requested separately against the next fixed commit.
- H1 partial (build/process/render evidence only); H2 native input pending; H4 numeric 144 DPI measurements passed but visual/hit checks pending; H5 loader/first-failure process behavior passed but real keyboard/Narrator pending. H3 not implemented; H6 clean-machine acceptance not performed. No claim that these gates or a release are accepted.
