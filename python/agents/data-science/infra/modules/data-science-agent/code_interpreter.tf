# Code Interpreter Extension for Vertex AI
# Using local-exec provisioner since Terraform doesn't have native support

resource "null_resource" "code_interpreter_extension" {
  count = var.create_code_interpreter ? 1 : 0

  triggers = {
    project_id = var.project_id
    region     = "us-east4"
  }

  # Create Code Interpreter Extension
  provisioner "local-exec" {
    command = <<-EOT
      export GOOGLE_CLOUD_PROJECT=${var.project_id}
      export GOOGLE_CLOUD_LOCATION=${var.region}
      cd ${path.root}/..
      
      uv run python -c "
import os
import sys
import json
import logging
import vertexai
from vertexai.preview.extensions import Extension

# Initialize Vertex AI
vertexai.init(project='${var.project_id}', location='${var.region}')

try:
    # Check if extension already exists by looking for existing code interpreter extensions
    extensions = Extension.list(location='${var.region}')
    existing_extension = None
    
    for extension in extensions:
        if 'Code Interpreter' in extension.gca_resource.display_name:
            existing_extension = extension
            break
    
    if existing_extension:
        extension_name = existing_extension.gca_resource.name
        print(f'Using existing extension: {extension_name}')
        
        # Write extension name to state file for cleanup
        with open('/tmp/terraform_code_interpreter_${var.project_id}_${var.region}.txt', 'w') as f:
            f.write(f'{extension_name}|existing')
    else:
        # Create new extension from hub
        print('Creating new Code Interpreter extension...')
        new_extension = Extension.from_hub('code_interpreter')
        extension_name = new_extension.gca_resource.name
        print(f'Created extension: {extension_name}')
        
        # Write extension name to state file for cleanup  
        with open('/tmp/terraform_code_interpreter_${var.project_id}_${var.region}.txt', 'w') as f:
            f.write(f'{extension_name}|created')
        
except Exception as e:
    print(f'Error managing extension: {e}', file=sys.stderr)
    # Create empty state file to indicate failure
    with open('/tmp/terraform_code_interpreter_${var.project_id}_${var.region}.txt', 'w') as f:
        f.write('|error')
    sys.exit(0)  # Don't fail terraform, just continue without extension
      "
    EOT
  }

  # Delete Code Interpreter Extension (only if we created it)
  provisioner "local-exec" {
    when = destroy
    command = <<-EOT
      cd ${path.root}/..
      uv run python -c "
import os
import sys
import vertexai
from vertexai.preview.extensions import Extension

try:
    # Read state file to determine if we should delete
    state_file = '/tmp/terraform_code_interpreter_${self.triggers.project_id}_${self.triggers.region}.txt'
    if not os.path.exists(state_file):
        print('No state file found, nothing to delete')
        sys.exit(0)
    
    with open(state_file, 'r') as f:
        content = f.read().strip()
    
    if not content or content.endswith('|error'):
        print('No valid extension to delete')
        sys.exit(0)
    
    extension_name, creation_type = content.split('|')
    
    if creation_type == 'existing':
        print(f'Extension {extension_name} was pre-existing, not deleting')
        sys.exit(0)
    elif creation_type == 'created':
        print(f'Deleting extension {extension_name} that was created by Terraform...')
        vertexai.init(project='${self.triggers.project_id}', location='${self.triggers.region}')
        
        # Load and delete the extension
        extension = Extension(extension_name)
        extension.delete()
        print(f'Successfully deleted extension {extension_name}')
    
    # Clean up state file
    os.remove(state_file)
    
except Exception as e:
    print(f'Error during extension cleanup: {e}', file=sys.stderr)
    # Don't fail the destroy operation
    sys.exit(0)
      "
    EOT
  }

  depends_on = [google_project_service.required_apis]
}

# Extract extension information
data "external" "code_interpreter_info" {
  count = var.create_code_interpreter ? 1 : 0
  
  program = ["bash", "-c", <<-EOT
    cd ${path.root}/..
    python -c "
import sys
import os
import json

try:
    # Read from state file created by the provisioner
    state_file = f'/tmp/terraform_code_interpreter_${var.project_id}_${var.region}.txt'
    
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            content = f.read().strip()
        
        if content and not content.endswith('|error'):
            extension_name, creation_type = content.split('|')
            
            # Get display name from the resource name
            display_name = 'Code Interpreter'
            if extension_name:
                # Extract display name from resource path if possible
                parts = extension_name.split('/')
                if len(parts) > 1:
                    display_name = f'Code Interpreter ({parts[-1]})'
            
            result = {
                'name': display_name,
                'resource_name': extension_name,
                'created': 'true' if creation_type in ['created', 'existing'] else 'false'
            }
        else:
            result = {
                'name': '',
                'resource_name': '',
                'created': 'false'
            }
    else:
        result = {
            'name': '',
            'resource_name': '',
            'created': 'false'
        }
    
    print(json.dumps(result))
    
except Exception as e:
    result = {
        'name': '',
        'resource_name': '',
        'created': 'false',
        'error': str(e)
    }
    print(json.dumps(result))
    "
    EOT
  ]
  
  depends_on = [null_resource.code_interpreter_extension]
}