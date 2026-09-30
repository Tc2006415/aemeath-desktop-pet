# Diagnostic pixels only

Three synthetic 96x104 RGBA8 PNGs: blue/one bar, orange/two bars, green/three bars. The pink cross marks the fixed (48,94) source anchor. Source pixels include an 8-pixel grid and transparent margins. These are engineering fixtures, not Aemeath artwork or completed character animation.

Reproduce with `node scripts/generate-diagnostic-assets.mjs` from the repository. The loader validates actual PNG bytes; the application uses its output directory's `assets/diagnostic` directory. neutral is static; idle-soft loops 400/200 ms; idle-smile plays 300/200 ms once, then neutral. No drag action or task state is supplied.

Visual inspection and actual Windows input checks are separate from encoding/loader tests. Pending native UI checks are recorded in `docs/implementation/host-progress.md`.
