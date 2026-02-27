import os
from pathlib import Path

def get_source_path():
    # Get source directory from environment variable or use neutral default
    source_dir = Path(os.getenv('XLSX_SOURCE_DIR', str(Path.cwd() / "data"))).resolve()
    xlsx_filename = os.getenv('XLSX_FILENAME', 'GRI_2017_2020.xlsx')
    if os.sep in xlsx_filename or (os.altsep and os.altsep in xlsx_filename) or any(
        part == '..' for part in Path(xlsx_filename).parts
    ):
        raise ValueError(f"Invalid XLSX_FILENAME value: {xlsx_filename!r}")
    xlsx_source_path = source_dir / xlsx_filename
    if not xlsx_source_path.is_file():
        raise FileNotFoundError(f"Excel file not found: {xlsx_source_path.resolve()}")    
    return xlsx_source_path

def get_output_directory():
    output_dir = Path(os.getenv('PDF_OUTPUT_DIR', str(Path.cwd() / 'pdf_output')))
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise RuntimeError(
            f"Failed to create output directory. "
            f"PDF_OUTPUT_DIR={os.getenv('PDF_OUTPUT_DIR', 'not set (using default)')} "
            f"path={output_dir} "
            f"error={type(e).__name__}: {e}"
        ) from e
    return output_dir