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

from google.auth import default
import vertexai
from vertexai.preview import rag
import os
from dotenv import load_dotenv, set_key
import requests
import tempfile
import argparse
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv()

# --- Please fill in your configurations ---
# Retrieve the PROJECT_ID from the environmental variables.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError(
        "GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file."
    )
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not LOCATION:
    raise ValueError(
        "GOOGLE_CLOUD_LOCATION environment variable not set. Please set it in your .env file."
    )
ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Default corpus metadata. Can be overridden via CLI.
CORPUS_DISPLAY_NAME = "Alphabet_10K_2024_corpus"
CORPUS_DESCRIPTION = "Corpus containing documentation files"

# Default single-file example (kept for backwards compatibility).
DEFAULT_PDF_URL = "https://abc.xyz/assets/77/51/9841ad5c4fbe85b4440c47a4df8d/goog-10-k-2024.pdf"

# --- Start of the script ---
def initialize_vertex_ai():
  credentials, _ = default()
  vertexai.init(
      project=PROJECT_ID, location=LOCATION, credentials=credentials
  )


def create_or_get_corpus():
  """Creates a new corpus or retrieves an existing one."""
  embedding_model_config = rag.EmbeddingModelConfig(
      publisher_model="publishers/google/models/text-embedding-004"
  )
  existing_corpora = rag.list_corpora()
  corpus = None
  for existing_corpus in existing_corpora:
    if existing_corpus.display_name == CORPUS_DISPLAY_NAME:
      corpus = existing_corpus
      print(f"Found existing corpus with display name '{CORPUS_DISPLAY_NAME}'")
      break
  if corpus is None:
    corpus = rag.create_corpus(
        display_name=CORPUS_DISPLAY_NAME,
        description=CORPUS_DESCRIPTION,
        embedding_model_config=embedding_model_config,
    )
    print(f"Created new corpus with display name '{CORPUS_DISPLAY_NAME}'")
  return corpus


def download_pdf_from_url(url: str, output_path: str):
  """Downloads a PDF file from the specified URL."""
  print(f"Downloading PDF from {url}...")
  response = requests.get(url, stream=True)
  response.raise_for_status()  # Raise an exception for HTTP errors
  
  with open(output_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
      f.write(chunk)
  
  print(f"PDF downloaded successfully to {output_path}")
  return output_path


def upload_pdf_to_corpus(corpus_name: str, pdf_path: str, display_name: str, description: str):
  """Uploads a PDF file to the specified corpus."""
  print(f"Uploading {display_name} to corpus...")
  try:
    rag_file = rag.upload_file(
        corpus_name=corpus_name,
        path=pdf_path,
        display_name=display_name,
        description=description,
    )
    print(f"Successfully uploaded {display_name} to corpus")
    return rag_file
  except Exception as e:
    print(f"Error uploading file {display_name}: {e}")
    return None

def update_env_file(corpus_name, env_file_path):
    """Updates the .env file with the corpus name."""
    try:
        set_key(env_file_path, "RAG_CORPUS", corpus_name)
        print(f"Updated RAG_CORPUS in {env_file_path} to {corpus_name}")
    except Exception as e:
        print(f"Error updating .env file: {e}")

def list_corpus_files(corpus_name):
  """Lists files in the specified corpus."""
  files = list(rag.list_files(corpus_name=corpus_name))
  print(f"Total files in corpus: {len(files)}")
  for file in files:
    print(f"File: {file.display_name} - {file.name}")

def _create_temp_dir() -> tempfile.TemporaryDirectory:
  """Creates and returns a TemporaryDirectory instance."""
  return tempfile.TemporaryDirectory()


def _filename_from_url(url: str) -> str:
  """Derives a filename from the last path component of the URL."""
  parsed = urlparse(url)
  return os.path.basename(parsed.path) or "downloaded_file.pdf"


# -----------------------------------------------------------------------------
# Entry-point
# -----------------------------------------------------------------------------

def main():
  """Entry-point for CLI/Script.

  Supports uploading multiple files to an existing or newly created RAG corpus.
  Files can be provided via URLs (they will be downloaded first) or local file
  paths. If no files are provided, the script falls back to a default single
  PDF example for backwards compatibility.
  """

  global CORPUS_DISPLAY_NAME, CORPUS_DESCRIPTION  # declare globals before use

  parser = argparse.ArgumentParser(description="Prepare corpus and upload PDF files to Vertex AI RAG")
  parser.add_argument(
      "--pdf_urls",
      nargs="*",
      help="One or more PDF URLs to download and upload.",
  )
  parser.add_argument(
      "--pdf_files",
      nargs="*",
      help="One or more local PDF file paths to upload.",
  )
  parser.add_argument(
      "--corpus_display_name",
      default=CORPUS_DISPLAY_NAME,
      help=f"Display name for the corpus (default: {CORPUS_DISPLAY_NAME}).",
  )
  parser.add_argument(
      "--corpus_description",
      default=CORPUS_DESCRIPTION,
      help="Description for the corpus.",
  )

  args = parser.parse_args()

  # Update global metadata if the user provided overrides.
  CORPUS_DISPLAY_NAME = args.corpus_display_name
  CORPUS_DESCRIPTION = args.corpus_description

  pdf_urls = args.pdf_urls or []
  pdf_files = args.pdf_files or []

  # Fallback to default example when no input is provided.
  if not pdf_urls and not pdf_files:
    pdf_urls.append(DEFAULT_PDF_URL)

  initialize_vertex_ai()
  corpus = create_or_get_corpus()

  # Ensure the .env file contains the correct corpus name so the retrieval
  # agent can reference it later.
  update_env_file(corpus.name, ENV_FILE_PATH)

  # Handle URL downloads inside a temporary directory to avoid cluttering the
  # workspace.
  with _create_temp_dir() as temp_dir:
    # First process URLs.
    for url in pdf_urls:
      try:
        filename = _filename_from_url(url)
        pdf_path = os.path.join(temp_dir, filename)
        download_pdf_from_url(url, pdf_path)
        upload_pdf_to_corpus(
            corpus_name=corpus.name,
            pdf_path=pdf_path,
            display_name=filename,
            description=f"Uploaded from URL: {url}",
        )
      except Exception as exc:
        print(f"❌ Skipped {url}: {exc}")

    # Next process local files.
    for file_path in pdf_files:
      if not os.path.isfile(file_path):
        print(f"❌ File not found: {file_path}. Skipping.")
        continue
      filename = os.path.basename(file_path)
      upload_pdf_to_corpus(
          corpus_name=corpus.name,
          pdf_path=file_path,
          display_name=filename,
          description="Uploaded from local filesystem.",
      )

  # Finally, show the corpus contents to the user.
  list_corpus_files(corpus_name=corpus.name)

if __name__ == "__main__":
  main()
