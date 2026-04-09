# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import logging
import os
import uuid
import mimetypes
from urllib.parse import urlparse
from typing import Optional, Tuple
from google.cloud import storage
import httpx
from aiofile import AIOFile, Writer
from ..config import config

# Config variables (Assuming they are set correctly via the actual config import)
project_id = config.project_id
bucket_name = config.bucket_name
gcs_download_dir = config.gcs_download_pdf_dirpath
temp_dir = config.temp_dir_path

os.makedirs(temp_dir, exist_ok=True)


# Define a custom exception for clarity
class DatasheetProcessingError(Exception):
    """Custom exception for errors during datasheet download/upload."""
    pass


# _logger is defined
_logger = logging.getLogger(__name__)


async def download_document(url: str, local_filename: str) -> Tuple[Optional[str], str]:
    """
    Downloads a document from a given URL and saves it locally.
    Supports authenticated GCS downloads for Google Cloud Storage URLs to prevent 403s.

    Args:
        url (str): The URL of the file to download.
        local_filename (str): The path and filename to save the downloaded file locally.

    Returns:
        tuple[str | None, str]: (local_filename, errors) if successful, otherwise (None, errors).
    """
    errors = ""
    parsed_url = urlparse(url)

    # Check if the URL relates to a Google Cloud Storage Bucket to use authenticated client
    if parsed_url.netloc == "storage.googleapis.com" or parsed_url.scheme == "gs":
        try:
            storage_client = storage.Client(project=project_id)
            if parsed_url.scheme == "gs":
                bucket_name_req = parsed_url.netloc
                blob_name = parsed_url.path.lstrip("/")
            else:
                # e.g https://storage.googleapis.com/bucket-name/path/to/object
                path_parts = parsed_url.path.lstrip("/").split("/", 1)
                bucket_name_req = path_parts[0]
                blob_name = path_parts[1] if len(path_parts) > 1 else ""

            bucket = storage_client.bucket(bucket_name_req)
            blob = bucket.blob(blob_name)

            _logger.info(f"Using authenticated GCS client for: gs://{bucket_name_req}/{blob_name}")
            # GCS Blob download to filename is synchronous, so we run in async executor
            await asyncio.to_thread(blob.download_to_filename, local_filename)
            return local_filename, errors
        
        except Exception as e:
            error = f"Error downloading from authenticated GCS {url}: {e}"
            errors += error
            _logger.error(error, exc_info=True)
            return None, errors

    # Public External Website Fallback
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
        }
        timeout = httpx.Timeout(120.0)

        async with httpx.AsyncClient(
            follow_redirects=True, headers=headers, timeout=timeout
        ) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()  # Raises HTTPError for bad status codes

                content_type = response.headers.get("Content-Type", "").lower()
                _logger.info(f"Downloaded content type: {content_type}")

                # Use aiofile for async file writing
                async with AIOFile(local_filename, "wb") as afp:
                    writer = Writer(afp)
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        if chunk:
                            await writer(chunk)

        return local_filename, errors

    except httpx.HTTPError as e:
        error = f"Error downloading document from {url}: {e}"
        errors += error
        _logger.error(error, exc_info=True)
        return None, errors

    except IOError as e:
        error = f"Error writing document to file {local_filename}: {e}"
        errors += error
        _logger.error(error, exc_info=True)
        return None, errors


async def upload_to_gcs(
    local_path: str, gcs_filename: str
) -> Tuple[Optional[str], str]:
    """
    Uploads a local file to a GCS bucket using global config variables.

    Args:
        local_path (str): The path to the local file to upload.
        gcs_filename (str): The desired filename (blob name) within the GCS bucket.

    Returns:
        tuple[str | None, str]: (GCS URI, errors) if successful, otherwise (None, errors).
    """
    global project_id, bucket_name  # Use globals defined from config
    errors = ""
    gcs_uri = f"gs://{bucket_name}/{gcs_filename}"

    # Infer type based on extension
    content_type, _ = mimetypes.guess_type(local_path)
    if not content_type:
        content_type = "application/octet-stream"

    # GCS client is synchronous, use asyncio.to_thread
    try:
        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(gcs_filename)

        # Use asyncio.to_thread to run the synchronous GCS upload operation asynchronously
        await asyncio.to_thread(
            blob.upload_from_filename, local_path, content_type=content_type
        )

        _logger.info(f"Successfully uploaded to GCS: {gcs_uri}")
        return gcs_uri, errors

    except Exception as e:
        error = f"Failed to upload {local_path} to GCS {gcs_uri}: {e}"
        errors += error
        _logger.error(error, exc_info=True)
        return None, errors


async def download_and_upload_datasheets(url: str) -> str:
    """
    Downloads a document from a URL, uploads it to GCS, and cleans up the local file.

    The function constructs local_filename and gcs_filename internally using global config.

    Args:
        url (str): The URL of the document to download.

    Returns:
        str: The GCS URI of the uploaded file.

    Raises:
        DatasheetProcessingError: If the download or upload fails.
    """
    global temp_dir, gcs_download_dir

    # Fix LLM hallucinated URLs where '://' is replaced by '.'
    if url.startswith("https."):
        url = url.replace("https.", "https://", 1)
    elif url.startswith("http."):
        url = url.replace("http.", "http://", 1)

    # Extract dynamic file extension from the original URL or fallback to pdf
    parsed_path = urlparse(url).path
    _, ext = os.path.splitext(parsed_path)
    if not ext:
        ext = ".pdf" # Default to pdf if no extension is found in URL

    unique_id = str(uuid.uuid4())
    filename = f"{unique_id}{ext}"

    local_path = os.path.join(temp_dir, filename)
    gcs_filename = os.path.join(gcs_download_dir, filename)

    # 1. Download
    _logger.info(f"Starting download for URL: {url}")
    downloaded_path, download_error = await download_document(url, local_path)

    if not downloaded_path:
        raise DatasheetProcessingError(
            f"Failed to download document from {url}. Error: {download_error}"
        )

    try:

        # 2. Upload
        _logger.info(f"Starting upload for local file: {downloaded_path}")
        gcs_path, upload_error = await upload_to_gcs(downloaded_path, gcs_filename)

        if not gcs_path:
            raise DatasheetProcessingError(
                f"Failed to upload document to GCS. Error: {upload_error}"
            )

        # 3. Extract Text Locally for Context Grounding
        extracted_text = ""
        try:
            if ext.lower() == ".pdf":
                import fitz  # PyMuPDF
                with fitz.open(local_path) as doc:
                    extracted_text = chr(10).join([page.get_text() for page in doc])
                _logger.info(f"Successfully extracted {len(extracted_text)} characters from {local_path}")
            elif ext.lower() in [".md", ".txt", ".json", ".csv", ".xml"]:
                with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text = f.read()
                _logger.info(f"Successfully extracted {len(extracted_text)} characters from {local_path}")
            else:
                _logger.info(f"Skipping local extraction for unsupported extension: {ext}")
                extracted_text = f"FILE SAVED WITH EXTENSION: {ext}. TEXT EXTRACTION NOT SUPPORTED."
        except Exception as e:
            _logger.warning(f"Failed to extract text locally from {local_path}: {e}")
            extracted_text = "FAILED TO EXTRACT TEXT."

        return f"GCS URI: {gcs_path}\n\n--- DOCUMENT CONTENT ---\n{extracted_text}\n--- END DOCUMENT ---\n"

    finally:
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
                _logger.info(f"Cleaned up local file: {local_path}")
        except OSError as e:
            # Log cleanup failure but don't re-raise
            _logger.warning(
                f"Could not remove local file {local_path} during cleanup: {e}",
                exc_info=True,
            )


download_and_upload_datasheets_tool = download_and_upload_datasheets
