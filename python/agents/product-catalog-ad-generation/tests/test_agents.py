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

import importlib
from unittest.mock import MagicMock, patch

from google.adk.apps import App


def _load_root_agent():
    with (
        patch("google.auth.default", return_value=(None, "test-project")),
        patch("google.genai.Client", return_value=MagicMock()),
    ):
        package = importlib.import_module("content_gen_agent")
    return package.root_agent


def test_runner_uses_app_wrapper() -> None:
    root_agent = _load_root_agent()
    app = App(name="product_catalog_ad_generation", root_agent=root_agent)

    with patch("google.adk.runners.InMemoryRunner") as runner_cls:
        runner_cls(app=app)

    runner_cls.assert_called_once_with(app=app)
