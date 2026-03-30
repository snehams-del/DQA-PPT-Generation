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

import vertexai
from vertexai.preview.evaluation import (
    PointwiseMetric,
    MetricPromptTemplateExamples,
    EvalTask,
)
try:
    from ..config import (
        GOOGLE_CLOUD_LOCATION,
    )
except ImportError:
    from podcast_agent.config import (
        GOOGLE_CLOUD_LOCATION,
    )

def init_vertex_eval():
    """Initializes Vertex AI for evaluation."""
    # Note: We assume project is set via env var or ADC.
    # location here refers to the EVALUATION SERVICE location.
    vertexai.init(location=GOOGLE_CLOUD_LOCATION)

def get_pointwise_metrics():
    """Returns a list of pointwise metrics to use for evaluation."""
    groundedness = PointwiseMetric(
        metric="groundedness",
        metric_prompt_template=MetricPromptTemplateExamples.Pointwise.GROUNDEDNESS,
    )
    fluency = PointwiseMetric(
        metric="fluency",
        metric_prompt_template=MetricPromptTemplateExamples.Pointwise.FLUENCY,
    )
    coherence = PointwiseMetric(
        metric="coherence",
        metric_prompt_template=MetricPromptTemplateExamples.Pointwise.COHERENCE,
    )
    return [groundedness, fluency, coherence]
