# PDF Downloader and Hive Storage

A comprehensive PDF download and storage system that retrieves PDFs from URLs specified in Excel files, manages file directories, stores metadata, and persists files in Apache Hive for distributed processing and analysis.

## Description

This project automates the workflow of downloading PDF files from URLs contained in Excel spreadsheets, organizing them into a managed directory structure, extracting and storing metadata, and persisting the files to Apache Hive for scalable data processing. It is designed for batch processing of large document collections with proper error handling and logging.

### Key Features

- **Batch PDF Downloads**: Download multiple PDFs from URLs in Excel files with built-in error handling
- **Fallback URL Support**: Attempt downloads from alternative URLs if primary URL fails
- **Metadata Management**: Extract and store metadata alongside PDF files
- **Hive Integration**: Write PDFs to Apache Hive database for distributed storage and analysis
- **Directory Management**: Automatic organization of downloaded files and outputs
- **Docker Support**: Full containerization with Hive server orchestration
- **Progress Tracking**: Monitor download progress and completion status

## Getting Started

### Dependencies

- Python 3.11+
- Apache Hive (via Docker or local installation)
- pandas==2.0.3 - Data manipulation
- openpyxl==3.1.5 - Excel file reading
- pypdf==6.7.3 - PDF processing
- requests==2.32.5 - HTTP requests for file downloads
- pyhive==0.6.5 - Hive database connectivity
- thrift==0.16.0 and thrift-sasl==0.4.3 - Hive communication

### Installation

#### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/Samirez/PDF_Downloader.git
cd PDF_Downloader
```

2. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Prepare your Excel input file with the following columns:

**Required Columns:**
  - `BRnum` (required) - string, identifier for tracking the PDF record through the pipeline.
  - `Pdf_URL` (required) - string, URL for the primary PDF download source. 
    - **Validation behavior**: No pre-validation is performed. The app only checks if the URL is non-empty at startup. Reachability and format are validated at runtime when attempting to download. 
    - **On failure**: If the URL is malformed or unreachable, the download attempt will fail with an HTTP error (e.g., `Connection error`, `404 Not Found`, `timeout`), which is caught and logged to console as `"Error downloading {BRnum}: {error_message}"`. The app then attempts the fallback URL.
    - **Length recommendation**: max 2048 characters (advisory; not enforced by the app).
    - **Example error**: If `Pdf_URL` is `https://invalid.host/doc.pdf`, the console will show: `Error downloading BRnum_123: Connection refused: ('invalid.host', 443)`
  
  - `Report Html Address` (required) - string, fallback URL used if the primary `Pdf_URL` download fails.
    - **Validation behavior**: Same as `Pdf_URL` — no pre-validation; reachability checked at runtime. 
    - **On failure**: If both `Pdf_URL` and `Report Html Address` fail or are empty, the download is skipped and logged as `"Error downloading {BRnum}: No valid URLs available for download"`.
    - **Length recommendation**: max 2048 characters (advisory; not enforced by the app).
    - **Example fallback flow**: If `Pdf_URL` times out, the app logs `"Error downloading BRnum_456: Connection timeout"`, then tries the `Report Html Address`. If that succeeds, the PDF is downloaded successfully. If both fail, the error is logged and the pipeline continues to the next row.

**Optional Metadata Columns:**
  - `title` (optional) - string, max length 255 characters. Not processed or validated by the application; preserved in source Excel file for reference.
  - `author` (optional) - string, max length 255 characters. Not processed or validated by the application; preserved in source Excel file for reference.
  - `date` (optional) - string, format `YYYY-MM-DD` (recommended format). 
    - **Validation behavior**: No format validation is performed by the application. The field is stored as-is in the source Excel file and not processed by the pipeline.
    - **If format is invalid or missing**: The date value is preserved unchanged in the source file; invalid formats do NOT cause errors or rejections.
    - **Example**: If a row has `date: "2024/01/15"` (slashes instead of hyphens) or `date: "invalid"`, the pipeline will not reject the row. The date is simply preserved as-is in the Excel file and ignored during processing.
    - **Note**: Optional metadata columns are preserved in the source Excel file but are NOT transferred to output files or used by the metadata_storage or hive_pdf_storage components.

**Constraints:**
  - **Column headers must match exactly** (case-sensitive). The application validates the required headers and will fail with a `ValueError: Missing required columns` error if any are missing or misspelled.
    - ✓ **Correct**: `BRnum`, `Pdf_URL`, `Report Html Address`
    - ✗ **Incorrect**: `brnum`, `PDF_URL`, `Report html address` (lowercase letters, missing underscores/spaces)
    - **Troubleshooting tip**: Check capitalization, underscores, spacing, and special characters exactly as shown above. Even `pdf_url` instead of `Pdf_URL` will cause the application to fail.
  - Data must be located in the first worksheet of the Excel file.
  - All rows in the file will be processed (use filtering in Excel if selective processing is needed).

#### Docker Setup

1. Build and start the services:
```bash
docker-compose up --build
```

Excel input files must be available inside the container at `/app/hive/data`. By default the app reads the file named `GRI_2017_2020.xlsx` from that directory. You can override the directory and filename with `XLSX_SOURCE_DIR` and `XLSX_FILENAME` environment variables.

Example docker-compose volume mapping:
```yaml
services:
  pyhive-client:
    volumes:
      - ./data/excel:/app/hive/data
    environment:
      XLSX_SOURCE_DIR: /app/hive/data
      XLSX_FILENAME: GRI_2017_2020.xlsx
```

Docker run alternative:
```bash
docker run --rm \
  -v ./data/excel:/app/hive/data \
  -e XLSX_SOURCE_DIR=/app/hive/data \
  -e XLSX_FILENAME=GRI_2017_2020.xlsx \
  your-image-name
```


This will:
- Start Apache Hive server on port 10000
- Build and run the PDF Downloader application
- Automatically execute the complete pipeline

## Executing the Program

### Local Execution

Run the complete pipeline:
```bash
python Downloader.py
python FileDirectories.py
python metadata_storage.py
python hive_pdf_storage.py
```

Run them in this order. Each step depends on the outputs of the previous one (downloads -> organized files -> metadata -> Hive). The `entrypoint.sh` script already orchestrates the correct sequence for you.

Or use the entrypoint script:
```bash
bash entrypoint.sh
```

### Docker Execution

```bash
docker-compose up
```

### Configuration

Set environment variables or use command-line arguments:

```bash
# Environment variables
export HIVE_HOST=localhost
export HIVE_PORT=10000
export HIVE_USER=default
export HIVE_DATABASE=default
export HIVE_AUTH_MECHANISM=NONE
```

Or pass them to docker-compose:
```yaml
environment:
  HIVE_HOST: hive-server
  HIVE_PORT: 10000
```

## Project Structure

```
PDF_Downloader/
├── Downloader.py              # Main PDF download class
├── FileDirectories.py         # File and directory management
├── metadata_storage.py        # Metadata extraction and storage
├── hive_pdf_storage.py        # Hive database integration
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Hive + App orchestration
├── entrypoint.sh              # Pipeline execution script
├── requirements.txt           # Python dependencies
├── data/                      # Input Excel files directory
│   ├── GRI_2017_2020.xlsx
│   └── Metadata2006_2016.xlsx
└── pdf_output/               # Output directory (created at runtime)
```

## How It Works

1. **Downloader**: Reads the Excel input (via `XLSX_SOURCE_DIR` and `XLSX_FILENAME`) and iterates rows, downloading PDFs from `Pdf_URL` with a fallback to `Report Html Address` when the primary URL fails. It cleans up partial files on errors, skips already-downloaded files, and prints per-row errors before continuing to the next record. Configuration points: Excel file path/filename and `PDF_OUTPUT_DIR` for output files.
2. **FileDirectories**: Scans the output folder and organizes PDFs into the expected directory hierarchy. It creates the output directory if needed and relies on `PDF_OUTPUT_DIR` to know where files live. This step is the handoff point for downstream steps to find the organized PDFs.
3. **metadata_storage**: Reopens the same Excel file, maps each `BRnum` to its PDF status, and uses `pypdf` to detect corrupted/empty files. It logs status counts, writes `metadata_with_filenames.xlsx`, and surfaces errors via logging so the pipeline can continue. Configuration points: Excel file path/filename and output directory from `PDF_OUTPUT_DIR`.
4. **hive_pdf_storage**: Reads PDFs from the output directory, base64-encodes them, and inserts them into the Hive table `pdf_storage` as `(filename, pdf_binary)`. It connects using `HIVE_HOST`, `HIVE_PORT`, `HIVE_USER`, `HIVE_DATABASE`, and `HIVE_AUTH_MECHANISM`; the Hive table must exist before ingestion.

End-to-end example: place `GRI_2017_2020.xlsx` in the input directory, run the pipeline, PDFs are downloaded to `pdf_output`, metadata is written to `metadata_with_filenames.xlsx`, and encoded PDFs are inserted into Hive. External dependencies include Excel files (`.xlsx` with required headers), a writable output directory, and a reachable Hive server.

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

## Authors

- Ahmadullah Naibi

## Acknowledgments

- [Viren070/PDF-Downloader](https://github.com/Viren070/PDF-Downloader) - Download pattern and error handling
- [Apache Hive](https://hive.apache.org/) - Distributed storage solution
- [InMobi/docker-hive](https://github.com/InMobi/docker-hive) - Docker Hive setup
- [ortolanph](https://stackoverflow.com/questions/21755456/) - PDF HDFS storage concepts
- [PlantUML](https://plantuml.com/) - Sequence diagram generation
- [CodeRabbit](https://www.coderabbit.ai/) AI code review for suggestions when committing to repository
- [PythonUnittest](https://www.browserstack.com/guide/unit-testing-python)

### Code Attribution

Portions of this project's download functionality were derived from [Viren070/PDF-Downloader](https://github.com/Viren070/PDF-Downloader):
- `FileDownloadError` exception class (modified: simplified error message)
- `AbortDownload` exception class
- Download pattern using `requests.get()` with streaming and `iter_content()`
- Progress tracking with `downloaded_size` and `total_size`

**Original License**: GPL-3.0 (same as this project)
