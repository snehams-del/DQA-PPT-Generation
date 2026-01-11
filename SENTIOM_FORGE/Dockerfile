# Dockerfile for SENTIOM AI Titans
# Base Image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent modules
COPY cio_agent /app/cio_agent
COPY cfo_agent /app/cfo_agent
COPY coo_agent /app/coo_agent

# Copy the main application entrypoint
COPY main_server.py .

# Expose the port the server will run on
EXPOSE 8080

# Command to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "main_server:app"]
