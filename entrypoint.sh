#!/bin/bash
set -e

echo "[1/4] Running Downloader..."
python Downloader.py

echo "[2/4] Running FileDirectories..."
python FileDirectories.py

echo "[3/4] Running metadata_storage..."
python metadata_storage.py

echo "[4/4] Running hive_pdf_storage..."
python hive_pdf_storage.py

echo "All scripts completed successfully!"
