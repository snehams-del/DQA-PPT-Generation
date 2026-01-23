
import os
import requests
import json
import google.auth
from google.auth.transport.requests import Request

def get_token():
    credentials, project = google.auth.default()
    if not credentials.valid:
        credentials.refresh(Request())
    return credentials.token, project

def test_gemini_fix(model_name, location="us-central1"):
    print(f"\n--- Testing Gemini Fix: modelName='{model_name}' ---")
    token, project = get_token()
    hostname = f"{location}-texttospeech.googleapis.com"
    url = f"https://{hostname}/v1beta1/text:synthesize"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
        "x-goog-user-project": project
    }
    
    # Try using 'modelName' 
    payload = {
        "input": {
            "multiSpeakerMarkup": {
                "turns": [
                    {"text": "Hello, this is spk1.", "speaker": "spk1"},
                    {"text": "And this is spk2.", "speaker": "spk2"}
                ]
            }
        },
        "voice": {
            "languageCode": "en-US",
            "modelName": model_name,
            "multiSpeakerVoiceConfig": {
                "speakerVoiceConfigs": [
                    {"speakerAlias": "spk1", "speakerId": "Puck"},
                    {"speakerAlias": "spk2", "speakerId": "Charon"}
                ]
            }
        },
        "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 24000}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("Success! Audio generated.")
            return True
        else:
            print(f"Failed: {response.status_code} {response.reason}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    test_gemini_fix("gemini-2.5-pro-tts")
