#!/usr/bin/env python3
# Copyright 2026 Google LLC
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

import os
import argparse
import datetime
import json
import io
import requests
from dotenv import load_dotenv

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import google.auth

from google.cloud import firestore
from google.cloud import storage

# Load environment variables
load_dotenv(override=True)

# Configuration from environment variables
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_REGION = os.getenv("GCP_REGION")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
FIRESTORE_DB = os.getenv("FIRESTORE_DB")
GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash")
GCS_BUCKET = os.getenv("GCS_BUCKET")
VERTEX_AI_SEARCH_DATA_STORE_ID = os.getenv("VERTEX_AI_SEARCH_DATA_STORE_ID")

def validate_config(subcommand):
    """Validates that all required environment variables are set for the subcommand."""
    required = ["GCP_PROJECT_ID", "GCP_REGION"]
    
    if subcommand in ["copy-to-staging", "poll-drive"]:
        required += ["DRIVE_FOLDER_ID"]
    if subcommand == "copy-to-staging":
        required += ["GCS_BUCKET"]
    elif subcommand == "extract-metadata":
         required += ["FIRESTORE_DB"]
    elif subcommand == "run-import":
         required += ["VERTEX_AI_SEARCH_DATA_STORE_ID", "GCS_BUCKET"]
         
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        return False
    return True

# Initialize clients
def get_drive_service():
    """Initializes and returns the Google Drive API service."""
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build('drive', 'v3', credentials=credentials)

def get_firestore_client():
    """Initializes and returns the Firestore client."""
    return firestore.Client(project=GCP_PROJECT_ID, database=FIRESTORE_DB)

def get_genai_client():
    """Initializes and returns the Google GenAI client."""
    return genai.Client(
        vertexai=True,
        project=GCP_PROJECT_ID,
        location=GCP_REGION
    )

def get_storage_client():
    """Initializes and returns the Cloud Storage client."""
    return storage.Client(project=GCP_PROJECT_ID)

def download_drive_file(service, file_id):
    """Downloads a file from Google Drive and returns its content as bytes."""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    return fh.getvalue()

def trigger_workflow(file_id):
    """Triggers the Google Cloud Workflow for a given Drive file ID."""
    import google.auth.transport.requests
    import google.auth
    
    print(f"Triggering Workflow for file_id: {file_id}")
    try:
        credentials, _ = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        token = credentials.token
    except Exception as e:
         print(f"Auth Error for Workflow trigger: {e}")
         return

    workflow_url = f"https://workflowexecutions.googleapis.com/v1/projects/{GCP_PROJECT_ID}/locations/{GCP_REGION}/workflows/contract-ingestion-workflow/executions"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {
        "argument": json.dumps({"data": {"id": file_id}})
    }
    
    try:
        response = requests.post(workflow_url, headers=headers, json=body)
        if response.status_code in [200, 202]:
            print(f"Workflow Triggered Successfully: {response.text}")
        else:
            print(f"Failed Trigger (HTTP {response.status_code}): {response.text}")
    except Exception as e:
         print(f"Request Error triggering workflow: {e}")

# Schema for extracted metadata
class ContractMetadata(BaseModel):
    provider_name: Optional[str] = Field(description="The name of the contract provider")
    start_date: Optional[str] = Field(description="The start date of the contract in YYYY-MM-DD")
    termination_date: Optional[str] = Field(description="The termination date or expiry in YYYY-MM-DD")
    commitment_amount: Optional[float] = Field(description="Total financial commitment value")
    currency: Optional[str] = Field(description="Currency code e.g. USD, EUR")

def extract_metadata_from_gemini(client, file_content, mime_type):
    """Uses Gemini to extract metadata from contract file content."""
    prompt = "Extract the provider name, termination date, commitment amount, and currency from this contract."
    
    response = client.models.generate_content(
        model=GEMINI_MODEL_ID,
        contents=[
            types.Part.from_bytes(data=file_content, mime_type=mime_type),
            prompt
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ContractMetadata
        )
    )
    
    if response.parsed:
        return response.parsed.model_dump()
    
    try:
         data = json.loads(response.text)
         return data
    except Exception as e:
         print(f"Error parsing Gemini response: {e}")
         return None

# --- Command Implementations ---

def cmd_poll_drive(args):
    """
    Subcommand: Polls a Drive folder for new files and triggers a Cloud Workflow for each.
    """
    print(f"Polling Drive folder: {DRIVE_FOLDER_ID}...")
    service = get_drive_service()
    db = get_firestore_client()
    collection_ref = db.collection('contracts')

    try:
        query = f"'{DRIVE_FOLDER_ID}' in parents and trashed = false"
        results = service.files().list(
            q=query,
            orderBy="modifiedTime desc",
            fields="files(id, name, mimeType)"
        ).execute()
        
        files = results.get('files', [])
        if not files:
            print("No files found in folder.")
            return

        print(f"Found {len(files)} files. Checking Firestore...")

        for file in files:
            file_id = file.get('id')
            file_name = file.get('name')
            mime_type = file.get('mimeType')

            if mime_type.startswith('application/vnd.google-apps'):
                 print(f"Skipping Google native file type: {file_name} ({mime_type})")
                 continue

            # Check if exists in Firestore (ID === Drive doc ID)
            doc_ref = collection_ref.document(file_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                print(f"New file detected: {file_name} ({file_id}). Triggering workflow...")
                trigger_workflow(file_id)
            else:
                print(f"File {file_name} ({file_id}) already processed. Skipping.")

    except Exception as e:
        print(f"Error during polling: {e}")
        sys.exit(1)

def cmd_copy_to_staging(args):
    """
    Subcommand: Downloads a file from Google Drive and uploads it to Cloud Storage.
    """
    print(f"Starting copy-to-staging for Drive File ID: {args.drive_file_id}")
    service = get_drive_service()
    
    # 1. Get metadata from Drive
    try:
        file_metadata = service.files().get(fileId=args.drive_file_id, fields="name, mimeType").execute()
        file_name = file_metadata.get('name')
        mime_type = file_metadata.get('mimeType')
        print(f"Found file: {file_name} ({mime_type})")
    except Exception as e:
        print(f"Error fetching metadata from Drive: {e}")
        sys.exit(1)

    if mime_type.startswith('application/vnd.google-apps'):
         print(f"Skipping Google native file type: {mime_type}")
         sys.exit(1)

    # 2. Download
    try:
        file_content = download_drive_file(service, args.drive_file_id)
        print(f"Downloaded {len(file_content)} bytes.")
    except Exception as e:
        print(f"Error downloading from Drive: {e}")
        sys.exit(1)

    # 3. Upload to GCS
    try:
        storage_client = get_storage_client()
        bucket = storage_client.bucket(GCS_BUCKET)
        gcs_path = f"staging/{args.drive_file_id}/{file_name}"
        blob = bucket.blob(gcs_path)
        blob.upload_from_string(file_content, content_type=mime_type)
        print(f"Uploaded to GCS: gs://{GCS_BUCKET}/{gcs_path}")
    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        sys.exit(1)

def cmd_extract_metadata(args):
    """
    Subcommand: Processes file from GCS using Gemini to extract metadata into Firestore.
    """
    print(f"Starting extract-metadata for GCS URI: {args.gcs_uri}")
    from urllib.parse import urlparse
    parsed = urlparse(args.gcs_uri)
    bucket_name = parsed.netloc
    blob_name = parsed.path.lstrip('/')
    
    if not bucket_name or not blob_name:
        print(f"Invalid GCS URI format: {args.gcs_uri}")
        sys.exit(1)

    # 1. Download from GCS
    try:
        storage_client = get_storage_client()
        bucket = storage_client.bucket(bucket_name)
        
        if blob_name.endswith('*'):
            prefix = blob_name[:-1]
            blobs = bucket.list_blobs(prefix=prefix)
            blob = None
            # Take the first matching blob
            for b in blobs:
                blob = b
                break
            if not blob:
                print(f"No files found with prefix: {prefix}")
                sys.exit(1)
            print(f"Found matching file: {blob.name}")
        else:
            blob = bucket.blob(blob_name)
            
        file_content = blob.download_as_bytes()
        mime_type = blob.content_type or "application/pdf"
    except Exception as e:
        print(f"Error downloading from GCS: {e}")
        sys.exit(1)

    # 2. Extract using Gemini
    try:
        genai_client = get_genai_client()
        metadata = extract_metadata_from_gemini(genai_client, file_content, mime_type)
        if not metadata:
            print("Failed to extract metadata.")
            sys.exit(1)
        print(f"Extracted metadata: {metadata}")
    except Exception as e:
        print(f"Gemini Error: {e}")
        sys.exit(1)

    # 3. Save to Firestore
    try:
        db = get_firestore_client()
        collection_ref = db.collection('contracts')
        
        term_date_str = metadata.get("termination_date")
        termination_date = None
        if term_date_str:
            try:
                termination_date = datetime.datetime.strptime(term_date_str, "%Y-%m-%d")
                termination_date = termination_date.replace(tzinfo=datetime.timezone.utc)
            except ValueError:
                pass

        doc_data = {
            "provider_name": metadata.get("provider_name"),
            "termination_date_str": term_date_str,
            "termination_date": termination_date,
            "commitment_amount": metadata.get("commitment_amount"),
            "currency": metadata.get("currency"),
            "gcs_uri": f"gs://{bucket_name}/{blob.name}",
            "file_name": os.path.basename(blob.name),
            "processed_at": firestore.SERVER_TIMESTAMP
        }
        if args.file_id:
            doc_data["file_id"] = args.file_id
            doc_ref = collection_ref.document(args.file_id)
        else:
            doc_ref = collection_ref.document()
            
        doc_ref.set(doc_data)
        print(f"Saved to Firestore: {doc_ref.id}")
    except Exception as e:
        print(f"Firestore Error: {e}")
        sys.exit(1)

def cmd_run_import(args):
    """
    Subcommand: Triggers indexing in Vertex AI Search for the processed folder/file.
    """
    print("Starting run-import for Vertex AI Search update...")
    
    # 1. Get auth token
    try:
        import google.auth.transport.requests
        credentials, _ = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        token = credentials.token
    except Exception as e:
         print(f"Auth Error for REST trigger: {e}")
         return

    # Endpoint URL
    location = os.getenv("VERTEX_AI_SEARCH_LOCATION", "global")
    url = f"https://discoveryengine.googleapis.com/v1/projects/{GCP_PROJECT_ID}/locations/{location}/collections/default_collection/dataStores/{VERTEX_AI_SEARCH_DATA_STORE_ID}/branches/0/documents:import"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {
        "gcsSource": {
            "inputUris": [f"gs://{GCS_BUCKET}/staging/**"],
            "dataSchema": "content"
        },
        "reconciliationMode": "INCREMENTAL"
    }
    
    print(f"Triggering Import for gs://{GCS_BUCKET}/staging/** ...")
    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code in [200, 202]:
            operation = response.json()
            operation_name = operation.get("name")
            print(f"Import Job Triggered: {operation_name}")
            
            print("Waiting for import operation to complete...")
            poll_url = f"https://discoveryengine.googleapis.com/v1/{operation_name}"
            
            import time
            while True:
                poll_resp = requests.get(poll_url, headers=headers)
                if poll_resp.status_code != 200:
                    print(f"Error polling operation: {poll_resp.text}")
                    sys.exit(1)
                
                poll_data = poll_resp.json()
                if poll_data.get("done"):
                    if "error" in poll_data:
                        print(f"Import Failed: {poll_data['error']}")
                        sys.exit(1)
                    else:
                        print("Import Completed Successfully.")
                        break
                print("Still importing...")
                time.sleep(10)
        else:
            print(f"Failed (HTTP {response.status_code}): {response.text}")
            sys.exit(1)
    except Exception as e:
         print(f"Request Error: {e}")
         sys.exit(1)

def cmd_fetch_spend(args):
    """
    Subcommand: Fetches daily spend for all contracts from their respective providers using pluggable importers.
    """
    print("Starting fetch-spend for all contracts...")
    import sys
    from importers import get_all_importer_classes
    
    # Instantiate all available importers
    importer_classes = get_all_importer_classes()
    importers = [cls() for cls in importer_classes]
    
    # Create a mapping of contract_id -> importer
    importer_map = {}
    for imp in importers:
        try:
            cid = imp.get_applicable_contract_id()
            importer_map[cid] = imp
        except Exception as e:
            print(f"Warning: Failed to get contract ID for importer {type(imp).__name__}: {e}")

    try:
        db = get_firestore_client()
        collection_ref = db.collection('contracts')
        contracts = collection_ref.stream()
        
        updated_count = 0
        skipped_count = 0
        
        for contract in contracts:
            contract_id = contract.id
            if contract_id in importer_map:
                importer = importer_map[contract_id]
                print(f"Processing contract {contract_id} with importer {type(importer).__name__}...")
                
                try:
                    current_spend = importer.get_current_spend()
                    contract.reference.update({
                        "current_spend": current_spend,
                        "last_spend_update": firestore.SERVER_TIMESTAMP
                    })
                    print(f"Successfully updated contract {contract_id} with absolute current spend: {current_spend:.2f}")
                    updated_count += 1
                except Exception as e:
                    print(f"Error fetching spend for contract {contract_id}: {e}")
            else:
                # print(f"Skipping contract {contract_id}: No matching importer found.")
                skipped_count += 1
                
        print(f"Fetch-spend completed. Updated: {updated_count}, Skipped: {skipped_count}")
        
    except Exception as e:
         print(f"Error during bulk fetch-spend: {e}")
         sys.exit(1)

def cmd_check_alerts(args):
    """
    Subcommand: Checks for alerts and sends notifications.
    """
    print(f"Starting check-alerts for type: {args.type}")
    try:
        db = get_firestore_client()
        collection_ref = db.collection('contracts')
        now = datetime.datetime.now(datetime.timezone.utc)
        
        if args.type == "expiration":
             target_date = now + datetime.timedelta(days=30)
             query = collection_ref.where(filter=firestore.FieldFilter("termination_date", ">=", now)) \
                                   .where(filter=firestore.FieldFilter("termination_date", "<=", target_date))
             hits = query.stream()
             alert_msg = "🚨 *Weekly Expiration Alerts* 🚨\n"
             found = False
             for hit in hits:
                  data = hit.to_dict()
                  alert_msg += f"- *{data.get('provider_name')}*: Expiring on {data.get('termination_date_str')}\n"
                  found = True
             if found:
                  print(alert_msg)
                  if SLACK_WEBHOOK_URL:
                       requests.post(SLACK_WEBHOOK_URL, json={"text": alert_msg})
             else:
                  print("No expiring contracts found.")
        elif args.type == "forecast":
             contracts = collection_ref.stream()
             alert_msg = "🚨 *Daily Spend Forecast Alerts* 🚨\n"
             found = False
             for contract in contracts:
                  data = contract.to_dict()
                  if 'commitment_amount' in data and 'current_spend' in data:
                       commitment = data['commitment_amount']
                       current = data['current_spend']
                       start_date_str = data.get("start_date")
                       term_date_str = data.get("termination_date_str")
                       if start_date_str and term_date_str:
                            try:
                                 start = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
                                 term = datetime.datetime.strptime(term_date_str, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
                                 total_time = (term - start).total_seconds()
                                 elapsed = (now - start).total_seconds()
                                 if total_time > 0 and elapsed > 0:
                                      forecast = (current / elapsed) * total_time
                                      if forecast < commitment * 0.9:
                                           alert_msg += f"- *{data.get('provider_name')}*: At risk. Forecast ${forecast:.2f} is under commitment ${commitment:.2f}\n"
                                           found = True
                            except ValueError:
                                 pass
             if found:
                  print(alert_msg)
                  if SLACK_WEBHOOK_URL:
                        requests.post(SLACK_WEBHOOK_URL, json={"text": alert_msg})
             else:
                  print("No spending forecast risks found.")
    except Exception as e:
         print(f"Alerts Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Procurement Ingestion Pipeline Multi-command tool")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    
    # Subcommand: poll-drive
    subparsers.add_parser("poll-drive", help="Poll Drive folder for new files and trigger workflow")

    # Subcommand: copy-to-staging
    copy_parser = subparsers.add_parser("copy-to-staging", help="Download from Drive and stage to GCS")
    copy_parser.add_argument("drive_file_id", type=str, help="The Drive File ID to process")
    
    # Subcommand: extract-metadata
    extract_parser = subparsers.add_parser("extract-metadata", help="Run Gemini extraction on staged GCS item")
    extract_parser.add_argument("gcs_uri", type=str, help="GCS URI (e.g. gs://bucket/file.pdf)")
    extract_parser.add_argument("--file-id", type=str, help="Original Drive File ID reference", required=False)
    
    # Subcommand: run-import
    subparsers.add_parser("run-import", help="Trigger Vertex AI Search index job")
    
    # Subcommand: fetch-spend
    fetch_parser = subparsers.add_parser("fetch-spend", help="Fetch daily spend for all providers")
    
    # Subcommand: check-alerts
    alerts_parser = subparsers.add_parser("check-alerts", help="Check alerts")
    alerts_parser.add_argument("--type", choices=["expiration", "forecast"], help="Alert type", required=True)
    
    args = parser.parse_args()
    
    if not validate_config(args.subcommand):
         sys.exit(1)
         
    if args.subcommand == "poll-drive":
        cmd_poll_drive(args)
    elif args.subcommand == "copy-to-staging":
        cmd_copy_to_staging(args)
    elif args.subcommand == "extract-metadata":
        cmd_extract_metadata(args)
    elif args.subcommand == "run-import":
        cmd_run_import(args)
    elif args.subcommand == "fetch-spend":
        cmd_fetch_spend(args)
    elif args.subcommand == "check-alerts":
        cmd_check_alerts(args)

if __name__ == "__main__":
    import sys
    main()
