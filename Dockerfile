FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsasl2-dev \
    libsasl2-modules \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
RUN mkdir -p /app/hive

# Copy requirements and install Python dependencies
COPY requirements.txt /app/hive/
RUN pip install --no-cache-dir -r /app/hive/requirements.txt

# Copy all necessary Python files
COPY Downloader.py /app/hive
COPY FileDirectories.py /app/hive
COPY metadata_storage.py /app/hive
COPY hive_pdf_storage.py /app/hive

# Copy Excel data files
COPY data/*.xlsx /app/hive/data/

# Copy entrypoint script
COPY --chmod=755 entrypoint.sh /app/hive/

# Create non-root user and set permissions
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app/hive

WORKDIR /app/hive
USER appuser

ENTRYPOINT ["./entrypoint.sh"]   