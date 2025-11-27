import logging

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

logger_provider = LoggerProvider(
    resource=Resource.create(
        {
            "service.name": "shoppingcart",
            "service.instance.id": "instance-12",
        }
    ),
)
set_logger_provider(logger_provider)

exporter = OTLPLogExporter(insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

# Set the root logger level to NOTSET to ensure all messages are captured
logging.getLogger().setLevel(logging.NOTSET)

# Attach OTLP handler to root logger.
# IMPORTANT: The handler is attached to the root logger, which means:
# 1. Child loggers must have propagate=True (the default) for their logs
#    to be captured by OpenTelemetry.
# 2. If using logging.config.dictConfig(), save and restore this handler
#    as dictConfig may clear existing handlers. See README.rst for details.
logging.getLogger().addHandler(handler)

# Create different namespaced loggers.
# These loggers propagate to the root logger by default (propagate=True),
# so their logs will be captured by the OpenTelemetry handler.
# It is recommended to not use the root logger with OTLP handler
# so telemetry is collected only for the application.
logger1 = logging.getLogger("myapp.area1")
logger2 = logging.getLogger("myapp.area2")

logger1.debug("Quick zephyrs blow, vexing daft Jim.")
logger1.info("How quickly daft jumping zebras vex.")
logger2.warning("Jail zesty vixen who grabbed pay from quack.")
logger2.error("The five boxing wizards jump quickly.")

# Log custom attributes
# Custom attributes are added on a per event basis
user_id = "user-123"
logger1.error("I have custom attributes.", extra={"user_id": user_id})

# Trace context correlation
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("foo"):
    # Do something
    logger2.error("Hyderabad, we have a major problem.")

logger_provider.shutdown()
