# Native v2 implementation plan and ledger

Spec: PM ADR005 commit 15b2c32; its accepted top section overrides historical proposal language. Base: 7a28a49. Existing isolated codex/desktop-runtime-proposal worktree; inline execution, no extra tasks/agents. User already confirmed design and execution.

Goal: consume schema3 ART036 0.5.0 explicitly while preserving schema1/2 and the existing default resources. Tech: existing C#/.NET10/WPF, no new dependency.

- [ ] Task 1: failing synthetic schema3 package tests, then BehaviorDefinition/BehaviorParser and PackageLoader integration. Strict fields, 64 keyed paths, exact profile timing/routes/manual actions, limits/SHA/atomic rejection. Verify old package suites and new package suite; commit.
- [ ] Task 2: failing controlled-clock controller tests, then layered scheduler and existing CharacterController façade/PlaybackSample extension. Verify eye collisions/rearming, source-first interaction/late samples/cancellation, manual and old-schema behavior. Integrate PetWindow Rendering/diagnostics; commit.
- [ ] Task 3: consume fixed ART036 with production decoder, all 64 release routes and manual actions, build explicit candidate process smoke, record exact fingerprints/results. Fixed-commit handoff to PM for QA; native mouse/visual checks separately pending if unavailable.

Interfaces: Task1 provides optional immutable BehaviorDefinition on AssetPackage; Task2 consumes it through an AssetPackage controller constructor, keeps old clips constructor and old player. Task2 returns effective path/key/phase on the existing owned sample; PetWindow commits that exact object. Task3 uses the same public façade and fixed candidate. No conflicting contracts found at preflight.

Ruling: keep this scoped implementation document as the persistent plan/ledger instead of introducing a separate tool-generated plan workspace, per PM's allowed own implementation-doc scope. Review remains with the existing QA task via PM; no extra agent/task is created.

Commands use C:/Users/bigxi/AppData/Local/Aemeath/toolchains/dotnet/10.0.401/dotnet.exe, Release, --no-restore and affected test filters. New tests must fail on the missing behavior first; geometry/DPI suites are excluded unless their code changes (not planned).

Task 1 complete: new valid-schema3 tests initially failed 2/2 at the old root-field whitelist; after strict parser implementation, affected package suites passed 21/21 (0 skipped). Task 2 RED: four new controller tests fail at the explicitly unimplemented package constructor, as expected. ART036 fixed 11a30f1 / manifest 95cf8f8102f9631d0a02ae40a46fa497f61d9d423ff350191a399104a0a4b182 is now available for final integration.
