# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
import random
from typing import Literal

from fastmcp import FastMCP

mcp = FastMCP("Weather Data Server")


@mcp.tool
def get_temperature(
    unit: Literal["celsius", "fahrenheit"] = "celsius",
) -> float:
  """Provides the current temperature."""
  # Returns a random temperature between -10 and 40 degrees Celsius
  temp_celsius = random.uniform(-10.0, 40.0)
  if unit == "fahrenheit":
    return round((temp_celsius * 9 / 5) + 32, 2)
  return round(temp_celsius, 2)


@mcp.tool
def get_wind_speed() -> float:
  """Provides the current wind speed in kilometers per hour."""
  # Returns a random wind speed between 0 and 50 km/h
  return round(random.uniform(0.0, 50.0), 2)


@mcp.tool
def get_rain_probability() -> float:
  """Provides the probability of rain as a percentage."""
  # Returns a random probability between 0 and 100 percent
  return round(random.uniform(0.0, 100.0), 2)


@mcp.tool
def get_humidity() -> float:
  """Provides the current humidity as a percentage."""
  # Returns a random humidity level between 0 and 100 percent
  return round(random.uniform(0.0, 100.0), 2)


# Create ASGI application
app = mcp.streamable_http_app()
