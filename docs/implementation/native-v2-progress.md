# Native v2 implementation plan and ledger

Spec: PM ADR005 commit 15b2c32; its accepted top section overrides historical proposal language. Base: 7a28a49. Existing isolated codex/desktop-runtime-proposal worktree; inline execution, no extra tasks/agents. User already confirmed design and execution.

Goal: consume schema3 ART036 0.5.0 explicitly while preserving schema1/2 and the existing default resources. Tech: existing C#/.NET10/WPF, no new dependency.

- [x] Task 1: failing synthetic schema3 package tests, then BehaviorDefinition/BehaviorParser and PackageLoader integration. Strict fields, 64 keyed paths, exact profile timing/routes/manual actions, limits/SHA/atomic rejection. Verify old package suites and new package suite; commit.
- [x] Task 2: failing controlled-clock controller tests, then layered scheduler and existing CharacterController façade/PlaybackSample extension. Verify eye collisions/rearming, source-first interaction/late samples/cancellation, manual and old-schema behavior. Integrate PetWindow Rendering/diagnostics; commit.
- [x] Task 3: consume fixed ART036 with production decoder, all 64 release routes and manual actions, build explicit candidate process smoke, record exact fingerprints/results. Fixed-commit handoff to PM for QA; native mouse/visual checks separately pending if unavailable.

Interfaces: Task1 provides optional immutable BehaviorDefinition on AssetPackage; Task2 consumes it through an AssetPackage controller constructor, keeps old clips constructor and old player. Task2 returns effective path/key/phase on the existing owned sample; PetWindow commits that exact object. Task3 uses the same public façade and fixed candidate. No conflicting contracts found at preflight.

Ruling: keep this scoped implementation document as the persistent plan/ledger instead of introducing a separate tool-generated plan workspace, per PM's allowed own implementation-doc scope. Review remains with the existing QA task via PM; no extra agent/task is created.

Commands use C:/Users/bigxi/AppData/Local/Aemeath/toolchains/dotnet/10.0.401/dotnet.exe, Release, --no-restore and affected test filters. New tests must fail on the missing behavior first; geometry/DPI suites are excluded unless their code changes (not planned).

Task 1 complete: new valid-schema3 tests initially failed 2/2 at the old root-field whitelist; after strict parser implementation, affected package suites passed 21/21 (0 skipped). Task 2 RED: four new controller tests fail at the explicitly unimplemented package constructor, as expected. ART036 fixed 11a30f1 / manifest 95cf8f8102f9631d0a02ae40a46fa497f61d9d423ff350191a399104a0a4b182 is now available for final integration.

Task 2 complete: controller RED 4/4 at missing package constructor, then new/old controller tests 18/18 passed. Corrected two test expectations using the frozen modulo-1400 wing/hem phase (4000→B/light,4140→A/light); production phase was correct. Real candidate loaded unchanged; all64 route binding test first failed at explicit BindRelease stub, then passed with production binder used by scheduler. Final affected run 48/48, 0 skipped; TRX bigxi_SENJO_2026-09-29_17_29_31_net10.0.trx includes schema1/2/new package, old/new controller, five player tests, ART019 and ART036. Manual six actions checked with actual candidate. 64 exhaustive routes are production binding/player tests; controller ownership/cancellation uses actual candidate sampled submissions on reachable phase examples, never invented external snapshots.

## Fixed implementation and exact verification

Code commits: `c608fa1` parser and `c9bac870d5a19c0b43dc6ff140f997e8d351ea62` controller/host/tests/smoke, pushed to existing codex/desktop-runtime-proposal. Scope diff from 7a28a49 contains only allowed Presentation/Host, corresponding tests, this document and explicit-package smoke script. No PNG, manifest, dependencies, locks, shared ADR or default packaging changes. PM owns integration and independent QA dispatch; no extra agent/task created.

Actual PowerShell commands from this worktree:

```powershell
$env:AEMEATH_V2_PACKAGE='C:/Users/bigxi/.codex/worktrees/eaf8/桌宠/assets/characters/aemeath-v1/source/art036-package'
$env:AEMEATH_RELEASE_PACKAGE='C:/Users/bigxi/.codex/worktrees/eaf8/桌宠/assets/characters/aemeath-v1/source/art019-package'
& "$env:LOCALAPPDATA/Aemeath/toolchains/dotnet/10.0.401/dotnet.exe" test tests/Aemeath.Presentation.Tests/Aemeath.Presentation.Tests.csproj -c Release --no-restore --filter 'FullyQualifiedName~PackageTests|FullyQualifiedName~ControllerTests|FullyQualifiedName~CandidateTests|FullyQualifiedName~CandidateReleaseTests|FullyQualifiedName~PlaybackGeometryTests.HalfOpen|FullyQualifiedName~PlaybackGeometryTests.Once|FullyQualifiedName~PlaybackGeometryTests.Replacement|FullyQualifiedName~PlaybackGeometryTests.Missing|FullyQualifiedName~PlaybackGeometryTests.Clock' --logger trx
& "$env:LOCALAPPDATA/Aemeath/toolchains/dotnet/10.0.401/dotnet.exe" publish src/Aemeath.Host/Aemeath.Host.csproj -c Release -r win-x64 --self-contained true --no-restore -p:PublishTrimmed=false -p:PublishSingleFile=false -o artifacts/native-v2-win-x64
& ./scripts/smoke-native-v2-host.ps1 -PackageRoot $env:AEMEATH_V2_PACKAGE
Get-FileHash artifacts/native-v2-win-x64/Aemeath.Host.exe,artifacts/native-v2-win-x64/Aemeath.Host.dll,artifacts/native-v2-win-x64/Aemeath.Presentation.dll -Algorithm SHA256
git diff --cached --check
```

Results: test command exit0, 48 passed/0 failed/0 skipped; publish exit0, self-contained output created with no warnings/errors printed. Actual ART036 commit `11a30f1ce32f973f02fedc85a29b20326b3ea151`, manifest SHA256 `95CF8F8102F9631D0A02AE40A46FA497F61D9D423FF350191A399104A0A4B182`, schema3/package0.5.0/profile layered-idle-drag-v1. Production parser/decoder accepted all64 registered PNG, 45 combinations, 64 routes/5 tails, six manual actions and no disabled actions; all64 bound sequences match ART035 source/timing/path assertions and complete once at540ms.

Task 3 process evidence: smoke exit0. Automatic run PID17244 (idle and blink), manual wink PID56248 (all four base frames and one completion), manual release PID54016 (all five base frames and one completion); each exited0 and logged render-callback, valid submitted key/path/epoch/sequence, pet-stopped, shutdown. Files: `artifacts/smoke-v2-automatic.jsonl`, `artifacts/smoke-v2-manual-wink.jsonl`, `artifacts/smoke-v2-manual-release.jsonl`. Candidate manifest fingerprint unchanged after runs.

| Built file under artifacts/native-v2-win-x64 | SHA256 |
| --- | --- |
| Aemeath.Host.exe | 9C266D8E594D5CD1D63AF8C81252302C2FE2EFBF85AA332946A4BED9B78208DE |
| Aemeath.Host.dll | C33F8E0CB167B466A7F660705F9B622A7B2A606EDC5CD00BA2DD44994DBC7610 |
| Aemeath.Presentation.dll | 6872A2184688B30D47EDBB4DD5F375E5F04C7CEA27EF1DF395145EA902C1D385 |

Use the explicit candidate argument shown above. This output is a dedicated developer probe, not a promoted default distribution: bundled default resource configuration remains this DEV branch's previous configuration, while PM's formal package remains0.4.0. Neither old output directory nor PM formal resources were replaced.

## Review and remaining acceptance

Author reviewed parser references/atomic rejection, shared manual/automatic instance IDs, input-to-submission ownership, phase boundaries and host capture-end ordering. PM received fixed commits and process evidence for independent review by the existing QA task; independent approval is not yet claimed. Ruling above is the only process deviation; the two test expectation corrections used frozen phase values, not a product-behavior change. No known deferred code finding was identified in this author pass.

Native mouse capture, rapid release/lost capture/focus/Escape, regrab and visual continuity remain pending: native UI control is unavailable. Controlled clock/submission tests and process logs are not native mouse/visual evidence. Existing hand/readability, wink/hem reset seams, finite-frame transitions and wing transparent points remain disclosed; no art changes were attempted. Random wink cadence is covered deterministically in tests; the short automatic process smoke covers blink, and the separate manual process covers wink frames, not a full random-wait native observation. No DPI suite rerun, default promotion, merge, floating, task integration, persistence, autostart or public release.

Handoff: PM can cherry-pick the two implementation commits and documentation follow-up onto its current integration base, then dispatch/complete fixed-candidate QA and human Windows acceptance. Do not merge ART branch history; candidate consumption remains selective and explicit.
