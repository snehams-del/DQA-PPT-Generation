import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Audio Generation Agent</title>
        </head>
        <body>
            <h1>Audio Generation Agent</h1>
            <form action="/generate" method="post">
                <label for="prompt">Prompt:</label><br>
                <input type="text" id="prompt" name="prompt" value="a light and happy ukulele song"><br>
                <label for="duration">Duration (seconds):</label><br>
                <input type="number" id="duration" name="duration" value="5"><br><br>
                <input type="submit" value="Generate Audio">
            </form>
        </body>
    </html>
    """


@app.post("/generate")
async def generate_audio(request: Request):
    form = await request.form()
    prompt = form["prompt"]
    duration = int(form["duration"])

    # Run the agent script
    os.system(f"python3 agent_testing/audio_generation/agent.py '{prompt}' {duration}")

    return FileResponse("output.wav", media_type="audio/wav", filename="output.wav")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
