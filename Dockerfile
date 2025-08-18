FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    bash build-essential cmake git libssl-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY scripts/build_liboqs.sh scripts/build_liboqs.sh
RUN chmod +x scripts/build_liboqs.sh && bash scripts/build_liboqs.sh

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml pyproject.toml
COPY src/ src/
RUN pip install -e .

ENTRYPOINT ["pqc-lab"]
CMD ["info"]

