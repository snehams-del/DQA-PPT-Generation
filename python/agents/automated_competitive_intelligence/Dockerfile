# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ==========================================
# STAGE 1: Build React UI Artifacts
# ==========================================
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

# Only fetch package manifests to utilize native Docker layer caching
COPY frontend/package.json ./
RUN npm install

# Build static minified React app
COPY frontend/ ./
RUN npm run build

# ==========================================
# STAGE 2: Construct FastAPI Production Environment
# ==========================================
FROM python:3.13-slim
WORKDIR /app

# Load the entire project root repository footprint logically
COPY . /app

# Inject compiled UI bundle from the earlier container logic securely over
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Install dependency engine UV overriding physical runtime maps
RUN python3 -m pip install uv 
RUN uv venv 
RUN . .venv/bin/activate && uv sync

# Define isolated execution targeting the native Uvicorn engine bridging UI hooks implicitly
CMD ["/app/.venv/bin/uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8080"]