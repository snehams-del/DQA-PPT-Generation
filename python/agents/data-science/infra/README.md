# Data Science Agent Terraform Module

Provisions BigQuery datasets, Vertex AI RAG corpus, and supporting infrastructure for the Data Science Agent.

> **Note:** For setup instructions, see the main [README.md](../README.md#setup-and-installation) in the project root.

## Configuration

### Required Variables

```hcl
# vars/env.tfvars (when using advanced configuration)
project_id = "your-gcp-project-id"
```

### Optional Variables

```hcl
project_name = "data-science"  # Base name for resources
region       = "us-central1"   # GCP region
resource_name_prefix = "ds"    # Resource prefix

# Data paths (relative to infra/)
train_csv_path = "../data_science/utils/data/train.csv"
test_csv_path  = "../data_science/utils/data/test.csv"
```

## Resources Created

- **BigQuery**: Dataset `{prefix}_{project_name}` with train/test tables
- **Cloud Storage**: Staging bucket `{prefix}-{project_name}-staging`
- **Vertex AI**: RAG corpus `{prefix}-{project_name}-bqml-corpus`
- **APIs**: BigQuery, Vertex AI, Cloud Storage
- **IAM**: Required service account permissions

## Outputs

Key outputs for agent configuration:

```hcl
bigquery_dataset = {
  dataset_id = "ds_data_science"
  project    = "your-project-id"
}

rag_corpus = {
  corpus_name = "projects/123/locations/us-central1/ragCorpora/456"
}
```

## Verification

```bash
# Check BigQuery tables have data
bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM `PROJECT.ds_data_science.train`'
```

## Cleanup

```bash
terraform destroy
```