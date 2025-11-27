# Fix Changelog

## Problem

The documentation for OpenTelemetry Python SDK stated that `BatchSpanProcessor` is "not fork-safe" and suggested that users must manually reinitialize the tracer provider in post-fork hooks when using fork-based application servers like Gunicorn, uWSGI, or Celery with multi/fork mode.

However, the SDK has actually implemented fork safety support via `os.register_at_fork`, which automatically reinitializes the background worker threads in child processes after a fork. The documentation was outdated and misleading users.

This caused confusion for users, particularly those using Celery with the `multi` command, who thought they needed complex workarounds when in most cases OpenTelemetry works correctly out of the box.

## What Changed

### Documentation Files

1. **docs/examples/fork-process-model/README.rst**
   - Rewrote the introduction to explain that the SDK now has built-in fork safety
   - Added a note about platform support (`os.register_at_fork` on Unix-like systems)
   - Added a new section "Automatic Fork Safety (Recommended)" showing the simple case
   - Added a new section "Celery with Multi/Fork Mode" with specific guidance for Celery users
   - Reorganized existing Gunicorn and uWSGI examples under "Manual Post-Fork Hooks (Advanced)"
   - Clarified when manual post-fork hooks are still needed (per-worker attributes, explicit control, older SDK versions)

### Source Code Documentation

1. **opentelemetry-sdk/src/opentelemetry/sdk/_shared_internal/__init__.py**
   - Updated `BatchProcessor` class docstring to document fork safety
   - Added docstring to `_at_fork_reinit` method explaining its purpose

2. **opentelemetry-sdk/src/opentelemetry/sdk/trace/export/__init__.py**
   - Added "Fork Safety" section to `BatchSpanProcessor` docstring

3. **opentelemetry-sdk/src/opentelemetry/sdk/_logs/_internal/export/__init__.py**
   - Added "Fork Safety" section to `BatchLogRecordProcessor` docstring

4. **opentelemetry-sdk/src/opentelemetry/sdk/metrics/_internal/export/__init__.py**
   - Added "Fork Safety" section to `PeriodicExportingMetricReader` docstring

## Root Cause

The documentation was written before fork safety was implemented in the SDK. The actual implementation uses:

1. `os.register_at_fork(after_in_child=...)` to register a callback that runs in child processes after fork
2. The `_at_fork_reinit` method reinitializes:
   - The export lock (creates a new `threading.Lock()`)
   - The worker awaken event (creates a new `threading.Event()`)
   - Clears the queue (so parent's spans/logs aren't duplicated in child)
   - Starts a new worker thread

This mechanism has been in place and tested, but the documentation never reflected this capability.

## Tests Added or Updated

No new tests were added as the existing test `test_batch_telemetry_record_processor_fork` in `opentelemetry-sdk/tests/shared_internal/test_batch_processor.py` already validates the fork safety functionality for both `BatchSpanProcessor` and `BatchLogRecordProcessor`.

All existing tests pass with the documentation changes.

## Backward Compatibility

This change is fully backward compatible:

1. **No code changes to functionality** - Only documentation and docstrings were updated
2. **Existing workarounds still work** - Users who manually reinitialize in post-fork hooks can continue doing so
3. **New users get simpler path** - Users can now rely on automatic fork safety for most use cases

## Migration Steps

For users experiencing issues with fork-based servers (Gunicorn, uWSGI, Celery multi):

1. **Try the simple approach first**: Configure OpenTelemetry in your main process as usual. The SDK will automatically handle fork safety.

2. **Use manual hooks only if needed**: Only implement post-fork hooks (`post_fork`, `@postfork`, `@worker_process_init.connect`) if you need:
   - Different resource attributes per worker (e.g., worker PID)
   - Explicit control over exporter configuration per worker
   - Compatibility with older SDK versions without fork safety

3. **For Celery specifically**: Use the `worker_process_init` signal if you need per-worker configuration, otherwise rely on automatic fork safety.
