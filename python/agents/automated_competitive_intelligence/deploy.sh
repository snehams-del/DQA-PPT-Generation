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

# Get latest commit ID
export COMMIT_SHA=$(git rev-parse --short HEAD)

# Check if the command worked
if [ -z "$COMMIT_SHA" ]; then
    echo "Error: Could not get commit SHA."
    echo "Make sure you are running this script from within a git repository."
    exit 1
fi

echo "==========================================================="
echo " Pre-Flight Build Verifications"
echo "==========================================================="
if [ ! -d "frontend" ] || [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: 'frontend/package.json' missing!"
    echo "React application configurations must be physically present before Cloud Build launches."
    exit 1
fi

if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Python backend 'pyproject.toml' missing!"
    exit 1
fi

echo "✅ Environment integrity verified. Bootscript validated!"

# Finally, deploy
gcloud builds submit --config cloudbuild.yaml --substitutions=SHORT_SHA=$COMMIT_SHA

# Setup IAP for GCC
gcloud beta iap web add-iam-policy-binding \
    --resource-type=cloud-run \
    --service="competitive-intelligence-agent-v1" \
    --region="us-central1" \
    --member=group:"gcc-all@google.com" \
    --role=roles/iap.httpsResourceAccessor \
    --condition=None
