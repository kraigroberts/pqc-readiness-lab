# Simple Dockerfile using official liboqs image - no more over-engineering!
FROM openquantumsafe/liboqs:latest

# Install Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY pyproject.toml .

# Install the package
RUN pip3 install -e .

# Create artifacts directory
RUN mkdir -p artifacts

# Set environment variables
ENV PYTHONPATH=/app/src
ENV LD_LIBRARY_PATH=/usr/local/lib

# Default command
ENTRYPOINT ["pqc-lab"]
CMD ["--help"]
