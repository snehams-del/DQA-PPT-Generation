#!/bin/bash
# This script replays a standard creation and edit session for local verification.

# 1. Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 2. Create a temporary replay file in the project root
REPLAY_FILE="$PROJECT_ROOT/tests/e2e_replay.json"

cat << 'JSON_EOF' > "$REPLAY_FILE"
{
  "state": {},
  "queries": [
    "Create a 3-slide presentation about the history of Irvine, CA. Just generate it fast.",
    "Please edit the title of slide 2 to be 'The Birth of a Master-Planned City'."
  ]
}
JSON_EOF

# 3. Run the agent using the ADK CLI from the project root
echo "🚀 Running End-to-End Replay Test..."
cd "$PROJECT_ROOT"
adk run presentation_agent --replay "$REPLAY_FILE"

# 4. Cleanup
echo "🧹 Cleaning up..."
rm "$REPLAY_FILE"
