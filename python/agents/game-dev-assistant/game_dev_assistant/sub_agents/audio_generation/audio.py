import os
import sys
import wave

import google.genai as genai
from dotenv import load_dotenv
from google.genai import types

load_dotenv()

API_KEY = os.getenv("API_KEY")
client = genai.Client(api_key=API_KEY)

VOICE_POOL = ["Puck", "Kore", "Aoede", "Charon"]

def generate_audio_agent(user_prompt, scene_context=""):
    print(f"🚀 Starting Audio Agent for: {user_prompt}")

    # --- STEP 1: SCRIPT GENERATION ---
    print("📝 Step 1: Generating Unity C# Logic...")
    script_prompt = (
        f"Context: {scene_context}. Generate a C# script for Unity to play 'generated_sfx.wav'. "
        "Use 3D spatial settings. Output ONLY raw code, no markdown."
    )

    script_response = client.models.generate_content(
        model="gemini-2.0-flash", contents=script_prompt
    )
    with open("SpatialAudioTrigger.cs", "w") as f:
        f.write(
            script_response.text.replace("```csharp", "").replace("```", "").strip()
        )
    print("✅ Script Saved.")

    # --- STEP 2: AUDIO GENERATION WITH RETRY LOOP ---
    print("🔊 Step 2: Synthesizing Sound Effect...")
    try:
        audio_response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=f"Generate a sound effect of: {user_prompt}",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Puck"
                        )
                    )
                ),
            ),
        )

        for part in audio_response.candidates[0].content.parts:
            if part.inline_data:
                raw_pcm_data = part.inline_data.data
                audio_filename = "generated_sfx.wav"

                with wave.open(audio_filename, "wb") as wf:
                    wf.setnchannels(1)  # Mono
                    wf.setsampwidth(2)  # 16-bit is 2 bytes
                    wf.setframerate(24000)  # 24kHz
                    wf.writeframes(raw_pcm_data)

                print(f"✅ Audio Saved with Header: {audio_filename}")
                # ---------------------------------------------

    except Exception as e:
        print(f"❌ Audio Step Failed: {e}")

    return "Audio generation complete"


if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "a scary monster roaring"
    generate_audio_agent(prompt)
