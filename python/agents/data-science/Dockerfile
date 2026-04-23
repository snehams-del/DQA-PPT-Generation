FROM python:3.12

# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip
# Install uv
RUN pip install --no-cache-dir uv>=0.7.19

# Copy only the dependency files to leverage Docker layer caching
COPY uv.lock pyproject.toml ./

# Remove any existing virtual environment and force system Python usage
RUN rm -rf .venv
ENV UV_SYSTEM_PYTHON=1

# Install project dependencies, sync to uv's lockfile using system Python
RUN uv sync

# Expose the port
EXPOSE 8080

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]