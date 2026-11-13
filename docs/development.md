# Development

Setting up, commit and branch conventions, continuous integration.

Part of the [Granulaire](../README.md) documentation.

## Development

```bash
pip install -e ".[dev]"
pytest            # test suite
ruff check .      # lint
ruff format .     # format
```

### Commits and versions

- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `build:`, `chore:`).
- Versions follow [Semantic Versioning](https://semver.org/). The version
  lives in one place, `pyproject.toml`; `granulaire.__version__` reads it from
  the installed package metadata.
- To release: update `version` in `pyproject.toml`, move the `Unreleased`
  entries of `CHANGELOG.md` under the new version with its date, commit as
  `chore(release): X.Y.Z`, then tag `vX.Y.Z` (annotated). Pre-releases use
  PEP 440 suffixes (`0.2.0b1` for a beta, tag `v0.2.0b1`).

### Branches (GitHub Flow)

The repository follows [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow):

1. `main` is the only long-lived branch and is always releasable. Nobody
   pushes to it directly.
2. Every change starts on a short-lived branch from `main`, named after its
   type: `feat/<name>`, `fix/<name>`, `docs/<name>`, `ci/<name>`, …
3. Push the branch and open a pull request into `main`; CI runs on it.
4. Merge when CI is green, then delete the branch.

Releasing is a change like any other: on a `chore/release-X.Y.Z` branch, bump
`version` in `pyproject.toml` and move the `Unreleased` entries of
`CHANGELOG.md` under the new version; merge the pull request, then tag
`vX.Y.Z` on `main` (or create the release on the GitHub web page with that new
tag). The release workflow builds the packages and attaches them.

A versioned `pre-push` hook refuses direct pushes to `main`. Enable it once per
clone with `git config core.hooksPath .githooks` (emergency override:
`ALLOW_MAIN_PUSH=1 git push`).

On a private repository, GitHub enforces branch protection rules only with
GitHub Pro (or on a public repository). With either, add a rule on `main`:
require a pull request and the CI checks to pass, block force pushes and
deletion.

### Continuous integration

GitHub Actions runs these workflows (`.github/workflows/`):

| Workflow | When | What |
|---|---|---|
| `ci.yml` | every push to `main`, every pull request | `ruff check` and `ruff format --check`; `pytest` on Python 3.11–3.13 (Linux) and 3.12 (macOS, Windows); a command-line smoke test; **the MuJoCo and Blender pile tests, the OpenUSD validators and the Primvaria contract check on every preset**; build the wheel and sdist, `twine check`, install the wheel in a clean environment. The packages are kept as a run artifact for 14 days. |
| `release.yml` | a pushed tag `v*` | checks the tag matches the version in `pyproject.toml`, tests, builds, then creates the GitHub release with the packages attached and the notes taken from `CHANGELOG.md`. Versions with `a`, `b` or `rc` are marked as pre-releases. If the release already exists (created on the web page), the packages are added to it. |
| Dependabot | monthly | pull requests to update the GitHub Actions and the Python dependencies. |

Ruff is pinned in CI so that a new ruff release cannot fail the build on
unchanged code; update the pin and run `ruff format .` together.
