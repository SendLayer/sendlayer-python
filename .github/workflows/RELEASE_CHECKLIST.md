# Release Checklist

Before pushing and publishing a new SDK version, ensure you have completed all of the following steps:

## 1. Versioning
- [ ] Update the version number in the appropriate file:
  - Python: `src/sendlayer/version.py`
- [ ] Ensure the version follows [Semantic Versioning](https://semver.org/).

## 2. Changelog
- [ ] Update the `CHANGELOG.md` with all new features, bug fixes, and breaking changes.
- [ ] Double-check that all changes since the last release are documented.

## 3. Code Quality
- [ ] Run all tests locally and ensure they pass:
  - Python: `pytest`
- [ ] Lint the codebase and fix any issues:
  - Python: `flake8` or `pylint`
- [ ] Review and update documentation as needed (README, docstrings, JSDoc, etc.).

## 4. Dependencies
- [ ] Review and update dependencies if necessary.
- [ ] Ensure there are no security vulnerabilities in dependencies.

## 5. Build
- [ ] Build the package locally to ensure it compiles without errors:
  - Python: `python -m build`

## 6. Test Publishing (Optional but Recommended)
- [ ] Publish to Test PyPI (Python):
  - `twine upload --repository testpypi dist/*`

## 7. Git
- [ ] Commit all changes and push to the main branch.
- [ ] Ensure the latest commit is on `main` and up to date with remote.
- [ ] Tag the release with the version number (the workflow will also do this).

## 8. CI/CD
- [ ] Ensure all GitHub Actions workflows pass (tests, build, publish, etc.).

## 9. Final Publishing
- [ ] Publish to production PyPI (Python):
  - `twine upload dist/*`

## 10. Post-Release
- [ ] Verify the package is available on PyPI registry.
- [ ] Announce the release (GitHub Release, social media, etc.).
- [ ] Monitor for any issues reported by users.

---

