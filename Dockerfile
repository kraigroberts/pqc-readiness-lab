# Simple Dockerfile - no over-engineering
FROM python:3.10-slim

# Install liboqs
RUN apt-get update && apt-get install -y \
    build-essential cmake git libssl-dev \
    && git clone https://github.com/open-quantum-safe/liboqs.git \
    && cd liboqs && mkdir build && cd build \
    && cmake .. && make -j$(nproc) && make install \
    && ldconfig \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source and install
COPY src/ ./src/
COPY pyproject.toml .
RUN pip install -e .

# Default command
ENTRYPOINT ["pqc-lab"]
CMD ["--help"]
