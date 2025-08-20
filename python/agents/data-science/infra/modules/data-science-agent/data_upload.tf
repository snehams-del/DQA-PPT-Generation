# Data upload to BigQuery using local-exec provisioners
# This handles CSV data loading since Terraform doesn't natively support BigQuery data loading

resource "null_resource" "bigquery_data_upload" {
  triggers = {
    dataset_id            = local.dataset_id
    bq_data_project_id   = var.bq_data_project_id
    bq_compute_project_id = var.bq_compute_project_id
    train_csv_path       = var.train_csv_path
    test_csv_path        = var.test_csv_path
    # Add file hashes to trigger on file changes
    train_csv_hash = fileexists("${path.root}/../${var.train_csv_path}") ? filemd5("${path.root}/../${var.train_csv_path}") : ""
    test_csv_hash  = fileexists("${path.root}/../${var.test_csv_path}") ? filemd5("${path.root}/../${var.test_csv_path}") : ""
  }

  # Upload training data
  provisioner "local-exec" {
    command = <<-EOT
      export BQ_DATA_PROJECT_ID=${var.bq_data_project_id}
      export BQ_COMPUTE_PROJECT_ID=${var.bq_compute_project_id}
      export BQ_DATASET_ID=${local.dataset_id}
      
      cd ${path.root}/..
      
      uv run python -c "
import os
from pathlib import Path
from google.cloud import bigquery

def load_csv_to_bigquery(data_project_id, dataset_name, table_name, csv_filepath):
    '''Loads a CSV file into a BigQuery table.'''
    
    client = bigquery.Client(project=data_project_id)
    dataset_ref = client.dataset(dataset_name)
    table_ref = dataset_ref.table(table_name)
    
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  # Skip the header row
        autodetect=True,  # Automatically detect the schema
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrite table
    )
    
    try:
        with open(csv_filepath, 'rb') as source_file:
            job = client.load_table_from_file(
                source_file, table_ref, job_config=job_config
            )
        
        job.result()  # Wait for the job to complete
        
        print(f'Loaded {job.output_rows} rows into {dataset_name}.{table_name}')
        return True
    except Exception as e:
        print(f'Error loading data to {table_name}: {e}')
        return False

# Load training data
data_project_id = os.getenv('BQ_DATA_PROJECT_ID')
dataset_name = os.getenv('BQ_DATASET_ID')

print('Loading training data...')
train_success = load_csv_to_bigquery(
    data_project_id,
    dataset_name, 
    'train',
    '${var.train_csv_path}'
)

print('Loading test data...')
test_success = load_csv_to_bigquery(
    data_project_id,
    dataset_name,
    'test', 
    '${var.test_csv_path}'
)

if train_success and test_success:
    print('All data loaded successfully')
else:
    print('Some data loading failed')
    exit(1)
      "
    EOT
  }

  depends_on = [
    google_bigquery_table.train,
    google_bigquery_table.test
  ]
}

# Verify data was loaded successfully
data "external" "bigquery_row_counts" {
  program = ["bash", "-c", <<-EOT
    cd ${path.root}/..
    source .venv/bin/activate
    python -c "
import json
import os
from google.cloud import bigquery

try:
    client = bigquery.Client(project='${var.bq_compute_project_id}')
    
    # Count rows in train table
    train_query = '''
    SELECT COUNT(*) as row_count 
    FROM \`${var.bq_data_project_id}.${local.dataset_id}.train\`
    '''
    train_result = client.query(train_query).result()
    train_count = list(train_result)[0].row_count
    
    # Count rows in test table  
    test_query = '''
    SELECT COUNT(*) as row_count 
    FROM \`${var.bq_data_project_id}.${local.dataset_id}.test\`
    '''
    test_result = client.query(test_query).result()
    test_count = list(test_result)[0].row_count
    
    result = {
        'train_rows': str(train_count),
        'test_rows': str(test_count),
        'total_rows': str(train_count + test_count)
    }
    
    print(json.dumps(result))
    
except Exception as e:
    print(json.dumps({
        'train_rows': '0',
        'test_rows': '0', 
        'total_rows': '0',
        'error': str(e)
    }))
    "
    EOT
  ]
  
  depends_on = [null_resource.bigquery_data_upload]
}