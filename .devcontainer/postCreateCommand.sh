export LOG_LEVEL="INFO"

pip install -r /workspaces/otel-example/fastapi-app/requirements.txt
pip install -r /workspaces/otel-example/flask-app/requirements.txt
opentelemetry-bootstrap -a install
