#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import random
import time
import httpx
from fastapi import FastAPI

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from otel_common import main as otel


app = FastAPI(title="fastapi-app")

# Initialize telemetry components
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "fastapi-app"),
    ResourceAttributes.SERVICE_VERSION: os.getenv("OTEL_SERVICE_VERSION", "0.1.0"),
    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.getenv("OTEL_DEPLOYMENT_ENVIRONMENT", "development")
})

tracer = otel.init_tracer(resource)
meter = otel.init_metrics(resource)
logger = otel.setup_logging(resource)

# Instrument FastAPI application
FastAPIInstrumentor.instrument_app(app, excluded_urls="/health")

HTTPXClientInstrumentor().instrument()

@app.get("/health")
async def health_check():
    return {"status": "OK"}

@tracer.start_as_current_span("root")
@app.get("/")
async def root():
    logger.info("Processing root request")
    return {"message": "Hello FastAPI"}

@tracer.start_as_current_span("fetch-data")
@app.get("/fetch-data/")
async def fetch_data():
    try:
        async with httpx.AsyncClient() as client:
            logger.info("Sending request to the external service.")
            response = await client.get("http://app:5000/slow")
        response.raise_for_status()

        logger.info(
            f"Received successful response with status code {response.status_code}.")
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting: {e}")
        return {"error": "Request error", "message": str(e)}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        return {"error": "HTTP error", "status_code": e.response.status_code}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": "Unexpected error", "message": str(e)}
