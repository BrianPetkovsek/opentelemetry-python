Working With Fork Process Models
================================

The OpenTelemetry SDK has built-in fork safety support for batch processors (``BatchSpanProcessor``,
``BatchLogRecordProcessor``, and ``PeriodicExportingMetricReader``). When a process forks, the SDK
automatically reinitializes the background worker threads in the child process using
``os.register_at_fork``. This means that in most cases, OpenTelemetry will work correctly with
fork-based application servers (Gunicorn, uWSGI, Celery with multi/fork mode) without any
additional configuration.

.. note::
   The built-in fork safety support is available on platforms that support ``os.register_at_fork``
   (Unix-like systems). On Windows, the ``spawn`` multiprocessing method is used instead of ``fork``,
   so this is not applicable.

For most use cases, you can simply use the ``opentelemetry-instrument`` command or programmatically
configure OpenTelemetry in your application, and it will work correctly after forking.

However, there are situations where you might want to manually reinitialize the tracer provider
in each worker process:

1. When you need different resource attributes per worker (e.g., including the worker PID).
2. When you need explicit control over the exporter configuration in each worker.
3. When using older versions of the SDK without fork safety support.

Please see http://bugs.python.org/issue6721 for background on Python locks in (multi)threaded
context with fork.

The source code for the examples with Flask app are available :scm_web:`here <docs/examples/fork-process-model/>`.

Automatic Fork Safety (Recommended)
-----------------------------------

For most applications, simply configure OpenTelemetry before forking and it will work automatically:

.. code-block:: python

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    # Configure once in the main process
    resource = Resource.create(attributes={"service.name": "api-service"})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    span_processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint="http://localhost:4317")
    )
    trace.get_tracer_provider().add_span_processor(span_processor)

    # After forking, the SDK automatically reinitializes worker threads

Celery with Multi/Fork Mode
---------------------------

When using Celery with the ``multi`` command or forking workers, OpenTelemetry works automatically
due to the built-in fork safety. However, if you need per-worker resource attributes, you can
use Celery's worker signals:

.. code-block:: python

    import os
    from celery import Celery
    from celery.signals import worker_process_init

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    app = Celery('tasks', broker='redis://localhost:6379/0')

    @worker_process_init.connect
    def init_tracing(**kwargs):
        # This runs in each worker process after fork
        resource = Resource.create(attributes={
            "service.name": "celery-worker",
            "worker.pid": os.getpid(),
        })

        trace.set_tracer_provider(TracerProvider(resource=resource))
        span_processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint="http://localhost:4317")
        )
        trace.get_tracer_provider().add_span_processor(span_processor)

    @app.task
    def add(x, y):
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("add"):
            return x + y

Manual Post-Fork Hooks (Advanced)
---------------------------------

For advanced use cases where you need explicit control over initialization in forked workers,
you can use the server-specific post-fork hooks as shown below.

Gunicorn post_fork hook
-----------------------

Use this approach if you need per-worker resource attributes or explicit control over configuration:

.. code-block:: python

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor


    def post_fork(server, worker):
        server.log.info("Worker spawned (pid: %s)", worker.pid)

        resource = Resource.create(attributes={
            "service.name": "api-service",
            "worker.pid": worker.pid,  # Include worker-specific attributes
        })

        trace.set_tracer_provider(TracerProvider(resource=resource))
        span_processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint="http://localhost:4317")
        )
        trace.get_tracer_provider().add_span_processor(span_processor)


uWSGI postfork decorator
------------------------

Use this approach if you need per-worker resource attributes or explicit control over configuration:

.. code-block:: python

    import os
    from uwsgidecorators import postfork

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor


    @postfork
    def init_tracing():
        resource = Resource.create(attributes={
            "service.name": "api-service",
            "worker.pid": os.getpid(),  # Include worker-specific attributes
        })

        trace.set_tracer_provider(TracerProvider(resource=resource))
        span_processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint="http://localhost:4317")
        )
        trace.get_tracer_provider().add_span_processor(span_processor)
