# OpenTelemetry Example

## Overview
This repository demonstrates how to integrate OpenTelemetry with FastAPI and Flask applications. It includes basic setup for distributed tracing, monitoring, and logging using OpenTelemetry.

## Project Structure
```
otel-example/
│-- fastapi-app/      # FastAPI application
│-- flask-app/        # Flask application
│-- otel_common/      # Shared OpenTelemetry configurations
```

## Running the Applications

### Start FastAPI Application
```
uvicorn fastapi-app.main:app --host 0.0.0.0 --port 8000 --reload
```
This will start the FastAPI server on port `8000`.

### Start Flask Application
```
flask --app flask-app.main run --host 0.0.0.0 --port 5000 --reload
```
This will start the Flask server on port `5000`.
