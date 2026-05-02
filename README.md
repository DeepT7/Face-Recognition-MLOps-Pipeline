# Scalable Face Matching Gateway

## Overview

This project is a production-minded AI gateway for scalable face matching, verification, and user management. It combines secure API access, efficient face embedding inference, and a responsive frontend experience to support real-world use cases like edge camera authentication, visitor screening, and enterprise identity verification.

The system is designed for AI engineers and MLOps practitioners who need a deployable pipeline that integrates model serving, data management, security, and operational readiness.

## What Makes This Project Impressive

- **Triton-ready model serving**: The architecture is designed to integrate with NVIDIA Triton Inference Server for production-scale GPU inference.
- **ONNX face recognition pipeline**: Uses `checkpoints/edgeface_base.onnx` for embedding extraction, with optional Triton model deployment via `model_repository/face_matching_model`.
- **Docker Compose orchestration**: Multi-container deployment for API + Triton, with health checks and service dependency management.
- **Scalable data access**: Supabase-backed gallery storage with pagination and safe bulk loading.
- **Secure management workflow**: Admin-only protected registration, user listing, and deletion.
- **FastAPI microservice architecture**: Lightweight, async-first API endpoints with clean separation of concerns.
- **Front-end usability**: A polished single-page interface for registration, verification, and user management.
- **Operational visibility**: Health endpoints and logging for easier debugging and deployment.

## Architecture and Workflow

### 1. Initialization

- Configuration values are loaded from `.env`; host/port defaults are defined in `app/core/config.py`.
- The FastAPI server boots and mounts the static frontend.
- The face matching model is loaded at startup using ONNX Runtime.
- Gallery embeddings and metadata are loaded from Supabase into memory to support fast similarity search.

### 2. Authentication

- The application uses a single `ADMIN_API_KEY` for all management operations:
  - `/users`
  - `/register`
  - `/person/{person_id}`
- This avoids unsafe preset keys and aligns with secure production patterns.
- Verification can remain open or be gated independently depending on desired deployment security.

### 3. Registration Pipeline

- Users upload an image and name through the frontend.
- The backend extracts face embeddings and writes metadata to Supabase.
- The image is also cached locally and optionally stored in Supabase bucket storage.
- The in-memory gallery is updated immediately for low-latency matching.

### 4. Verification Pipeline

- Probe images are compared against the gallery using similarity scoring.
- The result returns a confidence score and verification status.
- This is suitable for both batch and real-time inference.

### 5. Management and MLOps

- The project includes pagination for large user sets, avoiding Supabase’s default row limit.
- Search and delete features support lifecycle management of registered identities.
- Logging and health checks provide entry points for monitoring and alerting.

## Project Structure

- `app/`
  - `main.py` — API service and inference endpoints.
  - `utils.py` — helper functions for embeddings, gallery loading, and Supabase integration.
  - `core/config.py` — central path and server configuration.
- `static/`
  - `index.html` — web UI.
  - `css/style.css` — responsive design and dashboard styling.
  - `js/app.js` — authentication, API integration, pagination, and user workflows.
- `checkpoints/` — ONNX model and checkpoints used for face embedding extraction.
- `data/` — gallery/probe image storage and system database.
- `model_repository/` — model deployment resources.
- `start_website.py` — launcher that reads config and starts the API service.
- `requirements.txt` — pinned dependency list for reproducible environments.

## Technology Stack

- Python 3
- ONNX Runtime
- NVIDIA Triton Inference Server
- Triton client (gRPC / HTTP)
- Docker Compose
- Supabase Python client
- HTML, CSS, Vanilla JavaScript
- FastAPI
- Uvicorn
- `python-dotenv`

## Running the Project

### 1. Clone the repository

```bash
git clone <repository-url>
cd scalable_face_matching_gateway
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup `.env`

Create a `.env` file in the project root:

```env
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
ADMIN_API_KEY=your-admin-api-key
TRITON_SERVER_URL=localhost:8001
APP_HOST=127.0.0.1
APP_PORT=8000
```

### 4. Start the application

```bash
python start_website.py
```

Or run directly with Uvicorn:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Containerized deployment with Docker Compose

This repository includes `docker-compose.yaml` for running both Triton and the FastAPI gateway together.

```bash
docker compose up --build
```

When using Docker Compose, the gateway automatically uses `TRITON_SERVER_URL=triton:8001` to reach the Triton service inside the network.

### 6. Open the UI

```text
http://127.0.0.1:8000/web
```

### 7. Authenticate

Enter the `ADMIN_API_KEY` in the API Authentication modal.

## Interview Highlights

- Supports a full inference pipeline from image upload to embedding matching
- Demonstrates secure API key gating for management operations
- Uses Supabase for managed storage and data persistence
- Designed for MLOps with startup model loading, logging, health checks, and environment configuration
- Frontend-backed UX with pagination and search for large user sets
- Easy to extend for GPU acceleration, containerization, or CI/CD deployment

## Notes

- Keep `.env` secret and out of source control.
- Use a strong `ADMIN_API_KEY` for production.
- The Triton service and API gateway can be deployed together with Docker Compose.
- Restart the server after changing `APP_HOST` / `APP_PORT`.
