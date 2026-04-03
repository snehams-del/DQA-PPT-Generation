#!/bin/bash
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Script to grant RAG Corpus access permissions to AI Platform Reasoning Engine Service Agent

set -e

# Load environment variables from .env file
SCRIPT_DIR="$(dirname "$0")"

# Prioritize .env in the current working directory (e.g., when run inside a scaffolded project)
if [ -f "$PWD/.env" ]; then
  ENV_FILE="$PWD/.env"
elif [ -f "${SCRIPT_DIR}/../.env" ]; then
  ENV_FILE="${SCRIPT_DIR}/../.env"
else
  echo "Error: .env file not found"
  exit 1
fi

source "$ENV_FILE"

# Get the project ID from environment variable
PROJECT_ID="$GOOGLE_CLOUD_PROJECT"
if [ -z "$PROJECT_ID" ]; then
  echo "No project ID found. Please set your project ID with 'gcloud config set project YOUR_PROJECT_ID'"
  exit 1
fi

# Get the project number
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
if [ -z "$PROJECT_NUMBER" ]; then
  echo "Failed to retrieve project number for project $PROJECT_ID"
  exit 1
fi

# Define the service account
SERVICE_ACCOUNT="service-${PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"

# Get RAG Corpus ID from the RAG_CORPUS environment variable
if [ -z "$RAG_CORPUS" ]; then
  echo "RAG_CORPUS environment variable is not set in the .env file"
  exit 1
fi

# Extract RAG_CORPUS_ID from the full RAG_CORPUS path
RAG_CORPUS_ID=$(echo $RAG_CORPUS | awk -F'/' '{print $NF}')

# Define the RAG Corpus resource
RAG_CORPUS="projects/${PROJECT_NUMBER}/locations/us-central1/ragCorpora/${RAG_CORPUS_ID}"

echo "Granting permissions to $SERVICE_ACCOUNT..."

# Ensure the AI Platform service identity exists
gcloud beta services identity create --service=aiplatform.googleapis.com --project="$PROJECT_ID" --quiet

# Grant the standard Vertex AI Viewer role to the service account
# This role includes aiplatform.ragCorpora.query among other viewing permissions
echo "Granting roles/aiplatform.viewer for RAG Corpus access..."

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.viewer" \
  --condition=None

echo "Permissions granted successfully."
echo "Service account $SERVICE_ACCOUNT can now query the specific RAG Corpus: $RAG_CORPUS"
