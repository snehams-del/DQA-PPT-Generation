# Earth Engine enabled ADK agent

This directory contains a [Google Earth Engine](https://earthengine.google.com/)
enabled ADK agent implemented as a simple chatbot. 
The agent has a single tool that uses the [AlphaEarth Satellite Embeddings dataset](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_SATELLITE_EMBEDDING_V1_ANNUAL)
to compute the area of annual change between 2017-2025 in a geometry provided by
the user. The geometry is provided as GeoJSON text through the chat interface.
The tool converts the GeoJSON to an `ee.Geometry` and sends it to the Earth
Engine server for processing. The results of the computation are returned from
the server as a JSON dictionary with years for keys and square meters of change
as values. The agent uses these data and the coordinates in the geometry to
reason about land cover change and report back to the user.

## Manual setup

You will need a Google Cloud Project with the Earth Engine API and the Vertex
API enabled. Enter that project ID into the `.env` file. You will also need a
local development environment with ADK, Earth Engine, Numpy and the Google Cloud
SDK installed.

To install Python ADK and the Earth Engine client, you can use a package manager
such as `pip` or `pipx`. You may want to do the installs in a virtual
environment as follows.

```
pipx install -U virtualenv
python3 -m virtualenv ee-adk-env
source ee-adk-env/bin/activate
pip install -U earthengine-api
pip install -U google-adk
pip install -U numpy
```

Installation of the Google Cloud SDK depends on your environment. Follow
[these instructions](https://docs.cloud.google.com/sdk/docs/install-sdk) to
install the correct version.

To run the agent from a local host, first authenticate using the Google Cloud
CLI (you may also need to run `earthengine authenticate`):

```
cd <parent/directory/of/the/agent>
gcloud auth application-default login
adk web
```

The log should tell you the URL for the chat UI, but it will be something like:
`http://localhost:8000/`.

## Example Interaction

Interact with the agent through a chat interface. The agent can answer basic
questions about land cover change in small to medium sized polygons represented
as GeoJSON strings. For example, here's a small polygon in the Santa Cruz
mountains of California, USA:

```
{"type":"Polygon","coordinates":[[[-122.25468153773132,37.21100075492321],[-122.25468153773132,37.186046417670404],[-122.2224950295526,37.186046417670404],[-122.2224950295526,37.21100075492321]]],"geodesic":false,"evenOdd":true}
```

You can use a script like this to generate GeoJSON for your area(s) of interest:
https://code.earthengine.google.com/f81c949df0550ef68ea6aca3937ec9bd. Then you
can copy the GeoJSON printed in the Console of the Earth Engine Code Editor to a
chat:

User:

> Please tell me about
> {"type":"Polygon","coordinates":[[[-122.25468153773132,37.21100075492321],
> [-122.25468153773132,37.186046417670404],[-122.2224950295526,37.186046417670404],
> [-122.2224950295526, 37.21100075492321]]],"geodesic":false,"evenOdd":true}.

Agent:

> Based on an analysis of the provided geometry, here are the detected annual 
> changes for the years 2020 and 2021:
>
> - 2020: 3.45 square kilometers of change were detected. 
>
> - 2021: 2.74 square kilometers of change were detected.
>
> The provided coordinates are located in the Santa Cruz Mountains of California.
> The significant changes detected in 2020 are attributed to the CZU Lightning
> Complex fire, which burned a large area in this region in August 2020. The land
> cover transitioned from forest and shrubland to a burned landscape.
>
> The changes detected in 2021 represent post-fire effects, including vegetation
> regrowth and succession as the ecosystem begins to recover from the fire.

## Customization

This simple agent is extensible by providing more tools and more instructions
in the prompt. The tools can take this general form:

```python
@retry_async.AsyncRetry(deadline=60)
async def your_fancy_earth_engine_function(
    geojson: str,
) -> dict[str, Any]:
  """Gets some statistics about your area of interest (geojson).

  Args:
    geojson (str): A JSON string representing a GeoJSON geometry.

  Returns:
    A JSON dictionary.
  """
  region = ee.Geometry(json.loads(geojson))
  return await asyncio.to_thread(earth_engine_server_function(region).getInfo)
```

The `earth_engine_server_function` takes an `ee.Geometry` and returns an 
`ee.Dictionary` (the output of a `reduceRegion()` call), both of which are 
server variables. The `getInfo` call requests the result of the computation,
specifically the JSON representation of the `ee.Dictionary`. The function is
structured to make the request asynchronously and retry it it fails.

You can request textual representations of other server objects 
(`ee.SomeObject`) using `getInfo()`. You can also request patches of pixels
as images. See [this guide](https://developers.google.com/earth-engine/guides/data_extraction)
for examples of programmatically extracting image data.

## Disclaimer

This agent sample is provided for illustrative purposes only and is not intended
for production use. It serves as a basic example of an agent and a foundational
starting point for individuals or teams to develop their own agents.

This sample has not been rigorously tested, may contain bugs or limitations,
and does not include features or optimizations typically required for a
production environment (e.g., robust error handling, security measures,
scalability, performance considerations, comprehensive logging, or advanced
configuration options).

Users are solely responsible for any further development, testing, security
hardening, and deployment of agents based on this sample. We recommend thorough
review, testing, and the implementation of appropriate safeguards before using
any derived agent in a live or critical system.
