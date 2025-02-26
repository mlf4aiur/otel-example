#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from opentelemetry import metrics
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def init_tracer(resource):
    """Configure and setup the trace provider"""
    trace_exporter = OTLPSpanExporter()
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(tracer_provider)

    return trace.get_tracer(__name__)


def init_metrics(resource):
    """Configure and setup the metrics provider"""
    metrics_exporter = OTLPMetricExporter()
    metric_reader = PeriodicExportingMetricReader(metrics_exporter)
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    return metrics.get_meter(__name__)


def setup_logging(resource):
    """Configure and setup the logger provider"""
    log_exporter = OTLPLogExporter()
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    handler = LoggingHandler(level=logging.INFO,
                             logger_provider=logger_provider)
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.addHandler(handler)
    logging.getLogger().addHandler(handler)
    LoggingInstrumentor().instrument(logger_provider=logger_provider)

    return logging.getLogger(__name__)
