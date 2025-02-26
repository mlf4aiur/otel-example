#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import time
from flask import Flask, jsonify, request

from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from otel_common import main as otel


app = Flask(__name__)

# Initialize telemetry components
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "flask-app"),
    ResourceAttributes.SERVICE_VERSION: os.getenv("OTEL_SERVICE_VERSION", "0.1.0"),
    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.getenv("OTEL_DEPLOYMENT_ENVIRONMENT", "development")
})

tracer = otel.init_tracer(resource)
meter = otel.init_metrics(resource)
logger = otel.setup_logging(resource)

# Instrument Flask application
FlaskInstrumentor.instrument_app(app, excluded_urls="/health")


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="ok"), 200

@tracer.start_as_current_span("root")
@app.route('/', methods=['GET'])
def root():
    return jsonify(message="Hello Flask"), 200

@tracer.start_as_current_span("rolldice")
@app.route("/rolldice")
def roll_dice():
    player = request.args.get('player', default=None, type=str)
    result = str(roll())
    if player:
        logger.warning("%s is rolling the dice: %s", player, result)
    else:
        logger.warning("Anonymous player is rolling the dice: %s", result)
    return result

def roll():
    return random.randint(1, 6)

@app.route('/slow', methods=['GET'])
def slow():
    start_time = time.time()

    with tracer.start_as_current_span("slow") as span:
        span.set_attribute("endpoint", "/slow")
        logger.info("Starting slow operation")

        delay = random.uniform(0.1, 2.0)
        span.set_attribute("delay", delay)
        time.sleep(delay)

        duration = time.time() - start_time
        logger.info(f"Completed slow operation in {duration:.2f} seconds")
        return jsonify(message=f"Slow response after {delay:.2f} seconds")
