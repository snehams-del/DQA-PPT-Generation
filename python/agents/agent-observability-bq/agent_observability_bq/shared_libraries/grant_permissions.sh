#!/bin/bash
# Script to grant BigQuery dataset access permissions to Default Compute Service Account

set -e

# Load environment variables from .env file
SCRIPT_DIR="$(dirname "$0")"

# Prioritize .env in the current working directory (e.g., when run inside a scaffolded project)
if [ -f "$PWD/.env" ]; then
  ENV_FILE="$PWD/.env"
elif [ -f "${SCRIPT_DIR}/../../.env" ]; then
  ENV_FILE="${SCRIPT_DIR}/../../.env"
else
  echo "Warning: .env file not found"
fi

if [ -n "$ENV_FILE" ]; then
  source "$ENV_FILE"
fi

# Get the project ID from environment variable
PROJECT_ID="$GOOGLE_CLOUD_PROJECT"
if [ -z "$PROJECT_ID" ]; then
  PROJECT_ID=$(gcloud config get-value project)
fi

if [ -z "$PROJECT_ID" ]; then
  echo "No project ID found. Please set your project ID."
  exit 1
fi

PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
if [ -z "$PROJECT_NUMBER" ]; then
  echo "Failed to retrieve project number for project $PROJECT_ID"
  exit 1
fi

# Agents deployed to Agent Engine or Cloud Run use the Default Compute Service Account
# if no explicit service account is provided via Terraform.
SERVICE_ACCOUNT_COMPUTE="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
SERVICE_ACCOUNT_RE="service-${PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"

echo "Granting BigQuery permissions to Default Compute Service Account ($SERVICE_ACCOUNT_COMPUTE)..."

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_COMPUTE" \
  --role="roles/bigquery.dataEditor" > /dev/null

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_COMPUTE" \
  --role="roles/bigquery.jobUser" > /dev/null

echo "Granting BigQuery permissions to Agent Engine Service Agent ($SERVICE_ACCOUNT_RE)..."

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_RE" \
  --role="roles/bigquery.dataEditor" > /dev/null

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_RE" \
  --role="roles/bigquery.jobUser" > /dev/null

echo "✅ BigQuery permissions granted successfully for both service accounts."
