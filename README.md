# EdgeRareClip

EdgeRareClip is an edge-first anomaly detection platform for industrial computer vision. It brings inference closer to cameras and production equipment to reduce latency and upstream traffic while preserving centralized monitoring and fleet management.

> **Status:** The repository is currently in the architecture bootstrap phase. It contains the initial module layout and integration contracts. The production TensorRT models, business logic, database schema, and dashboard behavior will be delivered incrementally.

## Technical Goals

- Run near-real-time anomaly inference on Jetson Nano with TensorRT.
- Estimate visual rarity and update an online memory bank.
- Publish events through MQTT, buffer them locally during outages, and synchronize after recovery.
- Provide a FastAPI service for anomalies, device health, feedback, and metrics.
- Expose an operational React dashboard with anomaly feeds, heatmaps, device health, and performance indicators.
- Share data models, configuration, logging, metrics, and utilities through `shared/`.

## Architecture

```text
Camera -> Edge capture/preprocess -> TensorRT inference -> Postprocess
                                                |
                              Local SQLite buffer <- MQTT -> Backend
                                                               |
                                  PostgreSQL <- Services/API <- WebSocket
                                                               |
                                                        React Dashboard
```

### Components

| Component | Responsibility | Primary technologies |
| --- | --- | --- |
| `edge/` | Camera capture, preprocessing, inference, and health heartbeat on Jetson | Python, OpenCV/GStreamer, TensorRT, MQTT |
| `backend/` | API, business services, anomaly persistence, and fleet management | FastAPI, async SQLAlchemy, PostgreSQL |
| `frontend/` | Monitoring and configuration dashboard | React, TypeScript, Vite, Zustand |
| `shared/` | Shared Pydantic models, configuration, logging, metrics, and utilities | Python |
| `infra/` | MQTT broker, Prometheus, Grafana, and deployment scripts | Docker, Prometheus, Grafana |

## Repository Layout

- `shared/`: Python package shared by the edge and backend applications.
- `edge/`: Jetson Nano pipeline; TensorRT engines are stored in `edge/models/`.
- `backend/`: FastAPI server, MQTT subscriber, services, and migrations.
- `frontend/`: React dashboard.
- `infra/`: Observability and deployment configuration.
- `docs/`: [architecture](docs/architecture.md), [API reference](docs/api_reference.md), and [deployment guide](docs/deployment_guide.md).

## Prerequisites

- Python 3.11 or later.
- Node.js 22 or later and npm.
- Docker Desktop or Docker Engine with Compose.
- A Jetson Nano image with a TensorRT version compatible with the deployed engines.
- PostgreSQL and an MQTT broker for the complete stack.

## Quick Start

### 1. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Set appropriate values in `.env`, especially `DATABASE_URL`, MQTT connection settings, and `API_KEY`. Never commit `.env` or other secrets to the repository.

### 2. Start the backend and database

```powershell
docker compose up --build
```

The backend listens on `http://localhost:8000` by default. FastAPI's Swagger UI is available at `/docs` once the application routes are implemented.

### 3. Start the frontend in development mode

```powershell
Set-Location frontend
npm install
npm run dev
```

### 4. Run Python checks

From the repository root:

```powershell
python -m compileall shared edge backend
python -m pytest
```

Equivalent convenience commands are defined in the `Makefile` (`make test`, `make backend`, and `make frontend`) for environments with GNU Make.

## Edge Deployment

1. Prepare an ONNX model and build a Jetson-compatible TensorRT engine with `edge/scripts/build_engine.py`.
2. Place the engine files in `edge/models/` and update paths in `edge/config/edge_config.yaml`.
3. Configure the camera, MQTT broker, frame dimensions, and FPS.
4. Measure latency, memory, and power with `edge/scripts/benchmark_edge.py`.
5. Use `infra/scripts/setup_jetson.sh` to prepare the device and `infra/scripts/deploy_edge.sh` to deploy the edge service.

TensorRT engines are hardware- and CUDA/TensorRT-version-specific. The `.engine` files currently included in this repository are empty placeholders, not production models.

## Operational Principles

- **Edge-first:** send only required events and metadata; do not transmit full video by default.
- **Resilient:** use the local buffer during connectivity failures without stopping capture or inference.
- **Observable:** expose Prometheus metrics, emit structured logs, and monitor device health heartbeats.
- **Secure by default:** protect backend endpoints with API keys or JWT, restrict MQTT access, and keep secrets outside source control.
- **Reproducible:** pin runtime and model versions and test edge, backend, and frontend components independently.

## CI/CD

The workflows in `.github/workflows/` currently provide:

- `edge_build.yml`: source validation for the edge application.
- `backend_test.yml`: source validation for the backend.
- `frontend_test.yml`: dependency installation and frontend build.

## Documentation and Contributing

See the [`docs/`](docs/) directory for project documentation. When adding a feature, update the shared contracts, relevant tests, sample configuration, and operational documentation together.

## License

Released under the [MIT License](LICENSE).
