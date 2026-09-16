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

- [ ] Download official SDK ZIP, compare SHA512 with Microsoft release metadata, extract to the versioned user directory; run --info/list-sdks/list-runtimes.
- [ ] Add global.json, solution/projects, ignored build outputs and scripts/build.ps1. Host uses net10.0-windows and an explicit PerMonitorV2 manifest.
- [ ] Create a taskbar-visible diagnostic control window with named Exit/Alt+X and application-wide shutdown. Build Release, start the executable, record only process/own-window evidence; do not claim visual or keyboard acceptance.
- [ ] Commit this independently launchable increment and report its hash.

## Increment 2: behavioral tests first, then presentation/loading

Files: src/Aemeath.Presentation/{Playback,Geometry,PackageLoader}.cs; src/Aemeath.Host/PngDecoder.cs; tests/Aemeath.Presentation.Tests/.

Interfaces: PackageLoader.Load(root, decode) -> validated package (clips, cached pixels, disabled actions/errors); decode accepts already read PNG bytes, returns fixed dimensions/RGBA. Playback.Play(action, now), Sample(now), Cancel(now) -> selected action/frame plus optional completed playback ID. Geometry converts source physical scale to DIP and clamps cursor-minus-captured-offset to a work area.

- [ ] Write failing real-behavior tests for half-open frame boundaries, loop wrap, once return/one notification, cancel/replace, invalid times, 144 DPI geometry and nonzero/negative grab offsets.
- [ ] Write failing loader tests using temporary real files: valid subset, duplicate/unknown metadata, invalid duration/path/limits, bad neutral rejection, shared nonneutral bad PNG disables entire referencing actions. Test real WPF PNG decoding separately rather than mock its validity.
- [ ] Run tests and record expected failures, implement the smallest rules, rerun tests green. Keep generated diagnostic fixtures visibly synthetic; no character generation.
- [ ] Commit tested player/loader/geometry and its test evidence.

Representative independent expectations: durations [100,200] select frame 0 at 99 and frame 1 at 100; once total 300 selects neutral at 300 and emits one completion, never again at 301. 96x104 at k=2/dpi144 gives 192x208 physical and 128x138.6667 DIP. Pointer (410,320) minus captured offset (10,20) gives window origin (400,300).

## Increment 3: transparent window and actual input paths

Files: src/Aemeath.Host/{PetWindow,DiagnosticWindow,NativeMethods,App}.cs; assets/diagnostic/manifest.json and frames; scripts/validate.ps1.

- [ ] Bind preloaded pixels to nearest-neighbor WPF Image. Rendering uses Stopwatch milliseconds; do not load files on animation ticks.
- [ ] Capture mouse on press, store global physical cursor minus window origin, update SetWindowPos on MouseMove, release/cancel idempotently on mouse-up/capture-loss/deactivation/exit. Keep manually selected idle-soft playing during drag.
- [ ] Load/reload packages atomically: retain old valid package on rejection, visibly mark disabled actions, first-load failure leaves control window usable. No task completion mapping.
- [ ] Add bounded opt-in application diagnostics for own HWND/DPI/render/drag/shutdown events. Run build/tests, publish local self-contained directory and launch; report actual evidence separately from pending real UI checks.
- [ ] Final scope/diff review, progress report, commit and push original branch. Leave Draft PR open for PM/QA.

## Actual execution evidence

Pending execution entries are completed below as commands run; unchecked items are not claimed passed.

Increment 1: official SHA512 verified (24b670ad...9430); SDK --info/list-sdks/list-runtimes passed (10.0.401, WindowsDesktop.App 10.0.12). scripts/build.ps1 restore/Release build passed: 0 warnings/0 errors. Normal process launch created a main window handle; CloseMainWindow closed it. This is process lifecycle evidence, NOT native UI inspection/keyboard verification. SDK first-run automatically reported installing an ASP.NET development certificate; no trust command was run.
