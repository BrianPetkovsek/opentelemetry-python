Is your feature request related to a problem?
As part of Logging API/SDK becoming stable, it would help to update the documentation around end use and expectations. Concerns in Sept 2025 with current state were:

only the root logger is instrumented, so seen loggers must have propagate set to True
the root logger is instrumented, so handlers on it must not be cleared and if you are loading logging settings with logging/.config.dictConfig, you must save the root loggers before applying dictConfig, then re-apply missing handlers
Describe the solution you'd like
Update the Logging API/SDK documentation, for example at the readthedocs and at otel.io auto-instrumentation example:

https://opentelemetry-python.readthedocs.io/en/stable/examples/logs/README.html
https://opentelemetry.io/docs/zero-code/python/logs-example/