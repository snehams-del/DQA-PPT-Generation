# FILENAME: main_server.py
# IMPERIAL DIRECTIVE: FORGE THE TITAN API GATEWAY V0.1

from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    if not data or 'directive' not in data:
        return jsonify({"error": "Missing 'directive' in request body"}), 400

    founder_directive = data['directive']

    # Simple routing logic
    if "architectus" in founder_directive.lower() or "cio" in founder_directive.lower():
        agent_name = "cio_agent"
    elif "midas" in founder_directive.lower() or "cfo" in founder_directive.lower():
        agent_name = "cfo_agent"
    elif "praetor" in founder_directive.lower() or "coo" in founder_directive.lower():
        agent_name = "coo_agent"
    else:
        # Default to cio_agent if no specific agent is mentioned
        agent_name = "cio_agent"

    try:
        # Execute the adk run command
        process = subprocess.run(
            f'echo "{founder_directive}" | adk run {agent_name}',
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        
        # The output from `adk run` is a bit verbose. We need to parse it to get the agent's response.
        # This is a fragile parsing logic and might need to be improved.
        lines = process.stdout.splitlines()
        response = ""
        for line in lines:
            if line.startswith(f"[{agent_name.replace('_agent', '')}"):
                 response = line.split("]: ")[1]
                 break
        
        return jsonify({"response": response})

    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
