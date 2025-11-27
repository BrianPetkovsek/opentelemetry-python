# Description

This PR updates the Logging API/SDK documentation to address user concerns about important usage patterns and expectations. The documentation now clearly explains:

1. **Root logger instrumentation**: The `LoggingHandler` is attached to the root logger, which means child loggers must have `propagate=True` (the default) for their logs to be captured by OpenTelemetry.

2. **Handler preservation with `logging.config.dictConfig()`**: When using `dictConfig()` to configure logging, existing handlers on the root logger may be cleared. Users should save and restore the OpenTelemetry handler to maintain functionality.

These concerns were raised in the issue regarding the stability of the Logging API/SDK.

Fixes the documentation update request from current_issue.md

## Type of change

Please delete options that are not relevant.

- [x] This change requires a documentation update

# How Has This Been Tested?

Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce. Please also list any relevant details for your test configuration

- [x] `tox -e ruff` - All linting checks pass (including rstcheck for RST files)
- [x] `tox -e opentelemetry-sdk` - All SDK tests pass
- [x] `rstcheck --ignore-roles mod,scm_web docs/examples/logs/README.rst` - RST validation passes

# Does This PR Require a Contrib Repo Change?

- [x] No.

# Checklist:

- [x] Followed the style guidelines of this project
- [x] Changelogs have been updated (see fix_changelog.md)
- [x] Unit tests have been added (N/A - documentation only)
- [x] Documentation has been updated

## Additional Notes

### Files Changed

1. `docs/examples/logs/README.rst` - Added "Important Usage Notes" section with detailed documentation
2. `docs/examples/logs/example.py` - Added explanatory comments
3. `opentelemetry-sdk/src/opentelemetry/sdk/_logs/_internal/__init__.py` - Updated `LoggingHandler` class docstring

### Changelog Cross-Reference

See `fix_changelog.md` for detailed information about:
- The problem addressed
- Files and functions changed
- Root cause analysis
- Backward compatibility considerations

### Security Considerations

No security implications - this is a documentation-only change.

### Performance Considerations

No performance implications - this is a documentation-only change.
