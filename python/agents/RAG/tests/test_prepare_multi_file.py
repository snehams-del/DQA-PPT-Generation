"""Unit tests for multiple-file support in prepare_corpus_and_data.py."""

import os
import sys
import types
from pathlib import Path

import pytest

# Import the module under test
import importlib

MODULE_PATH = "rag.shared_libraries.prepare_corpus_and_data"


def reload_module():
    """Reload the target module to ensure CLI parsing reads patched sys.argv."""
    if MODULE_PATH in sys.modules:
        return importlib.reload(sys.modules[MODULE_PATH])
    return importlib.import_module(MODULE_PATH)


def test__filename_from_url():
    prepare = reload_module()
    url = "https://example.com/path/to/myfile.pdf"
    assert prepare._filename_from_url(url) == "myfile.pdf"


@pytest.mark.parametrize("num_urls,num_files", [(1, 1), (2, 0), (0, 3)])
def test_main_multi_file(monkeypatch, tmp_path, num_urls, num_files):
    """Verify that `main` attempts to upload all provided files/URLs."""

    # Dynamically build CLI args
    url_list = [f"https://example.com/doc_{i}.pdf" for i in range(num_urls)]
    file_list_paths = []
    for i in range(num_files):
        f_path = tmp_path / f"local_{i}.pdf"
        f_path.write_bytes(b"dummy")
        file_list_paths.append(str(f_path))

    argv = ["prepare_corpus_and_data.py"]
    if url_list:
        argv.extend(["--pdf_urls", *url_list])
    if file_list_paths:
        argv.extend(["--pdf_files", *file_list_paths])

    upload_calls = []

    # Patch environment variables expected by the script
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "dummy-project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    # First load module to reference its names for monkeypatching
    prepare = reload_module()

    # Stub external side-effect functions
    monkeypatch.setattr(prepare, "initialize_vertex_ai", lambda: None)
    monkeypatch.setattr(prepare, "create_or_get_corpus", lambda: types.SimpleNamespace(name="corpus/test"))
    monkeypatch.setattr(prepare, "update_env_file", lambda *args, **kwargs: None)

    def fake_download(url: str, output_path: str):
        # Simulate download by writing bytes to the expected path
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as fp:
            fp.write(b"dummy")
        return output_path

    monkeypatch.setattr(prepare, "download_pdf_from_url", fake_download)

    def fake_upload(corpus_name, pdf_path, display_name, description):
        upload_calls.append((corpus_name, pdf_path, display_name, description))
        return None

    monkeypatch.setattr(prepare, "upload_pdf_to_corpus", fake_upload)
    monkeypatch.setattr(prepare, "list_corpus_files", lambda **kwargs: None)

    # Patch sys.argv and rerun module.main()
    monkeypatch.setattr(sys, "argv", argv)

    prepare.main()

    expected_total = num_urls + num_files if (num_urls + num_files) > 0 else 1  # default single PDF use-case
    assert len(upload_calls) == expected_total, (
        f"Expected {expected_total} uploads (URLs: {num_urls}, files: {num_files}), got {len(upload_calls)}"
    ) 