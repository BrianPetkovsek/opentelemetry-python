# Fix Changelog

## Problem

The Logging API/SDK documentation lacked important information about end user expectations and usage patterns. Specifically, users were not informed about:

1. **Logger propagation requirement**: Only the root logger is instrumented with the OpenTelemetry `LoggingHandler`, so child loggers must have `propagate=True` (the default) for their log messages to be captured and exported.

2. **Handler preservation with dictConfig**: When using `logging.config.dictConfig()` to configure logging, existing handlers on the root logger may be cleared, including the OpenTelemetry handler. Users need to save and restore the handler to maintain OpenTelemetry log export functionality.

## What Changed

### Files Modified

1. **`docs/examples/logs/README.rst`**
   - Added a new "Important Usage Notes" section with detailed documentation about:
     - Root logger instrumentation behavior
     - Logger propagation requirements
     - Handler preservation when using `logging.config.dictConfig()`
   - Added code examples demonstrating the correct usage patterns
   - Reorganized document with "Basic Setup Example" section header

2. **`docs/examples/logs/example.py`**
   - Added detailed comments explaining:
     - That the handler is attached to the root logger
     - The importance of logger propagation (`propagate=True`)
     - Reference to README.rst for dictConfig usage
     - Explanation of how child loggers propagate to root

3. **`opentelemetry-sdk/src/opentelemetry/sdk/_logs/_internal/__init__.py`**
   - Updated `LoggingHandler` class docstring with comprehensive "Important Usage Notes" section documenting:
     - Logger propagation requirements
     - Handler preservation requirements
     - Code example for handling `dictConfig()` scenarios

## Root Cause

The existing documentation did not explicitly document the behavior of the `LoggingHandler` being attached to the root logger and its implications. This led to potential confusion and issues when users:
- Set `propagate=False` on loggers (preventing log export)
- Used `logging.config.dictConfig()` which cleared the OpenTelemetry handler

## Tests Added or Updated

No new tests were added as this is a documentation-only change. The existing tests continue to pass:
- `tox -e opentelemetry-sdk` - All SDK tests pass
- `tox -e ruff` - All linting checks pass

## Backward Compatibility

This change is fully backward compatible:
- No API changes were made
- No code behavior was modified
- Only documentation was updated to clarify existing behavior

## Migration Steps

No migration steps are required. Users who were experiencing issues with:
- Logs not being exported should verify that `propagate=True` (the default) is set on their loggers
- Logs disappearing after `dictConfig()` should implement the handler preservation pattern documented in the README and class docstring
