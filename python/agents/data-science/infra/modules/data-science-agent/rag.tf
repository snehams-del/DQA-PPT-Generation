# RAG Corpus for BQML Reference Guide
# Note: google_vertex_ai_corpus_rag is not yet available in Terraform
# Using local-exec provisioner as a workaround

resource "null_resource" "rag_corpus" {
  triggers = {
    project_id      = var.project_id
    region          = "us-east4"
    display_name    = local.rag_corpus_name
    data_sources    = join(",", var.rag_data_sources)
    python_path     = "${path.root}/../data_science/utils"
  }

  # Create RAG corpus using Python script
  provisioner "local-exec" {
    command = <<-EOT
      export GOOGLE_CLOUD_PROJECT=${var.project_id}
      export GOOGLE_CLOUD_LOCATION=us-east4
      cd ${path.root}/..
      uv run python -c "
import sys
sys.path.append('data_science/utils')
import os
import vertexai
from vertexai import rag

# Initialize Vertex AI
vertexai.init(project='${var.project_id}', location='us-east4')

# Configure embedding model
embedding_model_config = rag.RagEmbeddingModelConfig(
    vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
        publisher_model='publishers/google/models/text-embedding-005'
    )
)

backend_config = rag.RagVectorDbConfig(
    rag_embedding_model_config=embedding_model_config
)

# Create corpus
bqml_corpus = rag.create_corpus(
    display_name='${local.rag_corpus_name}',
    backend_config=backend_config,
)

print(f'CORPUS_NAME={bqml_corpus.name}')
      "
    EOT
  }

  # Delete RAG corpus on destroy
  provisioner "local-exec" {
    when    = destroy
    command = <<-EOT
      export GOOGLE_CLOUD_PROJECT=${self.triggers.project_id}
      export GOOGLE_CLOUD_LOCATION=us-east4
      uv run python -c "
import vertexai
from vertexai import rag
import os

# Initialize Vertex AI
vertexai.init(project='${self.triggers.project_id}', location='us-east4')

try:
    # List and find corpus
    corpora = rag.list_corpora()
    for corpus in corpora:
        if '${self.triggers.display_name}' in corpus.display_name:
            rag.delete_corpus(name=corpus.name)
            print(f'Deleted corpus: {corpus.name}')
            break
except Exception as e:
    print(f'Error deleting corpus: {e}')
      "
    EOT
  }

  depends_on = [google_project_service.required_apis]
}

# Extract corpus name from the creation output
data "external" "rag_corpus_info" {
  program = ["bash", "-c", <<-EOT
    cd ${path.root}/..
    source .venv/bin/activate
    python -c "
import sys
import os
import vertexai
from vertexai import rag
import json

# Initialize Vertex AI
vertexai.init(project='${var.project_id}', location='us-east4')

try:
    # List corpora and find the one we created
    corpora = rag.list_corpora()
    for corpus in corpora:
        if '${local.rag_corpus_name}' in corpus.display_name:
            result = {
                'name': corpus.name,
                'display_name': corpus.display_name,
                'location': 'us-east4'
            }
            print(json.dumps(result))
            sys.exit(0)
    
    # If not found, return empty
    print(json.dumps({'name': '', 'display_name': '', 'location': ''}))
except Exception as e:
    print(json.dumps({'name': '', 'display_name': '', 'location': '', 'error': str(e)}))
    sys.exit(1)
    "
    EOT
  ]
  
  depends_on = [null_resource.rag_corpus]
}

# Ingest files into RAG corpus
resource "null_resource" "rag_files_ingestion" {
  triggers = {
    corpus_name   = data.external.rag_corpus_info.result.name
    data_sources  = join(",", var.rag_data_sources)
    project_id    = var.project_id
    region        = "us-east4"
  }

  # Ingest files into corpus
  provisioner "local-exec" {
    command = <<-EOT
      export GOOGLE_CLOUD_PROJECT=${var.project_id}
      export GOOGLE_CLOUD_LOCATION=us-east4
      cd ${path.root}/..
      uv run python -c "
import vertexai
from vertexai import rag

# Initialize Vertex AI
vertexai.init(project='${var.project_id}', location='us-east4')

corpus_name = '${data.external.rag_corpus_info.result.name}'
if corpus_name:
    paths = [${join(", ", [for path in var.rag_data_sources : "'${path}'"])}]
    
    transformation_config = rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(
            chunk_size=512,
            chunk_overlap=100,
        ),
    )
    
    try:
        rag.import_files(
            corpus_name,
            paths,
            transformation_config=transformation_config,
            max_embedding_requests_per_min=1000,
        )
        print('Files ingested successfully')
        
        # List files
        files = list(rag.list_files(corpus_name))
        print(f'Ingested {len(files)} files')
        
    except Exception as e:
        print(f'Error ingesting files: {e}')
else:
    print('Corpus name not found, skipping file ingestion')
      "
    EOT
  }

  depends_on = [
    null_resource.rag_corpus,
    data.external.rag_corpus_info
  ]
}