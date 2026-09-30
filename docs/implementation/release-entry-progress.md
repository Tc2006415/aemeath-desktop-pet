# DEV-007 implementation and verification

Spec: accepted ADR 0004 (PM 22799b4), superseding DEV-006's tentative timing. Product baseline d80c302; only the ADR commit was cherry-picked, no ART/QA history merged. Execute inline under the authorized task using writing-plans/executing-plans and test-driven-development.

- [x] Loader/player: tests first for schema 1 compatibility, schema 2 optional release entries, strict fields/source/endpoints/bounds, shared bad-image disabling; then preload entries and expose the actual selected frame path. Keep original resource limits and manual base frames.
- [x] Controller/host: tests first for committed-source selection (including an older playback request), 40 ms/unrendered release, 16 deadlines, duplicate end, regrab, mode/package invalidation. Host assigns Image.Source only during Rendering and acknowledges exactly that sample, including package epoch. EndDrag clears motion/capture immediately; one selected release has one instance.
- [x] Candidate verification: consume ART019 fixed manifest with the real loader, inspect all 16 effective paths/deadlines, build local host and run own-process evidence/exit. Default 0.3.0 stays unchanged. Submit fixed code to existing QA/PM and record limits.

Tests use synthetic diagnostic PNGs in temporary directories and the actual player/decoder, never placeholder character art. Only affected suites run. Native mouse/visual checks are pending when native UI APIs are unavailable; Image.Source submission is not a display presentation receipt.

Implementation evidence: loader tests initially had 3 expected schema-2 failures / 3 existing rejection passes; after implementation, schema 1 and new entry tests passed. New controller suite initially failed all 6 tests at the missing submission acknowledgment; implemented effective-path playback and per-controller owned acknowledgments, then green. Final affected-only run: 39 tests passed, none skipped (2026-09-21); includes real ART019 candidate test, schema 1/2 loader, original/new controller and five playback-time tests. Unchanged geometry tests were excluded.

ART019 fixed source: c2f5a71312746990b9e7c715ad67e5e568d97a7c, source/art019-package in ART worktree. Raw manifest SHA256 EAB91ECB10037DA7320D4E9C9321C8DCE0F122D3B9D5DAA6E101A55E1E319DA3. Real loader accepts schema 2, version 0.4.0, 16 images/entries, 20 hold items/1440 ms and 104 total timing items, no disabled actions. Candidate test reaches every source using real candidate base actions and controlled submissions, then exercises every selected entry's effective frame path at each boundary and deadline, one completion and idle return. This is not native mouse input.

Host production changes: only Rendering calls Draw; Image.Source assignment immediately precedes acknowledgment of that exact owned sample. Snapshot includes package epoch, path, source instance/index and submission sequence. Request changes invalidate uncommitted samples while allowing a previously committed older request as a release source. Mode invalidates the saved submission; package changes replace the controller and advance epoch. No input handler samples or paints a new pose. EndDrag stops position/capture before selection and logs source/fallback. Default formal 0.3.0 and assets remain untouched.

## Fixed delivery and reproduction

Implementation commit: `74d84427c4b392d14aff146489acec820654488a`, pushed to `codex/desktop-runtime-proposal`, existing Draft PR #8. ADR-only cherry-pick: `a04a28a`. No formal assets, dependency locks or QA-owned files changed.

Actual commands (PowerShell, repository root):

```powershell
$env:AEMEATH_RELEASE_PACKAGE = 'C:/Users/bigxi/.codex/worktrees/eaf8/桌宠/assets/characters/aemeath-v1/source/art019-package'
& "$env:LOCALAPPDATA/Aemeath/toolchains/dotnet/10.0.401/dotnet.exe" test tests/Aemeath.Presentation.Tests/Aemeath.Presentation.Tests.csproj -c Release --no-restore --filter 'FullyQualifiedName~PackageTests|FullyQualifiedName~ReleaseControllerTests|FullyQualifiedName~CandidateReleaseTests|FullyQualifiedName~CharacterControllerTests|FullyQualifiedName~PlaybackGeometryTests.HalfOpen|FullyQualifiedName~PlaybackGeometryTests.Once|FullyQualifiedName~PlaybackGeometryTests.Replacement|FullyQualifiedName~PlaybackGeometryTests.Missing|FullyQualifiedName~PlaybackGeometryTests.Clock' --logger trx
& ./scripts/build.ps1 -Publish
& ./scripts/smoke-release-entry-host.ps1 -PackageRoot $env:AEMEATH_RELEASE_PACKAGE
& ./scripts/Test-PublishedAssets.ps1 -PublishDirectory (Join-Path $PWD 'artifacts/host-win-x64')
git diff --check
```

Results: affected tests 39/39 passed, 0 skipped; TRX `tests/Aemeath.Presentation.Tests/TestResults/bigxi_SENJO_2026-09-21_22_21_28_net10.0.trx`. Release build emitted 0 warnings/errors and produced the local self-contained host. Own-process smoke rerun (original command output was unavailable after context rollover) passed with PID 29368, exit 0, all 16 entry inventories matching manifest, all 20 hold timing items submitted, package epoch/submission identifiers valid, and pet-stopped/shutdown logged. Evidence: `artifacts/smoke-release-entry.jsonl`. Published asset check: 10 resources, all SHA256 match repository, 0 extras. Whitespace check passed.

Local binary `artifacts/host-win-x64/Aemeath.Host.exe` SHA256: `A84F035ADCCE7E31DB9CE6A3E9EF560612C2BF07C2BC0B2F6CCBB7F9EEDACA1F`. `Aemeath.Host.dll`: `DD192463188726259F10EE3E2A24BACE8E9B9F38BEFC3620D072770EA36597F3`.

Limits/handoff: actual window evidence covers candidate loading and hold Rendering, while all 16 release routes are exercised by the real controller with controlled clock/submission acknowledgments. Native mouse capture, rapid release, lost capture, real regrab and visual continuity remain pending because native UI control is disabled; no alternate input injection was used. No claim of display presentation receipt or full desktop acceptance. QA reported it has no PM task card for this review and has not begun independent review; PM must dispatch that work. Formal default remains 0.3.0. No merge, promotion, public release or next-stage work was performed.
