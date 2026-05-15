import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import datetime

# Add parent dir to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import process

class TestProcess(unittest.TestCase):
    @patch.dict(os.environ, {
        "GCP_PROJECT_ID": "test-project",
        "GCP_REGION": "us-central1",
        "DRIVE_FOLDER_ID": "drive-123",
        "FIRESTORE_DB": "fs-db",
        "GCS_BUCKET": "bucket-123",
        "VERTEX_AI_SEARCH_DATA_STORE_ID": "ds-123"
    })
    def test_validate_config_all_present(self):
        self.assertTrue(process.validate_config("copy-to-staging"))
        self.assertTrue(process.validate_config("extract-metadata"))
        self.assertTrue(process.validate_config("run-import"))

    @patch.dict(os.environ, {}, clear=True)
    def test_validate_config_missing(self):
        self.assertFalse(process.validate_config("copy-to-staging"))

    @patch('process.get_drive_service')
    @patch('process.get_storage_client')
    @patch('process.download_drive_file')
    @patch('process.GCS_BUCKET', 'bucket-123')
    def test_cmd_copy_to_staging_success(self, mock_download, mock_get_gcs, mock_get_drive):
        # Setup mocks
        mock_drive = MagicMock()
        mock_get_drive.return_value = mock_drive
        mock_drive.files().get().execute.return_value = {
            "name": "test.pdf",
            "mimeType": "application/pdf"
        }
        
        mock_download.return_value = b"file content"
        
        mock_gcs = MagicMock()
        mock_get_gcs.return_value = mock_gcs
        mock_bucket = MagicMock()
        mock_gcs.bucket.return_value = mock_bucket
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        
        # Trigger args
        args = MagicMock()
        args.drive_file_id = "123"
        args.subcommand = "copy-to-staging"
        
        process.cmd_copy_to_staging(args)
        
        # Verify calls
        mock_drive.files().get.assert_called_with(fileId="123", fields="name, mimeType")
        mock_download.assert_called_once_with(mock_drive, "123")
        mock_gcs.bucket.assert_called_with("bucket-123")
        mock_bucket.blob.assert_called_with("staging/123/test.pdf")
        mock_blob.upload_from_string.assert_called_once_with(b"file content", content_type="application/pdf")

    @patch('process.get_storage_client')
    @patch('process.get_genai_client')
    @patch('process.get_firestore_client')
    @patch('process.extract_metadata_from_gemini')
    def test_cmd_extract_metadata_success(self, mock_extract, mock_get_fs, mock_get_genai, mock_get_gcs):
        # Setup mocks
        mock_gcs = MagicMock()
        mock_get_gcs.return_value = mock_gcs
        mock_bucket = MagicMock()
        mock_gcs.bucket.return_value = mock_bucket
        mock_blob = MagicMock()
        mock_blob.name = "staging/123/test.pdf"
        mock_bucket.blob.return_value = mock_blob
        mock_blob.download_as_bytes.return_value = b"gcs content"
        mock_blob.content_type = "application/pdf"
        
        mock_extract.return_value = {
            "provider_name": "Acme",
            "termination_date": "2027-01-01",
            "commitment_amount": 1000.0,
            "currency": "USD"
        }
        
        mock_fs = MagicMock()
        mock_get_fs.return_value = mock_fs
        mock_collection = MagicMock()
        mock_fs.collection.return_value = mock_collection
        mock_doc = MagicMock()
        mock_collection.document.return_value = mock_doc
        
        args = MagicMock()
        args.gcs_uri = "gs://bucket-123/staging/123/test.pdf"
        args.file_id = "123"
        args.subcommand = "extract-metadata"
        
        # Run
        with patch.dict(os.environ, {"GCS_BUCKET": "bucket-123"}):
             process.cmd_extract_metadata(args)
        
        # Verify
        mock_gcs.bucket.assert_called_with("bucket-123")
        mock_blob.download_as_bytes.assert_called_once()
        mock_extract.assert_called_once()
        mock_doc.set.assert_called_once()
        sent_data = mock_doc.set.call_args[0][0]
        self.assertEqual(sent_data["provider_name"], "Acme")
        self.assertEqual(sent_data["commitment_amount"], 1000.0)
        self.assertEqual(sent_data["gcs_uri"], "gs://bucket-123/staging/123/test.pdf")

    @patch('process.get_storage_client')
    @patch('process.get_genai_client')
    @patch('process.get_firestore_client')
    @patch('process.extract_metadata_from_gemini')
    def test_cmd_extract_metadata_glob_success(self, mock_extract, mock_get_fs, mock_get_genai, mock_get_gcs):
        # Setup mocks
        mock_gcs = MagicMock()
        mock_get_gcs.return_value = mock_gcs
        mock_bucket = MagicMock()
        mock_gcs.bucket.return_value = mock_bucket
        
        # Mock list_blobs
        mock_blob = MagicMock()
        mock_blob.name = "staging/123/test.pdf"
        mock_blob.download_as_bytes.return_value = b"gcs content"
        mock_blob.content_type = "application/pdf"
        mock_bucket.list_blobs.return_value = [mock_blob]
        
        mock_extract.return_value = {
            "provider_name": "AcmeGlob",
            "termination_date": "2027-01-01",
            "commitment_amount": 1000.0,
            "currency": "USD"
        }
        
        mock_fs = MagicMock()
        mock_get_fs.return_value = mock_fs
        mock_collection = MagicMock()
        mock_fs.collection.return_value = mock_collection
        mock_doc = MagicMock()
        mock_collection.document.return_value = mock_doc
        
        args = MagicMock()
        args.gcs_uri = "gs://bucket-123/staging/123/*"
        args.file_id = "123"
        args.subcommand = "extract-metadata"
        
        # Run
        with patch.dict(os.environ, {"GCS_BUCKET": "bucket-123"}):
             process.cmd_extract_metadata(args)
        
        # Verify
        mock_gcs.bucket.assert_called_with("bucket-123")
        mock_bucket.list_blobs.assert_called_once_with(prefix="staging/123/")
        mock_blob.download_as_bytes.assert_called_once()
        mock_extract.assert_called_once()
        mock_doc.set.assert_called_once()
        sent_data = mock_doc.set.call_args[0][0]
        self.assertEqual(sent_data["provider_name"], "AcmeGlob")
        self.assertEqual(sent_data["file_name"], "test.pdf")
        self.assertEqual(sent_data["gcs_uri"], "gs://bucket-123/staging/123/test.pdf")

    @patch('process.get_firestore_client')
    def test_cmd_fetch_spend_success(self, mock_get_fs):
        mock_fs = MagicMock()
        mock_get_fs.return_value = mock_fs
        mock_collection = MagicMock()
        mock_fs.collection.return_value = mock_collection
        mock_doc = MagicMock()
        # Use the ID from MockProviderImporter
        mock_doc.id = "1DhBwF2yXlOSdlzkYIAaWqdRWdiFFjmLX"
        mock_doc.to_dict.return_value = {"provider_name": "mock", "current_spend": 100.0}
        mock_collection.stream.return_value = [mock_doc]
        
        args = MagicMock()
        process.cmd_fetch_spend(args)
        mock_doc.reference.update.assert_called_once()

    @patch('process.get_firestore_client')
    @patch('requests.post')
    def test_cmd_check_alerts_expiration(self, mock_post, mock_get_fs):
        mock_fs = MagicMock()
        mock_get_fs.return_value = mock_fs
        mock_collection = MagicMock()
        mock_fs.collection.return_value = mock_collection
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {"provider_name": "Acme", "termination_date_str": "2027-01-01"}
        mock_collection.where().where().stream.return_value = [mock_doc]
        
        args = MagicMock()
        args.type = "expiration"
        with patch('process.SLACK_WEBHOOK_URL', 'http://slack'):
             process.cmd_check_alerts(args)
        mock_post.assert_called_once()

    @patch('process.get_firestore_client')
    @patch('requests.post')
    def test_cmd_check_alerts_forecast(self, mock_post, mock_get_fs):
        mock_fs = MagicMock()
        mock_get_fs.return_value = mock_fs
        mock_collection = MagicMock()
        mock_fs.collection.return_value = mock_collection
        mock_doc = MagicMock()
        now = datetime.datetime.now(datetime.timezone.utc)
        start = now - datetime.timedelta(days=10)
        term = now + datetime.timedelta(days=10)
        mock_doc.to_dict.return_value = {
            "provider_name": "Acme", "commitment_amount": 1000.0, "current_spend": 200.0,
            "start_date": start.strftime("%Y-%m-%d"), "termination_date_str": term.strftime("%Y-%m-%d")
        }
        mock_collection.stream.return_value = [mock_doc]
        
        args = MagicMock()
        args.type = "forecast"
        with patch('process.SLACK_WEBHOOK_URL', 'http://slack'):
             process.cmd_check_alerts(args)
        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()
