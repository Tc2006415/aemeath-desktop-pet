# Character interaction coordination / DEV-004

Implementation plan under ADR 0003, PM baseline `77fa5c0e056e45d8e5c9872195ce86ea91b9e9fd`. Uses writing-plans / executing-plans inline in the existing worktree; no additional task. Scope is the existing Presentation playback and Host input path, not a business-state module or artwork.

## Design and steps

- [x] Add clock-controlled `CharacterController` in Presentation, owning the existing Playback. Commands and sampling read the same injected monotonic millisecond clock. Default manual mode remains neutral/manual selection. Automatic mode enters idle-soft; after 15000 ms since entering idle, plays idle-smile once and returns to idle with a fresh wait. Drag interrupts the wait/smile and resets it.
- [x] Test before implementation: pickup duration from manifest then hold; early release/capture-loss idempotence; re-grab during release; stale instance isolation; missing pickup/hold/release/idle/smile; manual/automatic switching and exact wait boundaries. In-memory synthetic clips are test fixtures only, not character frames.
- [x] Wire successful capture and EndDrag to the controller. Keep an explicit accessible automatic-mode switch and disable manual action controls in that mode. Package reload preserves selected mode but starts a new controller; rejected package still leaves the old one intact. No task completion mapping.
- [x] Build and run actual process diagnostics in automatic mode using the existing diagnostic package. Review fixed commit with the existing QA task, push original branch, record executable path and pending native UI/character checks.

Missing-action choices: pickup missing skips to hold if available, else neutral while captured; hold missing uses neutral while captured; release missing immediately returns to idle-soft (or neutral); missing smile is not repeatedly requested; missing idle-soft uses neutral with no smile timer. No transition waits on a nonexistent completion. All once transitions accept only the current playback instance. Long scheduling gaps do not accumulate smiles.

## Evidence and limits

Implementation and process checks are recorded below. No ART assets, loader limits, shared contracts, state module or PM documents are edited. Upstream manual acceptance is user-reported per ADR 0003; this increment's character visuals, real capture/animation transitions and accessibility remain unverified until explicitly tested. Native UI APIs remain disabled.

Coordinator evidence: new CharacterControllerTests initially RED 8/8 due to unimplemented behavior, then GREEN 8/8 using the real Playback and a controlled clock. Command: dotnet test tests/Aemeath.Presentation.Tests/Aemeath.Presentation.Tests.csproj -c Release --no-restore --filter FullyQualifiedName~CharacterControllerTests --logger trx. Existing loader/geometry tests were not rerun for this unchanged scope.

Host wiring: explicit automatic checkbox, disabled manual action controls in automatic mode, --mode automatic/manual for own-process diagnostics. Default remains manual and diagnostic assets remain unchanged. Successful capture calls BeginDrag; every actual EndDrag path calls EndDrag once; package/mode change cancels capture first. Build/locked restore succeeded with 0 warnings/errors; targeted controller tests remain 8/8 green after host integration. Process smoke pending against the next fixed commit.

## Runtime evidence and use

Code revision `9f0494dbea1aed8ff415b2d5e78a518a9ec4e7ec`: `./scripts/build.ps1 -Publish` completed locked restore, Release build (0 warnings/errors) and self-contained win-x64 directory publish. `./scripts/smoke-character-host.ps1` launched the actual app with the existing `diagnostic-v1/0.1.0` package from a different cwd, ran 18 seconds, and exited 0 (PID 24780). Own diagnostics recorded automatic idle, smile at about 15 seconds after idle entry, its manifest-driven 500 ms duration, one natural-end and return to idle before shutdown. No mouse input was synthesized. The probe now requests `-WindowStyle Hidden` after QA's review; script syntax parsing passed. A hidden-launch request does not establish actual OS visibility or native UI acceptance.

Published code remains 9f0494d; subsequent script/docs-only edits do not alter the binary. Executable: `artifacts/host-win-x64/Aemeath.Host.exe`, with the entire adjacent runtime/assets directory required.

- Executable SHA256: `217C611BFC5FB6B5C320053BC6181BFD773DB8F31BAFA332FD9645C0FDCC43C0`
- Host DLL SHA256: `880887E4F27EF370A1FA9C385F0AC278C967EE315F6B24860C6443B39BD2F9BC`

Open normally, check “自动角色交互”, and drag visible pixels; uncheck to return to manual selection. Alternatively start with `--mode automatic`. Explicit package loading still uses the local directory field or `--package <directory>`; no default character pack is bundled or fabricated. The diagnostic pack lacks all drag clips, so capture uses neutral safely and release immediately returns to idle-soft. Actual pickup/hold/release frames must come from an ART package that passes the unchanged loader.

QA independently reported all 8 new tests and five additional API probe groups passed, including 32 missing-action combinations, switching mode while captured/releasing, one completion and repeated calls. QA completed runtime/input code-path review of 9f0494d with no blocking code finding. Existing loader/geometry suites were intentionally not repeated because they were not changed.

## Remaining acceptance

New mode switch usability, real pickup/hold/release transitions under Windows capture, frame appearance and final character artwork acceptance remain pending. Existing user-reported DEV-003 manual checks do not prove these new actions. First-load broken-assets keyboard behavior and Narrator remain as the upstream pending items. This increment contains no business status, real Codex connection, persistence, new startup registration, public release or default character-package change.

Final QA handoff: independent publish of 9f0494d and Hidden-request process probe passed (PID 17664, exit 0, one natural-end then idle). Own-log observation showed 14999 ms between different instrumentation points; exact 15000 ms behavior is established by controlled-clock boundary tests, not a claim of millisecond-perfect OS scheduling. QA confirmed capture-success ordering, idempotent release before capture-loss reentry, all host EndDrag paths, same-clock use, and capture cancellation before mode switches. Real checkbox/input/character visual acceptance remains pending. Original branch and Draft PR #8 are updated for PM integration; no merge or new task.
