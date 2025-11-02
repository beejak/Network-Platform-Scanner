# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only pyproject.toml and poetry.lock to leverage Docker cache
COPY pyproject.toml poetry.lock /app/

# Install dependencies
RUN poetry install --no-root --no-dev

# Copy the rest of the application
COPY . /app/

# Command to run the application
CMD ["poetry", "run", "uvicorn", "platform_core.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
