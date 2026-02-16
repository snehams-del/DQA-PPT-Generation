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

import os

PODCAST_TRANSCRIPT_MODEL_NAME = os.getenv("PODCAST_TRANSCRIPT_MODEL_NAME", "gemini-2.5-flash")
PODCAST_MODEL_GOOGLE_CLOUD_LOCATION = os.getenv("MODEL_GOOGLE_CLOUD_LOCATION", "global")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
TTS_LOCATION = os.getenv("TTS_LOCATION", GOOGLE_CLOUD_LOCATION)
