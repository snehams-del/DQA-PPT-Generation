#!/usr/bin/env bash
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Exit immediately for non-zero status
set -e

echo "==========================================================="
echo " Starting Competitive Intelligence Engine - Local Dev Setup "
echo "==========================================================="

# Ask user for which UI to run : Streamlit or React.JS
echo "Which UI would you like to run?"
echo "1) Streamlit UI"
echo "2) React UI + FastAPI Backend"
read -p "Enter choice [1 or 2]: " ui_choice

# Cleanup function to kill background processes when the script exits
cleanup() {
    echo ""
    echo "Shutting down servers..."
    # Kill the backend server
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    # Kill the frontend server
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo "Cleanup complete. Exiting."
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM exit

# Set the virtual environment
source .venv/bin/activate

# depending on choice by user, run the UI (+ backend if React)
# For Streamlit choice, we do not require a backend.
if [ "$ui_choice" == "1" ]; then
    echo "[1/1] Starting Streamlit UI..."
    streamlit run streamlit_app.py &
    FRONTEND_PID=$!
    echo "Streamlit running with PID: $FRONTEND_PID"
    
    echo "==========================================================="
    echo " Streamlit Dashboard: http://localhost:8501"
    echo " Press Ctrl+C to stop."
    echo "==========================================================="
else
    echo "[1/2] Starting FastAPI Backend on config port 8000..."
    uvicorn backend.api.main:app --port 8000 --reload &
    BACKEND_PID=$!
    echo "Backend running with PID: $BACKEND_PID"

    echo "[2/2] Starting React Frontend on config port 5173..."
    # Ensure the correct PATH for node/npm via Homebrew
    export PATH="/opt/homebrew/bin:$PATH"
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend running with PID: $FRONTEND_PID"

    echo "==========================================================="
    echo " API Server:      http://localhost:8000/api/health"
    echo " React Dashboard: http://localhost:5173"
    echo " Press Ctrl+C to stop both servers."
    echo "==========================================================="
fi

# Wait indefinitely to keep the script running
# allowing cleanup trap to catch signals
wait
