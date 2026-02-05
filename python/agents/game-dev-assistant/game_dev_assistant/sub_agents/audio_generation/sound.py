import argparse
import base64
import os
import wave
from typing import Dict

from dotenv import load_dotenv
from google.api_core import exceptions
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

# Construct the path to the .env file relative to the current script
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

# Set the PROJECT_ID
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")


def musicgen_predict(
    instance_dict: Dict,
    location: str = "us-central1",
    api_endpoint: str = "aiplatform.googleapis.com",
    publisher_endpoint: str = "publishers/google/models/lyria-002",
):

    client_options = {"api_endpoint": api_endpoint}
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    instance = json_format.ParseDict(instance_dict, Value())
    instances = [instance]

    parameters_dict = {"duration_secs": 30}
    parameters = json_format.ParseDict(parameters_dict, Value())

    endpoint_path = (
        "projects/{project}/locations/{location}/{publisher_endpoint}".format(
            project=PROJECT_ID, location=location, publisher_endpoint=publisher_endpoint
        )
    )
    print(endpoint_path)

    response = client.predict(
        endpoint=endpoint_path, instances=instances, parameters=parameters
    )
    predictions = response.predictions
    print("Returned ", len(predictions), " samples")
    return predictions


def generate_music(prompt: str, output_filename: str):
    """Generates music based on a prompt and saves it to a file."""
    try:
        preds = musicgen_predict({"prompt": prompt})

        if preds:
            pred = preds[0]
            bytes_b64 = dict(pred)["bytesBase64Encoded"]
            decoded_audio_data = base64.b64decode(bytes_b64)

            # Ensure the output filename has a .wav extension
            if not output_filename.lower().endswith(".wav"):
                output_filename += ".wav"

            with wave.open(output_filename, "wb") as wf:
                wf.setnchannels(2)  # Assuming stereo
                wf.setsampwidth(2)  # Assuming 16-bit audio
                wf.setframerate(48000)  # Set sample rate
                wf.writeframes(decoded_audio_data)
            print(f"Generated music saved to {output_filename}")
        else:
            print("No predictions were returned from the model.")

    except exceptions.InvalidArgument as e:
        if "recitation checks" in str(e):
            print(
                "Audio generation failed because the prompt was blocked for safety reasons."
            )
            print(
                "This can happen if the prompt is too similar to existing copyrighted material."
            )
            print("Please try a more original or different prompt.")
        else:
            print(f"Audio generation failed: {e}")
            print("Please modify your prompt and try again.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # NOTE: If you are facing a PermissionDenied error, you need to authenticate with Google Cloud.
    # You can do this by running the following command in your terminal:
    # gcloud auth application-default login
    parser = argparse.ArgumentParser(description="Generate music from a text prompt.")
    parser.add_argument("prompt", type=str, help="The text prompt for the music.")
    args = parser.parse_args()

    output_filename = "generated_music"
    generate_music(args.prompt, output_filename)
