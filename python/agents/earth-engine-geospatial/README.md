# Earth Engine enabled ADK agent

This directory contains an Earth Engine enabled ADK agent. You will need a
Google Cloud Project with the Earth Engine API and the Vertex API enabled. Enter
that project ID into the `.env` file. You will also need a local development
environment with ADK, Earth Engine, Numpy and the Google Cloud SDK installed.

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

You interact with the agent through a chat interface. The agent can answer basic
questions about land cover change in small to medium sized polygons represented
as GeoJSON strings. For example, here's a small polygon in the Santa Cruz
mountains of California, USA:

```
{"type":"Polygon","coordinates":[[[-122.25468153773132,37.21100075492321],[-122.25468153773132,37.186046417670404],[-122.2224950295526,37.186046417670404],[-122.2224950295526,37.21100075492321]]],"geodesic":false,"evenOdd":true}
```

You can use a script like this to generate GeoJSON for your area(s) of interest:
https://code.earthengine.google.com/f81c949df0550ef68ea6aca3937ec9bd.
