# Description

This PR updates the fork-process-model documentation and docstrings to reflect that the OpenTelemetry Python SDK has built-in fork safety support. The existing documentation incorrectly stated that `BatchSpanProcessor` is "not fork-safe," causing confusion for users of fork-based application servers (Gunicorn, uWSGI, Celery with multi/fork mode).

The SDK actually implements fork safety via `os.register_at_fork`, which automatically reinitializes background worker threads in child processes after a fork. This has been implemented and tested, but the documentation was outdated.

## Changes

1. **Updated `docs/examples/fork-process-model/README.rst`**:
   - Rewrote introduction to explain built-in fork safety
   - Added "Automatic Fork Safety (Recommended)" section
   - Added "Celery with Multi/Fork Mode" section with specific guidance
   - Reorganized existing examples under "Manual Post-Fork Hooks (Advanced)"
   - Clarified when manual hooks are still needed

2. **Updated docstrings in source code**:
   - `BatchProcessor` class in `_shared_internal/__init__.py`
   - `BatchSpanProcessor` in `trace/export/__init__.py`
   - `BatchLogRecordProcessor` in `_logs/_internal/export/__init__.py`
   - `PeriodicExportingMetricReader` in `metrics/_internal/export/__init__.py`

Fixes #(related to Celery multi forking issue described in CURRENT_ISSUE.md)

## Type of change

- [x] Bug fix (non-breaking change which fixes an issue)
- [x] This change requires a documentation update

# How Has This Been Tested?

1. **Existing fork tests**: Ran the existing `test_batch_telemetry_record_processor_fork` test which validates fork safety for both `BatchSpanProcessor` and `BatchLogRecordProcessor`:
   ```
   pytest opentelemetry-sdk/tests/shared_internal/test_batch_processor.py -v
   ```
   Result: All 15 tests pass.

2. **RST documentation validation**: Ran `rstcheck` on the updated documentation:
   ```
   rstcheck docs/examples/fork-process-model/README.rst
   ```
   Result: No issues detected.

3. **Code linting**: Ran `ruff check` on all modified Python files:
   ```
   ruff check opentelemetry-sdk/src/opentelemetry/sdk/_shared_internal/__init__.py \
              opentelemetry-sdk/src/opentelemetry/sdk/trace/export/__init__.py \
              opentelemetry-sdk/src/opentelemetry/sdk/_logs/_internal/export/__init__.py \
              opentelemetry-sdk/src/opentelemetry/sdk/metrics/_internal/export/__init__.py
   ```
   Result: All checks passed.

# Does This PR Require a Contrib Repo Change?

- [x] No.

This is a documentation-only change that doesn't affect any API interfaces or configurations that need to be synchronized with the contrib repo.

# Checklist:

- [x] Followed the style guidelines of this project
- [x] Changelogs have been updated (fix_changelog.md created)
- [x] Unit tests have been added (existing tests already cover fork safety)
- [x] Documentation has been updated

# Security Considerations

No security implications. This change only updates documentation to accurately reflect existing functionality.

# Performance Considerations

No performance implications. This change only updates documentation and docstrings.

# Additional Notes

The fix_changelog.md file at the repository root contains a detailed explanation of:
- The problem
- What changed (files, functions)
- Root cause
- Backward compatibility
- Migration steps for users
