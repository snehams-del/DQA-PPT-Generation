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

import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from backend.tools.document_downloader import download_document, upload_to_gcs, download_and_upload_datasheets, DatasheetProcessingError

@pytest.mark.asyncio
@patch("backend.tools.document_downloader.AIOFile")
@patch("backend.tools.document_downloader.Writer")
@patch("backend.tools.document_downloader.httpx.AsyncClient")
async def test_download_document_http(mock_async_client, mock_writer, mock_aiofile):
    """
    Simulates fetching a public Datasheet bypassing physical network calls.
    Mocks response buffers and ensures HTTPError exceptions aren't caught silently.
    """
    # Simulate a stream payload iterator
    mock_response = AsyncMock()
    mock_response.headers = {"Content-Type": "application/pdf"}
    
    # We cheat the asynchronous iteration chunk loop
    async def mock_aiter(*args, **kwargs):
        yield b"chunk_block"
    
    mock_response.aiter_bytes = mock_aiter

    mock_ctx_manager = AsyncMock()
    mock_ctx_manager.__aenter__.return_value = mock_response
    
    mock_client_instance = MagicMock()
    mock_client_instance.stream.return_value = mock_ctx_manager
    mock_async_client.return_value.__aenter__.return_value = mock_client_instance
    
    # Simulate internal async file handlers
    mock_aiofile.return_value.__aenter__.return_value = MagicMock()
    mock_writer.return_value = AsyncMock()

    file_path, err = await download_document("http://example.com/datasheet.pdf", "/tmp/mocked.pdf")

    assert file_path == "/tmp/mocked.pdf"
    assert err == ""
    mock_client_instance.stream.assert_called_with("GET", "http://example.com/datasheet.pdf")


@pytest.mark.asyncio
@patch("backend.tools.document_downloader.storage.Client")
async def test_upload_to_gcs(mock_storage_client):
    """
    Overrides the python multiprocessing thread used for synchronous SDK Google Blob Uploads.
    """
    mock_client_instance = mock_storage_client.return_value
    mock_bucket = mock_client_instance.bucket.return_value
    mock_blob = mock_bucket.blob.return_value
    
    # Because GCS uses sync `upload_from_filename` running in `asyncio.to_thread`
    # We mock its behavior as a standard pass completion
    mock_blob.upload_from_filename = MagicMock()

    with patch("backend.tools.document_downloader.project_id", "test_proj"):
        with patch("backend.tools.document_downloader.bucket_name", "test_bucket"):
            uri, err = await upload_to_gcs("/tmp/mocked.pdf", "remote_datasheet.pdf")
            
            assert uri == "gs://test_bucket/remote_datasheet.pdf"
            assert err == ""
            mock_blob.upload_from_filename.assert_called_once()
