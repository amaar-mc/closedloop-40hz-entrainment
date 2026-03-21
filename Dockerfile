FROM python:3.11-slim

WORKDIR /app

# Install only what the caregiver app needs
COPY requirements-deploy.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and dependencies
COPY caregiver_app.py .
COPY src/eegnet.py src/eegnet.py
COPY src/__init__.py src/__init__.py
COPY src/streaming/ src/streaming/
COPY temporal_multiscale/model_registry.py temporal_multiscale/model_registry.py
COPY temporal_multiscale/realtime_inference.py temporal_multiscale/realtime_inference.py
COPY temporal_multiscale/multiscale_tcn.py temporal_multiscale/multiscale_tcn.py
COPY temporal_multiscale/__init__.py temporal_multiscale/__init__.py
COPY models/muse_4ch/ models/muse_4ch/
COPY data/caregiver_profiles.json data/caregiver_profiles.json
COPY .streamlit/ .streamlit/

EXPOSE 7860

HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

ENTRYPOINT ["streamlit", "run", "caregiver_app.py", "--server.port=7860", "--server.address=0.0.0.0", "--server.headless=true"]
