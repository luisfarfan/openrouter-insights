# CHANGELOG


## v0.6.0 (2026-04-06)

### Chores

* chore: professional-grade library, 98% coverage and robust error handling ([`cfbe004`](https://github.com/luisfarfan/openrouter-insights/commit/cfbe0047aba3f8da59687f98c70ab653875f310c))

### Documentation

* docs: update README with DX features, substitution engine, and 95% test coverage stats ([`0952de5`](https://github.com/luisfarfan/openrouter-insights/commit/0952de5102a1f31c4ee07f3d1d69a4d8edb92b6b))

### Features

* feat: professionalize LLM registry with DX upgrades and high-fidelity reliability

- Promoted 'intelligence_score' and 'is_virtual' to top-level LLMModel properties for easier access.
- Implemented 'Substitution Engine' (get_best_alternative) across all repositories and facades.
- Hardened SyncRegistryUseCase to safely handle non-numeric benchmarks and prevent empty data objects.
- Modernized SQLiteModelRepository using 'session.exec(select())' and '.is_(False)' for SQLModel compliance.
- Ensured 100% test suite stability (63/63 passing) with 95% coverage.
- Resolved all remaining ruff and formatting lints.🦾🤖🚀✨��👣🧹🦾🦾✨🤞🤖🦾🚀🥂 ([`dac0d6b`](https://github.com/luisfarfan/openrouter-insights/commit/dac0d6b76b4d5813df12d243cb2cbb1eb8ab1f79))

* feat: enhance DX with intelligence_score, virtual model filtering, and get_best_alternative substitution engine ([`5ed9b64`](https://github.com/luisfarfan/openrouter-insights/commit/5ed9b64f058b251a93125ab31f65366df3df9836))


## v0.5.1 (2026-04-06)

### Bug Fixes

* fix: update JSON loader for v2.0 format and fix async test decoration ([`15a027b`](https://github.com/luisfarfan/openrouter-insights/commit/15a027b5704344c50df051e81c438a3c918786ad))

### Documentation

* docs: upgrade README with TOC, roadmap and intelligence providers ([`b4212fe`](https://github.com/luisfarfan/openrouter-insights/commit/b4212fe9af6150b92d7dffe0124963e237ac1449))


## v0.5.0 (2026-04-06)

### Chores

* chore: update author metadata to Luis Eduardo Farfan Melgar ([`4b6560d`](https://github.com/luisfarfan/openrouter-insights/commit/4b6560d92ae73721ba51ea6c610fa0461876051a))

### Features

* feat: migrate to openrouter-insights and update author metadata ([`695fda5`](https://github.com/luisfarfan/openrouter-insights/commit/695fda59aa5f6281015b99ae0a985d1726a43726))

### Refactoring

* refactor: implement idempotent JSON export and structured metadata ([`76d26da`](https://github.com/luisfarfan/openrouter-insights/commit/76d26dada07a552ebf17d4e0b03cb1b559fd2861))


## v0.4.0 (2026-04-06)

### Documentation

* docs: modernize README with professional branding, badges, and examples ([`6be554c`](https://github.com/luisfarfan/openrouter-insights/commit/6be554c1487036671c0a1705e6ba7a850c9a2b13))

### Features

* feat: implement daily git-ops sync and professionalize maintainer identity ([`8ebf708`](https://github.com/luisfarfan/openrouter-insights/commit/8ebf708a081cddfd1eb76ab2ea2e97e33bda4d10))


## v0.3.0 (2026-04-06)

### Features

* feat: rename project to openrouter-insights for PyPI publication ([`8e60e39`](https://github.com/luisfarfan/openrouter-insights/commit/8e60e39adb7c126cd7500cdc1d1cbb32de8aa583))


## v0.2.1 (2026-04-06)

### Bug Fixes

* fix: simplify publish step and remove redundant build/rm ([`f9bcf95`](https://github.com/luisfarfan/openrouter-insights/commit/f9bcf95da7ae7a8dfd0ad91ff4c644c61ee701fb))


## v0.2.0 (2026-04-06)

### Bug Fixes

* fix: synchronize poetry.lock with pyproject.toml ([`3ff545a`](https://github.com/luisfarfan/openrouter-insights/commit/3ff545a93037963c7e60bcf3e7283b11bdea758c))

* fix: use official snok/install-poetry action for reliable path ([`098bdaa`](https://github.com/luisfarfan/openrouter-insights/commit/098bdaa1bff1faec0a61967c6b81024a32842ec2))

* fix: run poetry in non-interactive mode for CI/CD ([`2dfb477`](https://github.com/luisfarfan/openrouter-insights/commit/2dfb4778bb3b9740cba970b9c6f2f3039308662a))

### Features

* feat: add comprehensive test suite and integrate with CI/CD ([`cff4072`](https://github.com/luisfarfan/openrouter-insights/commit/cff40721a3e847418251bdc35d44804e8c4d9b5d))


## v0.1.0 (2026-04-06)

### Bug Fixes

* fix: upgrade semantic-release to v9 to resolve debian repo 404 ([`cdf8cad`](https://github.com/luisfarfan/openrouter-insights/commit/cdf8cadab42149e5828d55eb7217e3876681923d))

### Chores

* chore: bump version to 0.2.0 ([`2f71b19`](https://github.com/luisfarfan/openrouter-insights/commit/2f71b19228469358cc6bbefac597615f2d909c59))

* chore: remove database files from repo and update gitignore ([`945e839`](https://github.com/luisfarfan/openrouter-insights/commit/945e839b9ea5a9d6b3890751614c9097964c9e42))

### Documentation

* docs: initial SDD and architecture spec ([`1791e19`](https://github.com/luisfarfan/openrouter-insights/commit/1791e1922ec0cb722b04bb64c91014782e99c625))

### Features

* feat: add fully automated CI/CD for python-semantic-release and PyPI ([`ad35dd6`](https://github.com/luisfarfan/openrouter-insights/commit/ad35dd6961d0f1c3d4c0c8a3fca6f0ff2600fab4))

* feat: llm registry ([`84610c6`](https://github.com/luisfarfan/openrouter-insights/commit/84610c69799b1c7cea72e5e7620efc54b25c6e19))

* feat: implement high-fidelity API Query Engine with SQLite persistence ([`6650e44`](https://github.com/luisfarfan/openrouter-insights/commit/6650e447705936c495e4a8f0124ba441c2eae838))

* feat: scaffold backend infrastructure and api ([`96fbda7`](https://github.com/luisfarfan/openrouter-insights/commit/96fbda7b43680de905e0eaf03142dae00204a02a))

* feat: domain layer implementation (entities and interfaces) ([`d97c185`](https://github.com/luisfarfan/openrouter-insights/commit/d97c1855b896bebe08eabe044fdf20c50d2ea32c))

### Testing

* test: unit tests for domain entities ([`2da2660`](https://github.com/luisfarfan/openrouter-insights/commit/2da2660aad80eec2e4b368efc21f4b41a6b3478a))

### Unknown

* Convert LLMIndex to a feature-rich library with dual sync/async support and smart query methods ([`1d12e58`](https://github.com/luisfarfan/openrouter-insights/commit/1d12e587aa068366f20e35176299946fa04bac3a))

* init: project setup with poetry and tools ([`7f2c332`](https://github.com/luisfarfan/openrouter-insights/commit/7f2c332b34241934667f1881cb6615fbb119f676))
