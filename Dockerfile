FROM python:3.12-slim

WORKDIR /app

# Copy dependency files
COPY requirements.txt pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py ./

# Run the server
CMD ["python", "server.py"]
