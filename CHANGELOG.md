# CHANGELOG

<!-- version list -->

## v0.2.1 (2026-03-10)

### Bug Fixes

- Suppress pyright reportUnnecessaryIsInstance in BDD inheritance tests
  ([`cfbb18c`](https://github.com/grimlor/actionable-errors/commit/cfbb18cc12a5698ee54eefc95a17a65b3917c7ea))

- **ci**: Push release commit to main alongside tag
  ([`4792615`](https://github.com/grimlor/actionable-errors/commit/4792615b767d4af8978d82475f9c9e1e1f30e359))

### Build System

- Update ruff pre-commit hook from v0.8.6 to v0.15.1
  ([`29c0004`](https://github.com/grimlor/actionable-errors/commit/29c000443ffd36fff7f6f98a5d4632f3f45cf7d0))

### Chores

- Update .gitignore to exclude Copilot work plans and add README for .copilot directory
  ([`6c92902`](https://github.com/grimlor/actionable-errors/commit/6c92902265ed3d503fd4a7d64fb409f14285fa03))

- **config**: Add python upper bound, pyright strict, reportMissingTypeStubs
  ([`7323d4b`](https://github.com/grimlor/actionable-errors/commit/7323d4b9d2fdb61d8a9259a711d2ab2aeffa11eb))

### Code Style

- Add combine-as-imports to ruff isort config
  ([`06f14fd`](https://github.com/grimlor/actionable-errors/commit/06f14fd34cfdb187b8978fb91bbeb84d69f73b94))

### Continuous Integration

- Use step outputs instead of env for coverage percentage
  ([`6cce058`](https://github.com/grimlor/actionable-errors/commit/6cce058beb503e3abef61819fb2ce45dc217d285))


## v0.2.0 (2026-03-09)

### Build System

- Add Copilot skills and instructions from WO gold standard
  ([`d5b6670`](https://github.com/grimlor/actionable-errors/commit/d5b66707a3c331197d9e4db86bce84d8dfcfc354))

- Migrate from mypy to pyright and sync universal skills
  ([`ed0837d`](https://github.com/grimlor/actionable-errors/commit/ed0837d91a8ae2fa49ec0d2c361872e97016b1a8))

- Set major_on_zero = false to prevent premature 1.0.0 bump
  ([`af94266`](https://github.com/grimlor/actionable-errors/commit/af9426629faf00c532067ba7c63df7fe352fb7dc))

- Standardize direnv, gitignore, and add cov task
  ([`25dafb3`](https://github.com/grimlor/actionable-errors/commit/25dafb39f04005220c9906501f097c70de005d2a))

### Chores

- Align pytest config with WO gold standard
  ([`66b0d48`](https://github.com/grimlor/actionable-errors/commit/66b0d4863c150e2829cd3581da5ea7626d8dd599))

- Switch pre-commit mypy to local hook and add .copilot/ to gitignore
  ([`1c177bd`](https://github.com/grimlor/actionable-errors/commit/1c177bde8dda92cc21f2d7b7170a22de7163a7e2))

### Continuous Integration

- Merge publish workflow into release pipeline
  ([`936133c`](https://github.com/grimlor/actionable-errors/commit/936133c5ddde58e3a0a38399c69238545913bac7))

- Retrigger release pipeline
  ([`d8544f8`](https://github.com/grimlor/actionable-errors/commit/d8544f8551541bb50500b6c5f7870b995901a5c4))

- Trigger release pipeline for v0.2.0
  ([`c88fe90`](https://github.com/grimlor/actionable-errors/commit/c88fe90e1e84859d2b073b0104ef50e78824564e))

### Documentation

- Update CONTRIBUTING.md for Python 3.11+ and conventional commits
  ([`2f5f826`](https://github.com/grimlor/actionable-errors/commit/2f5f82649f2cc522c4758a2babff7f2d05f762a6))

### Features

- **classifier**: Add auth keywords for Azure credential errors
  ([`044c443`](https://github.com/grimlor/actionable-errors/commit/044c443c8f5c44f2c445e723b03ef391d8bc126d))

### Testing

- Align BDD compliance in test_error and test_guidance
  ([`e819bb7`](https://github.com/grimlor/actionable-errors/commit/e819bb7fb7b4a55d9c36bd5a4716a52737f4c9e3))


## v0.1.1 (2026-03-03)

### Build System

- Lower Python floor to >=3.11 and add CI version matrix\n\nNo 3.12-specific features are used —
  true floor is 3.11 (StrEnum,\ndatetime.UTC). Updated ruff target-version and mypy
  python_version\nto py311/3.11. CI now tests 3.11, 3.12, and 3.13 in a matrix\n(lint/type/badge
  only on 3.13). Added 3.11 classifier."
  ([`52ff09b`](https://github.com/grimlor/actionable-errors/commit/52ff09b698c26c195f3fced70d5b2860505823ea))

### Continuous Integration

- **release**: Add semantic-release config and automated release workflow
  ([`fc96028`](https://github.com/grimlor/actionable-errors/commit/fc9602806368941ea970f1675c65936bdca8703b))


## v0.1.0 (2026-03-03)

- Initial Release
