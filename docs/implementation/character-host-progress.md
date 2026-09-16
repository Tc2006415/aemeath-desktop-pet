# Character interaction coordination / DEV-004

Implementation plan under ADR 0003, PM baseline `77fa5c0e056e45d8e5c9872195ce86ea91b9e9fd`. Uses writing-plans / executing-plans inline in the existing worktree; no additional task. Scope is the existing Presentation playback and Host input path, not a business-state module or artwork.

## Design and steps

- [ ] Add clock-controlled `CharacterController` in Presentation, owning the existing Playback. Commands and sampling read the same injected monotonic millisecond clock. Default manual mode remains neutral/manual selection. Automatic mode enters idle-soft; after 15000 ms since entering idle, plays idle-smile once and returns to idle with a fresh wait. Drag interrupts the wait/smile and resets it.
- [ ] Test before implementation: pickup duration from manifest then hold; early release/capture-loss idempotence; re-grab during release; stale instance isolation; missing pickup/hold/release/idle/smile; manual/automatic switching and exact wait boundaries. In-memory synthetic clips are test fixtures only, not character frames.
- [ ] Wire successful capture and EndDrag to the controller. Keep an explicit accessible automatic-mode switch and disable manual action controls in that mode. Package reload preserves selected mode but starts a new controller; rejected package still leaves the old one intact. No task completion mapping.
- [ ] Build and run actual process diagnostics in automatic mode using the existing diagnostic package. Review fixed commit with the existing QA task, push original branch, record executable path and pending native UI/character checks.

Missing-action choices: pickup missing skips to hold if available, else neutral while captured; hold missing uses neutral while captured; release missing immediately returns to idle-soft (or neutral); missing smile is not repeatedly requested; missing idle-soft uses neutral with no smile timer. No transition waits on a nonexistent completion. All once transitions accept only the current playback instance. Long scheduling gaps do not accumulate smiles.

## Evidence and limits

Pending. No ART assets, loader limits, shared contracts, state module or PM documents are edited. Upstream manual acceptance is user-reported per ADR 0003; this increment's character visuals, real capture/animation transitions and accessibility remain unverified until explicitly tested. Native UI APIs remain disabled.

Coordinator evidence: new CharacterControllerTests initially RED 8/8 due to unimplemented behavior, then GREEN 8/8 using the real Playback and a controlled clock. Command: dotnet test tests/Aemeath.Presentation.Tests/Aemeath.Presentation.Tests.csproj -c Release --no-restore --filter FullyQualifiedName~CharacterControllerTests --logger trx. Existing loader/geometry tests were not rerun for this unchanged scope.
