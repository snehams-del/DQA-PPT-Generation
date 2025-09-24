# Weather Data Server

This is a sample Model Context Protocol (MCP) server that provides
random weather data via four distinct tools. It's built using
 the `fastmcp` Python library.

## Features

The server exposes the following tools:

* `get_temperature`: Provides a random temperature in Celsius or Fahrenheit.

* `get_wind_speed`: Provides a random wind speed in kilometers per hour.

* `get_rain_probability`: Provides a random probability of rain as a percentage.

* `get_humidity`: Provides a random humidity level as a percentage.

## Prerequisites

It's recommended to use a virtual environment.

`pip install -r requirements.txt`


## How to Run

The server can be run as an ASGI application. Use `uvicorn` to start it:

`uvicorn server:app --host 0.0.0.0 --port 8080`

The server will be available at `http://127.0.0.1:8080/mcp`.

## Deploy to Cloud Run
The following command can be used to deploy the mcp server on Cloud Run.

`gcloud run deploy weather-mcp-service --region us-central1  --source .`

## Tools

Each tool is designed to be called asynchronously. The definitions are available
 in the `server.py` file.

### `get_temperature`

get_temperature(unit: Literal["celsius", "fahrenheit"] = "celsius") -> float


This tool returns a random temperature. The `unit` parameter can be used to
 specify the desired unit.

### `get_wind_speed`

get_wind_speed() -> float


This tool returns a random wind speed in kilometers per hour.

### `get_rain_probability`

get_rain_probability() -> float


This tool returns a random percentage representing the probability of rain.

### `get_humidity`

get_humidity() -> float


This tool returns a random percentage for the current humidity.