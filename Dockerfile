# Multi-stage build for PQC Readiness Lab
# Stage 1: Build liboqs
FROM ubuntu:22.04 AS liboqs-builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    ninja-build \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Clone and build liboqs
WORKDIR /tmp
RUN git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs.git
WORKDIR /tmp/liboqs

# Build liboqs with optimizations
RUN mkdir build && cd build \
    && cmake -GNinja -DCMAKE_BUILD_TYPE=Release -DOQS_USE_OPENSSL=ON .. \
    && ninja install

# Stage 2: Python runtime
FROM python:3.10-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libssl3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy liboqs from builder stage
COPY --from=liboqs-builder /usr/local/lib/liboqs.so* /usr/local/lib/
COPY --from=liboqs-builder /usr/local/include/oqs /usr/local/include/oqs

# Update library path
RUN ldconfig

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY pyproject.toml .

# Install the package
RUN pip install -e .

# Create artifacts directory
RUN mkdir -p artifacts

# Set environment variables
ENV PYTHONPATH=/app/src
ENV LD_LIBRARY_PATH=/usr/local/lib

# Default command
ENTRYPOINT ["pqc-lab"]
CMD ["--help"]
